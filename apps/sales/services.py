from decimal import Decimal
from django.db import transaction
from apps.inventory.models import Product
from apps.sales.models import Sale, SaleItem


# ─── Clave con la que el carrito vive en la sesión ───────────────────────────
CART_SESSION_KEY = "cart"


class CartService:
    """
    Maneja el carrito temporal en la sesión de Django.
    El carrito NO toca la base de datos hasta que se confirma la venta.

    Estructura del carrito en sesión:
    {
        "cart": {
            "items": {
                "42": {                        ← ID del producto como string
                    "product_id": 42,
                    "name": "Coca-Cola 350ml",
                    "sku": "7802800891016",
                    "quantity": 2,
                    "unit_price": "1200.00",
                    "purchase_price": "700.00",
                }
            }
        }
    }
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            # Si no existe carrito en sesión, crea uno vacío
            cart = self.session[CART_SESSION_KEY] = {"items": {}}
        self.cart = cart

    def _save(self):
        """Marca la sesión como modificada para que Django la guarde."""
        self.session.modified = True

    # ─── Agregar producto ─────────────────────────────────────────────────────

    def add(self, product: Product, quantity: int = 1) -> dict:
        """
        Agrega un producto al carrito o incrementa su cantidad.
        Retorna el estado actual del carrito.
        """
        product_id = str(product.id)  # Las keys del dict deben ser strings

        if product_id in self.cart["items"]:
            # El producto ya está en el carrito, solo suma la cantidad
            self.cart["items"][product_id]["quantity"] += quantity
        else:
            # Producto nuevo en el carrito
            self.cart["items"][product_id] = {
                "product_id": product.id,
                "name": product.name,
                "sku": product.sku,
                "quantity": quantity,
                "unit_price": str(product.sale_price),
                "purchase_price": str(product.purchase_price),
            }

        self._save()
        return self.cart

    # ─── Quitar producto ──────────────────────────────────────────────────────

    def remove(self, product_id: int) -> dict:
        """Elimina un producto del carrito completamente."""
        key = str(product_id)
        if key in self.cart["items"]:
            del self.cart["items"][key]
            self._save()
        return self.cart

    # ─── Cambiar cantidad ─────────────────────────────────────────────────────

    def update_quantity(self, product_id: int, quantity: int) -> dict:
        """
        Actualiza la cantidad de un producto.
        Si la cantidad es 0 o menos, elimina el producto.
        """
        key = str(product_id)
        if key in self.cart["items"]:
            if quantity <= 0:
                return self.remove(product_id)
            self.cart["items"][key]["quantity"] = quantity
            self._save()
        return self.cart

    # ─── Vaciar carrito ───────────────────────────────────────────────────────

    def clear(self):
        """Vacía el carrito completamente."""
        self.session[CART_SESSION_KEY] = {"items": {}}
        self.session.modified = True
        self.cart = self.session[CART_SESSION_KEY]

    # ─── Obtener items ────────────────────────────────────────────────────────

    def get_items(self) -> list:
        """
        Retorna la lista de items del carrito con los valores
        convertidos a Decimal para cálculos seguros.
        """
        items = []
        for item in self.cart["items"].values():
            unit_price = Decimal(item["unit_price"])
            quantity = item["quantity"]
            items.append({
                **item,
                "unit_price": unit_price,
                "purchase_price": Decimal(item["purchase_price"]),
                "subtotal": unit_price * quantity,
            })
        return items

    # ─── Calcular total ───────────────────────────────────────────────────────

    def get_total(self) -> Decimal:
        """Retorna el total del carrito."""
        return sum(
            Decimal(item["unit_price"]) * item["quantity"]
            for item in self.cart["items"].values()
        )

    # ─── Cantidad de items ────────────────────────────────────────────────────

    def get_item_count(self) -> int:
        """Retorna el número total de productos (sumando cantidades)."""
        return sum(
            item["quantity"]
            for item in self.cart["items"].values()
        )

    # ─── Verificar si está vacío ──────────────────────────────────────────────

    def is_empty(self) -> bool:
        return len(self.cart["items"]) == 0

    # ─── Calcular vuelto ──────────────────────────────────────────────────────

    @staticmethod
    def calculate_change(total: Decimal, amount_tendered: Decimal) -> Decimal:
        """Calcula el vuelto para pagos en efectivo."""
        return amount_tendered - total


class SaleService:
    """
    Maneja la creación de ventas en la base de datos.
    Toda la lógica crítica vive aquí, no en las vistas.
    """

    @staticmethod
    @transaction.atomic
    def create_sale(
        cart_service: CartService,
        payment_method: str,
        amount_tendered: Decimal = None,
        seller=None,
    ) -> Sale:
        """
        Crea la venta en la base de datos de forma atómica:
        1. Verifica stock de todos los productos
        2. Crea el registro Sale
        3. Crea los SaleItems con precios históricos
        4. Descuenta el stock de cada producto
        5. Limpia el carrito

        Si cualquier paso falla, se hace ROLLBACK completo.
        Nadie queda con stock descontado sin venta registrada.
        """
        items = cart_service.get_items()

        if not items:
            raise ValueError("No se puede crear una venta con el carrito vacío.")

        # ── Paso 1: Verificar stock ANTES de tocar nada ───────────────────────
        for item in items:
            product = Product.objects.select_for_update().get(
                id=item["product_id"]
            )
            # select_for_update() bloquea la fila en PostgreSQL
            # evita que dos cajeros vendan el último producto al mismo tiempo
            if product.stock < item["quantity"]:
                raise ValueError(
                    f"Stock insuficiente para '{product.name}'. "
                    f"Disponible: {product.stock}, Solicitado: {item['quantity']}"
                )

        # ── Paso 2: Crear la cabecera de la venta ─────────────────────────────
        sale = Sale.objects.create(
            seller=seller,
            payment_method=payment_method,
            total_amount=cart_service.get_total(),
            amount_tendered=amount_tendered,
            status=Sale.SaleStatus.COMPLETED,
        )

        # ── Paso 3 y 4: Crear items y descontar stock ─────────────────────────
        for item in items:
            product = Product.objects.select_for_update().get(
                id=item["product_id"]
            )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                purchase_price_snapshot=item["purchase_price"],
            )

            # Descuento de stock seguro
            product.stock -= item["quantity"]
            product.save(update_fields=["stock"])  # Solo actualiza el campo stock

        # ── Paso 5: Limpiar el carrito ────────────────────────────────────────
        cart_service.clear()

        return sale
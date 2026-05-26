from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation

from apps.inventory.models import Product
from apps.sales.services import CartService, SaleService


def _render_cart(request):
    """
    Helper interno: renderiza el partial del carrito.
    Lo usamos en todas las vistas que modifican el carrito.
    """
    cart_service = CartService(request)
    return render(request, "sales/partials/cart.html", {
        "cart_items": cart_service.get_items(),
        "cart_total": cart_service.get_total(),
        "item_count": cart_service.get_item_count(),
    })


def pos_view(request):
    """Vista principal de la pantalla de caja."""
    cart_service = CartService(request)
    return render(request, "sales/pos.html", {
        "cart_items": cart_service.get_items(),
        "cart_total": cart_service.get_total(),
        "item_count": cart_service.get_item_count(),
    })


@require_POST
def add_to_cart(request):
    """
    Recibe el SKU escaneado, busca el producto y lo agrega al carrito.
    Responde con el HTML del carrito actualizado (para HTMX).
    """
    sku = request.POST.get("sku", "").strip()

    if not sku:
        return _render_cart(request)

    try:
        product = Product.objects.get(sku=sku, is_active=True)
    except Product.DoesNotExist:
        # Producto no encontrado: devuelve carrito con mensaje de error
        cart_service = CartService(request)
        return render(request, "sales/partials/cart.html", {
            "cart_items": cart_service.get_items(),
            "cart_total": cart_service.get_total(),
            "item_count": cart_service.get_item_count(),
            "error_message": f"Producto con SKU '{sku}' no encontrado.",
        })

    if not product.is_in_stock:
        cart_service = CartService(request)
        return render(request, "sales/partials/cart.html", {
            "cart_items": cart_service.get_items(),
            "cart_total": cart_service.get_total(),
            "item_count": cart_service.get_item_count(),
            "error_message": f"'{product.name}' no tiene stock disponible.",
        })

    cart_service = CartService(request)
    cart_service.add(product)
    return _render_cart(request)


@require_POST
def update_cart(request):
    """Actualiza la cantidad de un producto en el carrito."""
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    cart_service = CartService(request)
    cart_service.update_quantity(int(product_id), quantity)
    return _render_cart(request)


@require_POST
def remove_from_cart(request):
    """Elimina un producto del carrito."""
    product_id = request.POST.get("product_id")
    cart_service = CartService(request)
    cart_service.remove(int(product_id))
    return _render_cart(request)


@require_POST
def clear_cart(request):
    """Vacía el carrito completo."""
    cart_service = CartService(request)
    cart_service.clear()
    return _render_cart(request)


@require_GET
def payment_modal(request):
    """Devuelve el HTML del modal de pago para HTMX."""
    payment_method = request.GET.get("method", "CASH")
    cart_service = CartService(request)
    return render(request, "sales/partials/payment_modal.html", {
        "payment_method": payment_method,
        "cart_total": cart_service.get_total(),
    })


@require_POST
def confirm_sale(request):
    """
    Confirma y procesa la venta completa.
    Llama a SaleService que maneja todo dentro de transaction.atomic().
    """
    payment_method = request.POST.get("payment_method")
    amount_tendered = None

    if payment_method == "CASH":
        try:
            amount_tendered = Decimal(request.POST.get("amount_tendered", "0"))
        except InvalidOperation:
            messages.error(request, "Monto inválido.")
            return redirect("sales:pos")

    cart_service = CartService(request)

    if cart_service.is_empty():
        messages.error(request, "El carrito está vacío.")
        return redirect("sales:pos")

    try:
        sale = SaleService.create_sale(
            cart_service=cart_service,
            payment_method=payment_method,
            amount_tendered=amount_tendered,
            seller=request.user,
        )
        messages.success(
            request,
            f"✅ Venta #{sale.id} registrada por ${sale.total_amount:,.0f}"
        )
        return redirect("sales:ticket", pk=sale.id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect("sales:pos")


def ticket_view(request, pk):
    """Muestra el ticket interno después de confirmar la venta."""
    from apps.sales.models import Sale
    try:
        sale = Sale.objects.prefetch_related("items__product").get(pk=pk)
    except Sale.DoesNotExist:
        messages.error(request, "Venta no encontrada.")
        return redirect("sales:pos")

    return render(request, "sales/ticket.html", {"sale": sale})
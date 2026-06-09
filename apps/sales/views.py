from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

from apps.inventory.models import Product
from apps.sales.services import CartService, SaleService

from functools import wraps


def htmx_login_required(view_func):
    """
    Decorador que maneja login_required para requests HTMX.
    En vez de redirigir dentro del swap, fuerza recarga completa al login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('HX-Request'):
                # Es un request HTMX → respuesta especial
                response = HttpResponse()
                response['HX-Redirect'] = '/login/'
                return response
            else:
                from django.shortcuts import redirect
                return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

def _render_cart(request, error_message=None):
    cart_service = CartService(request)
    return render(request, "sales/partials/cart.html", {
        "cart_items": cart_service.get_items(),
        "cart_total": cart_service.get_total(),
        "item_count": cart_service.get_item_count(),
        "error_message": error_message,  # ← Siempre presente
    })  

def pos_view(request):
    """Vista principal de la pantalla de caja."""
    cart_service = CartService(request)
    return render(request, "sales/pos.html", {
        "cart_items": cart_service.get_items(),
        "cart_total": cart_service.get_total(),
        "item_count": cart_service.get_item_count(),
    })


@htmx_login_required
@require_POST
def add_to_cart(request):
    sku = request.POST.get("sku", "").strip()

    if not sku:
        return _render_cart(request)

    try:
        product = Product.objects.get(sku=sku, is_active=True)
    except Product.DoesNotExist:
        return _render_cart(request, f"❌ SKU '{sku}' no encontrado.")

    if not product.is_in_stock:
        return _render_cart(request, f"⚠ '{product.name}' sin stock.")

    cart_service = CartService(request)
    cart_service.add(product)
    return _render_cart(request)

@htmx_login_required
@require_POST
def update_cart(request):
    """Actualiza la cantidad de un producto en el carrito."""
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    cart_service = CartService(request)
    cart_service.update_quantity(int(product_id), quantity)
    return _render_cart(request)

@htmx_login_required
@require_POST
def remove_from_cart(request):
    """Elimina un producto del carrito."""
    product_id = request.POST.get("product_id")
    cart_service = CartService(request)
    cart_service.remove(int(product_id))
    return _render_cart(request)

@htmx_login_required
@require_POST
def clear_cart(request):
    """Vacía el carrito completo."""
    cart_service = CartService(request)
    cart_service.clear()
    return _render_cart(request)

@htmx_login_required
@require_GET
def payment_modal(request):
    """Devuelve el HTML del modal de pago para HTMX."""
    payment_method = request.GET.get("method", "CASH")
    cart_service = CartService(request)
    return render(request, "sales/partials/payment_modal.html", {
        "payment_method": payment_method,
        "cart_total": cart_service.get_total(),
    })


@htmx_login_required
@require_POST
def confirm_sale(request):
    from django.http import HttpResponse

    payment_method = request.POST.get("payment_method")
    amount_tendered = None

    if payment_method == "CASH":
        try:
            amount_tendered = Decimal(request.POST.get("amount_tendered", "0"))
        except InvalidOperation:
            response = HttpResponse()
            response["HX-Redirect"] = "/ventas/caja/"
            return response

        cart_service = CartService(request)
        total = cart_service.get_total()

        if amount_tendered < total:
            # ─── Devuelve el modal con el error, sin cerrar ni redirigir ──
            return render(request, "sales/partials/payment_modal.html", {
                "payment_method": payment_method,
                "cart_total": total,
                "error_pago": f"⚠ El monto (${amount_tendered:,.0f}) es menor al total (${total:,.0f}).",
            })

    cart_service = CartService(request)

    if cart_service.is_empty():
        response = HttpResponse()
        response["HX-Redirect"] = "/ventas/caja/"
        return response

    try:
        sale = SaleService.create_sale(
            cart_service=cart_service,
            payment_method=payment_method,
            amount_tendered=amount_tendered,
            seller=request.user,
        )
        response = HttpResponse()
        response["HX-Redirect"] = f"/ventas/caja/ticket/{sale.id}/"
        return response

    except ValueError as e:
        cart_service_new = CartService(request)
        return render(request, "sales/partials/payment_modal.html", {
            "payment_method": payment_method,
            "cart_total": cart_service_new.get_total(),
            "error_pago": str(e),
        })
@htmx_login_required
def ticket_view(request, pk):
    """Muestra el ticket interno después de confirmar la venta."""
    from apps.sales.models import Sale
    try:
        sale = Sale.objects.prefetch_related("items__product").get(pk=pk)
    except Sale.DoesNotExist:
        messages.error(request, "Venta no encontrada.")
        return redirect("sales:pos")

    return render(request, "sales/ticket.html", {"sale": sale})
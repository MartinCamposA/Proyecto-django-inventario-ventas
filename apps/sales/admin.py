from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    """
    Muestra los productos de una venta directamente
    dentro del detalle de la venta. Solo lectura.
    """
    model = SaleItem
    extra = 0
    readonly_fields = [
        "product",
        "quantity",
        "unit_price",
        "purchase_price_snapshot",
        "subtotal",
        "profit",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # No permitir agregar items desde el admin


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "created_at",
        "seller",
        "payment_method",
        "total_amount",
        "status",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["id", "seller__username"]
    readonly_fields = [
        "seller",
        "total_amount",
        "amount_tendered",
        "payment_method",
        "created_at",
        "change_due",
        "total_profit",
    ]
    inlines = [SaleItemInline]

    def has_add_permission(self, request):
        return False  # Las ventas solo se crean desde el POS, no desde el admin

    def has_delete_permission(self, request, obj=None):
        return False  # Las ventas no se eliminan, se anulan
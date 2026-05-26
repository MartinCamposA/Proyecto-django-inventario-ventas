from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}  # Auto-genera el slug desde el nombre


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "category",
        "purchase_price",
        "sale_price",
        "stock",
        "stock_status",
        "is_active",
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "sku"]
    list_editable = ["stock", "sale_price", "is_active"]  # Editar directo desde la lista
    readonly_fields = ["created_at", "updated_at", "margin"]

    fieldsets = (
        ("Información General", {
            "fields": ("category", "name", "sku", "is_active")
        }),
        ("Precios", {
            "fields": ("purchase_price", "sale_price", "margin")
        }),
        ("Inventario", {
            "fields": ("stock",)
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)  # Sección colapsable
        }),
    )

    @admin.display(description="Stock")
    def stock_status(self, obj):
        """Muestra el stock con color según la cantidad."""
        if obj.stock == 0:
            color = "red"
            texto = "⚠ Sin stock"
        elif obj.stock <= 5:
            color = "orange"
            texto = f"⚡ {obj.stock} unidades"
        else:
            color = "green"
            texto = f"✓ {obj.stock} unidades"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            texto
        )
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.inventory.models import Product

User = get_user_model()


class Sale(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Efectivo"
        CARD = "CARD", "Tarjeta"

    class SaleStatus(models.TextChoices):
        COMPLETED = "COMPLETED", "Completada"
        CANCELLED = "CANCELLED", "Anulada"

    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
        verbose_name="Vendedor",
    )
    status = models.CharField(
        max_length=20,
        choices=SaleStatus.choices,
        default=SaleStatus.COMPLETED,
        verbose_name="Estado",
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        verbose_name="Método de Pago",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Total de la Venta",
    )
    amount_tendered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monto Entregado (Efectivo)",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Venta #{self.pk} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    @property
    def change_due(self) -> Decimal | None:
        if self.payment_method == self.PaymentMethod.CASH and self.amount_tendered:
            return self.amount_tendered - self.total_amount
        return None

    @property
    def total_profit(self) -> Decimal:
        return sum(item.profit for item in self.items.all())


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Venta",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sale_items",
        verbose_name="Producto",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de Venta (al momento de vender)",
    )
    purchase_price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de Compra (al momento de vender)",
    )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.quantity}x {self.product.name} en Venta #{self.sale_id}"

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

    @property
    def profit(self) -> Decimal:
        return (self.unit_price - self.purchase_price_snapshot) * self.quantity
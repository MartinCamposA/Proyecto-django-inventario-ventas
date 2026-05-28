from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, F
from decimal import Decimal

from apps.sales.models import Sale, SaleItem


@login_required
def dashboard(request):
    """
    Dashboard principal con resumen del día.
    """
    hoy = timezone.localdate()

    # Ventas de hoy
    ventas_hoy = Sale.objects.filter(
        created_at__date=hoy,
        status=Sale.SaleStatus.COMPLETED,
    )

    # Totales del día
    total_ventas_hoy = ventas_hoy.aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    cantidad_ventas_hoy = ventas_hoy.count()

    # Ganancia del día usando precios históricos
    ganancia_hoy = SaleItem.objects.filter(
        sale__created_at__date=hoy,
        sale__status=Sale.SaleStatus.COMPLETED,
    ).aggregate(
        ganancia=Sum(
            (F("unit_price") - F("purchase_price_snapshot")) * F("quantity")
        )
    )["ganancia"] or Decimal("0")

    # Ventas por método de pago hoy
    efectivo_hoy = ventas_hoy.filter(
        payment_method=Sale.PaymentMethod.CASH
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")

    tarjeta_hoy = ventas_hoy.filter(
        payment_method=Sale.PaymentMethod.CARD
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")

    # Últimas 10 ventas
    ultimas_ventas = Sale.objects.select_related("seller").prefetch_related(
        "items"
    ).order_by("-created_at")[:10]

    # Producto más vendido hoy
    producto_top = SaleItem.objects.filter(
        sale__created_at__date=hoy,
        sale__status=Sale.SaleStatus.COMPLETED,
    ).values(
        "product__name"
    ).annotate(
        total_vendido=Sum("quantity")
    ).order_by("-total_vendido").first()

    return render(request, "reporting/dashboard.html", {
        "hoy": hoy,
        "total_ventas_hoy": total_ventas_hoy,
        "cantidad_ventas_hoy": cantidad_ventas_hoy,
        "ganancia_hoy": ganancia_hoy,
        "efectivo_hoy": efectivo_hoy,
        "tarjeta_hoy": tarjeta_hoy,
        "ultimas_ventas": ultimas_ventas,
        "producto_top": producto_top,
    })


@login_required
def historial(request):
    """
    Historial completo de ventas con filtro por fecha.
    """
    fecha_desde = request.GET.get("desde", "")
    fecha_hasta = request.GET.get("hasta", "")

    ventas = Sale.objects.select_related("seller").prefetch_related(
        "items__product"
    ).order_by("-created_at")

    if fecha_desde:
        ventas = ventas.filter(created_at__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(created_at__date__lte=fecha_hasta)

    # Totales del período filtrado
    totales = ventas.aggregate(
        total_ingresos=Sum("total_amount"),
        cantidad=Count("id"),
    )

    ganancia_periodo = SaleItem.objects.filter(
        sale__in=ventas
    ).aggregate(
        ganancia=Sum(
            (F("unit_price") - F("purchase_price_snapshot")) * F("quantity")
        )
    )["ganancia"] or Decimal("0")

    return render(request, "reporting/historial.html", {
        "ventas": ventas,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "total_ingresos": totales["total_ingresos"] or Decimal("0"),
        "cantidad_ventas": totales["cantidad"] or 0,
        "ganancia_periodo": ganancia_periodo,
    })
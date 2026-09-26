from datetime import timedelta

from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from catalogo.models import Inventario
from config.utils import redondear_centavos
from finanzas.models import Deuda
from ventas.models import Venta


def _variacion_pct(actual, anterior):
    if not anterior:
        return 0
    return round(((actual - anterior) / anterior) * 100)


def dashboard(request):
    hoy = timezone.localdate()
    ayer = hoy - timedelta(days=1)

    ventas_hoy_total = redondear_centavos(Venta.objects.filter(fecha__date=hoy).aggregate(total=Sum('total'))['total'])
    ventas_ayer_total = redondear_centavos(Venta.objects.filter(fecha__date=ayer).aggregate(total=Sum('total'))['total'])

    mes_actual_ventas = Venta.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month)
    ventas_mes_total = redondear_centavos(mes_actual_ventas.aggregate(total=Sum('total'))['total'])

    mes_anterior = (hoy.replace(day=1) - timedelta(days=1))
    mes_anterior_ventas = Venta.objects.filter(fecha__year=mes_anterior.year, fecha__month=mes_anterior.month)
    ventas_mes_anterior_total = redondear_centavos(mes_anterior_ventas.aggregate(total=Sum('total'))['total'])

    alertas_stock = Inventario.objects.filter(stock__lte=F('stock_minimo')).select_related(
        'producto', 'talla', 'color', 'seccion'
    )
    productos_stock_critico_count = alertas_stock.filter(stock__lte=1).count()

    deudas_pendientes = Deuda.objects.exclude(estado=Deuda.Estado.PAGADA).prefetch_related('abonos')
    deuda_total_pendiente = sum((d.saldo_pendiente for d in deudas_pendientes), redondear_centavos(0))
    clientes_con_deuda_count = len({d.cliente_id for d in deudas_pendientes if d.saldo_pendiente > 0})

    context = {
        'active_view': 'dashboard',
        'fecha_hoy': hoy,
        'ventas_hoy_total': ventas_hoy_total,
        'ventas_hoy_variacion_pct': _variacion_pct(ventas_hoy_total, ventas_ayer_total),
        'productos_stock_bajo_count': alertas_stock.count(),
        'productos_stock_critico_count': productos_stock_critico_count,
        'deuda_total_pendiente': deuda_total_pendiente,
        'clientes_con_deuda_count': clientes_con_deuda_count,
        'ventas_mes_total': ventas_mes_total,
        'ventas_mes_variacion_pct': _variacion_pct(ventas_mes_total, ventas_mes_anterior_total),
        'ventas_recientes': Venta.objects.select_related('cliente').order_by('-fecha')[:5],
        'alertas_stock': alertas_stock[:8],
    }
    return render(request, 'dashboard.html', context)

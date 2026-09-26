from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from catalogo.models import Inventario

SESSION_KEY = 'carrito'
CENTAVO = Decimal('0.01')


def obtener_carrito(session):
    return session.get(SESSION_KEY, {})


def guardar_carrito(session, carrito):
    session[SESSION_KEY] = carrito
    session.modified = True


def construir_lineas(carrito):
    if not carrito:
        return []

    inventarios = Inventario.objects.select_related('producto', 'talla', 'color').filter(
        pk__in=[int(k) for k in carrito.keys()]
    )
    inventarios_por_id = {inv.pk: inv for inv in inventarios}

    lineas = []
    for inventario_id, cantidad in carrito.items():
        inv = inventarios_por_id.get(int(inventario_id))
        if not inv:
            continue
        precio_unitario = inv.producto.precio_producto
        lineas.append({
            'inventario': inv,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': precio_unitario * cantidad,
        })
    return lineas


def iva_de_linea(linea):
    if not linea['inventario'].producto.iva_aplica:
        return Decimal('0.00')
    iva_pct = Decimal(str(settings.IVA_PORCENTAJE))
    return (linea['subtotal'] * iva_pct / Decimal('100')).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def calcular_totales(lineas):
    subtotal = sum((l['subtotal'] for l in lineas), Decimal('0.00'))
    iva = sum((iva_de_linea(l) for l in lineas), Decimal('0.00'))
    return subtotal, iva, subtotal + iva

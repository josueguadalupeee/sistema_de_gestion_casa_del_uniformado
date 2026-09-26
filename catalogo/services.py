from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F

from .models import Inventario


def enviar_alerta_stock():
    """Envia el correo de stock bajo si corresponde.

    Devuelve una tupla (enviado: bool, detalle: str) para que tanto el
    management command como el endpoint HTTP puedan reportar el resultado.
    """
    alertas = Inventario.objects.filter(stock__lte=F('stock_minimo')).select_related(
        'producto', 'talla', 'color', 'seccion'
    ).order_by('producto__nombre_producto')

    if not alertas.exists():
        return False, 'Sin productos en stock minimo. No se envia correo.'

    destinatarios = settings.STOCK_ALERT_RECIPIENTS
    if not destinatarios:
        return False, 'STOCK_ALERT_RECIPIENTS no esta configurado; no hay a quien enviar el reporte.'

    from configuracion.models import CasaUniformado
    nombre_negocio = CasaUniformado.get_solo().nombre or 'Sistema de inventario'

    lineas = [
        f'- {item.producto.nombre_producto} ({item.producto.codigo}) '
        f'talla {item.talla.descripcion}, color {item.color.descripcion}, '
        f'seccion {item.seccion.nombre_seccion}: stock {item.stock} / minimo {item.stock_minimo}'
        for item in alertas
    ]
    mensaje = (
        f'Hay {alertas.count()} variante(s) en o por debajo del stock minimo:\n\n'
        + '\n'.join(lineas)
    )

    send_mail(
        subject=f'{nombre_negocio} - Alerta de stock ({alertas.count()} variantes)',
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=destinatarios,
    )
    return True, f'Correo de alerta enviado a {", ".join(destinatarios)} ({alertas.count()} variantes).'

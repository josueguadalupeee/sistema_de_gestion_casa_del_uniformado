from django.db import migrations


def vincular_deudas_existentes(apps, schema_editor):
    """Reconecta deudas creadas antes de que existiera Deuda.venta con la venta
    a crédito que las originó, emparejando por cliente + monto + cercanía en el
    tiempo (se crean en la misma transacción, así que la fecha coincide casi
    exactamente). Deudas registradas manualmente (sin venta) quedan como están.
    """
    Deuda = apps.get_model('finanzas', 'Deuda')
    Venta = apps.get_model('ventas', 'Venta')

    ventas_usadas = set()
    for deuda in Deuda.objects.filter(venta__isnull=True).order_by('fecha_deuda'):
        candidatas = list(
            Venta.objects.filter(
                cliente_id=deuda.cliente_id,
                estado_pago='CREDITO',
                total=deuda.monto_total,
            ).exclude(pk__in=ventas_usadas)
        )
        if not candidatas:
            continue
        venta = min(candidatas, key=lambda v: abs((v.fecha - deuda.fecha_deuda).total_seconds()))
        deuda.venta_id = venta.pk
        deuda.save(update_fields=['venta'])
        ventas_usadas.add(venta.pk)


def revertir(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('finanzas', '0002_deuda_venta'),
        ('ventas', '0002_venta_estado_pago'),
    ]

    operations = [
        migrations.RunPython(vincular_deudas_existentes, revertir),
    ]

from django.db import migrations


def crear_talla_no_aplica(apps, schema_editor):
    Talla = apps.get_model('catalogo', 'Talla')
    Talla.objects.get_or_create(descripcion='N/A')


def eliminar_talla_no_aplica(apps, schema_editor):
    Talla = apps.get_model('catalogo', 'Talla')
    Talla.objects.filter(descripcion='N/A').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_remove_inventario_variante_unica_por_producto_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_talla_no_aplica, eliminar_talla_no_aplica),
    ]

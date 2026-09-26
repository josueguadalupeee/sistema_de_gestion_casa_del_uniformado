from django.core.management.base import BaseCommand

from catalogo.services import enviar_alerta_stock


class Command(BaseCommand):
    help = (
        'Envia un correo con el resumen de variantes en o por debajo del stock minimo. '
        'Si no hay ninguna, no envia nada.'
    )

    def handle(self, *args, **options):
        _, detalle = enviar_alerta_stock()
        self.stdout.write(detalle)

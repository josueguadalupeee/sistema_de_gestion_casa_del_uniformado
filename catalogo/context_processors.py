from django.db.models import F

from .models import Inventario


def alertas_inventario(request):
    count = Inventario.objects.filter(stock__lte=F('stock_minimo')).count()
    return {'productos_stock_bajo_count': count}

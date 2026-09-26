from django.shortcuts import render

from .models import FacturaProveedor


def facturas_proveedor(request):
    facturas = FacturaProveedor.objects.select_related('proveedor').prefetch_related('detalles')
    context = {
        'active_view': 'facturas_proveedor',
        'facturas': facturas,
    }
    return render(request, 'facturas_proveedor.html', context)

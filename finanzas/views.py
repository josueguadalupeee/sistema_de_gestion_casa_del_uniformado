from datetime import timedelta

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.utils import redondear_centavos

from .forms import AbonoDeudaForm, DeudaForm
from .models import AbonoDeuda, Deuda


def deudores(request):
    q = request.GET.get('q', '').strip()

    deudas_qs = (
        Deuda.objects.select_related('cliente').prefetch_related('abonos')
        .exclude(estado=Deuda.Estado.PAGADA)
    )
    if q:
        deudas_qs = deudas_qs.filter(Q(cliente__nombre_cliente__icontains=q) | Q(cliente__cedula__icontains=q))
    deudas = list(deudas_qs)
    deudas.sort(key=lambda d: d.saldo_pendiente, reverse=True)

    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    deudas_vencidas_count = sum(
        1 for d in deudas if d.fecha_deuda <= hace_30_dias and d.saldo_pendiente > 0
    )
    clientes_con_deuda = {d.cliente_id for d in deudas if d.saldo_pendiente > 0}

    abonado_mes_total = redondear_centavos(
        AbonoDeuda.objects.filter(
            fecha_abono__year=hoy.year, fecha_abono__month=hoy.month
        ).aggregate(total=Sum('monto_abono'))['total']
    )

    context = {
        'active_view': 'deudores',
        'deudas': deudas,
        'q': q,
        'saldo_total_pendiente': sum((d.saldo_pendiente for d in deudas), redondear_centavos(0)),
        'deudas_vencidas_count': deudas_vencidas_count,
        'clientes_con_deuda_count': len(clientes_con_deuda),
        'abonado_mes_total': abonado_mes_total,
    }
    return render(request, 'deudores.html', context)


def deuda_nueva(request):
    if request.method == 'POST':
        form = DeudaForm(request.POST)
        if form.is_valid():
            deuda = form.save()
            messages.success(request, f'Deuda registrada para {deuda.cliente}.')
            return redirect('deuda_detalle', pk=deuda.pk)
    else:
        form = DeudaForm()
    return render(request, 'deuda_form.html', {'active_view': 'deudores', 'form': form})


def deuda_detalle(request, pk):
    deuda = get_object_or_404(
        Deuda.objects.select_related('cliente', 'venta').prefetch_related(
            'venta__detalles__inventario__producto',
            'venta__detalles__inventario__talla',
            'venta__detalles__inventario__color',
        ),
        pk=pk,
    )

    if request.method == 'POST':
        abono_form = AbonoDeudaForm(request.POST)
        if abono_form.is_valid():
            abono = abono_form.save(commit=False)
            abono.deuda = deuda
            abono.save()
            if deuda.saldo_pendiente <= 0:
                deuda.estado = Deuda.Estado.PAGADA
            else:
                deuda.estado = Deuda.Estado.ABONADA
            deuda.save(update_fields=['estado'])
            messages.success(request, 'Abono registrado.')
            return redirect('deuda_detalle', pk=deuda.pk)
    else:
        abono_form = AbonoDeudaForm()

    context = {
        'active_view': 'deudores',
        'deuda': deuda,
        'abonos': deuda.abonos.all(),
        'abono_form': abono_form,
    }
    return render(request, 'deuda_detalle.html', context)

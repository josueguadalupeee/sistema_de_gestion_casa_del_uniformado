import json

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from catalogo.models import Inventario

from .carrito import calcular_totales, construir_lineas, guardar_carrito, iva_de_linea, obtener_carrito
from .forms import ClienteForm
from .models import Cliente, DetalleVenta, Venta


def clientes(request):
    q = request.GET.get('q', '').strip()
    clientes_qs = Cliente.objects.all()
    if q:
        clientes_qs = clientes_qs.filter(Q(nombre_cliente__icontains=q) | Q(cedula__icontains=q))
    context = {'active_view': 'clientes', 'clientes': clientes_qs, 'q': q}
    return render(request, 'clientes.html', context)


def cliente_nuevo(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente "{cliente.nombre_cliente}" creado.')
            return redirect('clientes')
    else:
        form = ClienteForm()
    context = {'active_view': 'clientes', 'form': form, 'modo': 'nuevo'}
    return render(request, 'cliente_form.html', context)


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{cliente.nombre_cliente}" actualizado.')
            return redirect('clientes')
    else:
        form = ClienteForm(instance=cliente)
    context = {'active_view': 'clientes', 'form': form, 'modo': 'editar', 'cliente': cliente}
    return render(request, 'cliente_form.html', context)


def _cliente_actual(request):
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        cliente = Cliente.objects.filter(pk=cliente_id).first()
        if cliente:
            return cliente
    return Cliente.objects.filter(nombre_cliente='Consumidor Final').first()


def _render_carrito(request):
    carrito = obtener_carrito(request.session)
    lineas = construir_lineas(carrito)
    subtotal, iva, total = calcular_totales(lineas)
    return render_to_string('_carrito.html', {
        'carrito_lineas': lineas,
        'carrito_subtotal': subtotal,
        'carrito_iva': iva,
        'carrito_total': total,
    }, request=request)


def facturacion(request):
    cliente = _cliente_actual(request)
    lineas = construir_lineas(obtener_carrito(request.session))
    subtotal, iva, total = calcular_totales(lineas)

    context = {
        'active_view': 'facturacion',
        'resultados_busqueda': [],
        'cliente_seleccionado': cliente,
        'carrito_lineas': lineas,
        'carrito_subtotal': subtotal,
        'carrito_iva': iva,
        'carrito_total': total,
        'historial_cliente': Venta.objects.filter(cliente=cliente).order_by('-fecha')[:5] if cliente else [],
        'siguiente_numero_factura': Venta.objects.count() + 1,
    }
    return render(request, 'facturacion.html', context)


def ventas_lista(request):
    q = request.GET.get('q', '').strip()
    fecha = request.GET.get('fecha', '').strip()
    fecha_parseada = parse_date(fecha) if fecha else None

    ventas_qs = Venta.objects.select_related('cliente').order_by('-fecha')
    if q:
        ventas_qs = ventas_qs.filter(Q(cliente__nombre_cliente__icontains=q) | Q(cliente__cedula__icontains=q))
    if fecha_parseada:
        ventas_qs = ventas_qs.filter(fecha__date=fecha_parseada)

    context = {
        'active_view': 'ventas',
        'ventas': ventas_qs,
        'q': q,
        'fecha': fecha,
    }
    return render(request, 'ventas.html', context)


def venta_detalle(request, pk):
    venta = get_object_or_404(Venta.objects.select_related('cliente'), pk=pk)
    detalles = venta.detalles.select_related(
        'inventario__producto', 'inventario__talla', 'inventario__color', 'inventario__seccion'
    )
    context = {'active_view': 'ventas', 'venta': venta, 'detalles': detalles}
    return render(request, 'venta_detalle.html', context)


def buscar_productos(request):
    q = request.GET.get('q', '').strip()
    resultados = []
    if q:
        resultados = Inventario.objects.select_related('producto', 'talla', 'color').filter(
            stock__gt=0
        ).filter(
            Q(producto__nombre_producto__icontains=q) | Q(producto__codigo__icontains=q)
        )[:20]
    html = render_to_string('_resultados_busqueda.html', {'resultados_busqueda': resultados}, request=request)
    return HttpResponse(html)


@require_POST
def carrito_agregar(request):
    try:
        data = json.loads(request.body)
        inventario_id = int(data['inventario_id'])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return HttpResponseBadRequest('inventario_id inválido')

    inventario = Inventario.objects.filter(pk=inventario_id).first()
    if not inventario:
        return HttpResponseBadRequest('Variante no encontrada')

    carrito = obtener_carrito(request.session)
    clave = str(inventario_id)
    cantidad_actual = carrito.get(clave, 0)
    if cantidad_actual < inventario.stock:
        carrito[clave] = cantidad_actual + 1
        guardar_carrito(request.session, carrito)
    return HttpResponse(_render_carrito(request))


@require_POST
def carrito_actualizar(request):
    try:
        data = json.loads(request.body)
        inventario_id = int(data['inventario_id'])
        delta = int(data['delta'])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return HttpResponseBadRequest('datos inválidos')

    inventario = Inventario.objects.filter(pk=inventario_id).first()
    carrito = obtener_carrito(request.session)
    clave = str(inventario_id)
    nueva_cantidad = carrito.get(clave, 0) + delta
    if inventario and nueva_cantidad > inventario.stock:
        nueva_cantidad = inventario.stock
    if nueva_cantidad <= 0:
        carrito.pop(clave, None)
    else:
        carrito[clave] = nueva_cantidad
    guardar_carrito(request.session, carrito)
    return HttpResponse(_render_carrito(request))


@require_POST
def carrito_vaciar(request):
    guardar_carrito(request.session, {})
    return HttpResponse(_render_carrito(request))


def seleccionar_cliente(request):
    form = ClienteForm()
    if request.method == 'POST':
        if 'crear_cliente' in request.POST:
            form = ClienteForm(request.POST)
            if form.is_valid():
                cliente = form.save()
                request.session['cliente_id'] = cliente.pk
                messages.success(request, f'Cliente "{cliente.nombre_cliente}" creado y seleccionado.')
                return redirect('facturacion')
        else:
            cliente_id = request.POST.get('cliente_id')
            if cliente_id:
                request.session['cliente_id'] = int(cliente_id)
            return redirect('facturacion')

    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(Q(nombre_cliente__icontains=q) | Q(cedula__icontains=q))
    context = {'active_view': 'facturacion', 'clientes': clientes[:30], 'q': q, 'form': form}
    return render(request, 'seleccionar_cliente.html', context)


@require_POST
def confirmar_venta(request):
    cliente = _cliente_actual(request)
    lineas = construir_lineas(obtener_carrito(request.session))

    if not lineas:
        messages.error(request, 'El carrito está vacío.')
        return redirect('facturacion')
    if not cliente:
        messages.error(request, 'No hay un cliente seleccionado.')
        return redirect('facturacion')
    for linea in lineas:
        if linea['cantidad'] > linea['inventario'].stock:
            messages.error(request, f'Stock insuficiente para {linea["inventario"]}.')
            return redirect('facturacion')

    subtotal, iva, total = calcular_totales(lineas)
    es_credito = request.POST.get('registrar_como_deuda') == '1'

    with transaction.atomic():
        venta = Venta.objects.create(
            cliente=cliente,
            subtotal=subtotal,
            total_iva=iva,
            total=total,
            estado_pago=Venta.EstadoPago.CREDITO if es_credito else Venta.EstadoPago.PAGADA,
        )
        for linea in lineas:
            DetalleVenta.objects.create(
                venta=venta,
                inventario=linea['inventario'],
                precio_unitario=linea['precio_unitario'],
                iva=iva_de_linea(linea),
                cantidad=linea['cantidad'],
                subtotal=linea['subtotal'],
            )
        if es_credito:
            from finanzas.models import Deuda
            Deuda.objects.create(cliente=cliente, monto_total=total, venta=venta)

    guardar_carrito(request.session, {})
    messages.success(request, f'Venta #{venta.pk} registrada correctamente.')
    return redirect('dashboard')

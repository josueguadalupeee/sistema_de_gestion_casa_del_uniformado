import hmac

from django.conf import settings
from django.contrib import messages
from django.db.models import ProtectedError, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import CategoriaForm, ColorForm, InventarioForm, ProductoForm, ProveedorForm, SeccionForm, TallaForm
from .models import Categoria, Color, Producto, Proveedor, Seccion, Talla
from .services import enviar_alerta_stock


def inventario(request):
    q = request.GET.get('q', '').strip()
    categoria_activa = request.GET.get('categoria') or None
    categoria_activa = int(categoria_activa) if categoria_activa and categoria_activa.isdigit() else None
    seccion_activa = request.GET.get('seccion') or None
    seccion_activa = int(seccion_activa) if seccion_activa and seccion_activa.isdigit() else None
    stock_filtro = request.GET.get('stock') or None

    productos_qs = Producto.objects.select_related('categoria').prefetch_related(
        'inventarios__talla', 'inventarios__color', 'inventarios__seccion'
    )
    if q:
        productos_qs = productos_qs.filter(Q(nombre_producto__icontains=q) | Q(codigo__icontains=q))
    if categoria_activa:
        productos_qs = productos_qs.filter(categoria_id=categoria_activa)
    if seccion_activa:
        productos_qs = productos_qs.filter(inventarios__seccion_id=seccion_activa).distinct()

    productos = list(productos_qs)
    if stock_filtro == 'bajo':
        productos = [p for p in productos if p.stock_total <= p.stock_minimo_referencia]
    elif stock_filtro == 'ok':
        productos = [p for p in productos if p.stock_total > p.stock_minimo_referencia]

    context = {
        'active_view': 'inventario',
        'q': q,
        'categorias': Categoria.objects.all(),
        'categoria_activa': categoria_activa,
        'secciones': Seccion.objects.all(),
        'seccion_activa': seccion_activa,
        'stock_filtro': stock_filtro,
        'productos': productos,
        'productos_total': len(productos),
    }
    return render(request, 'inventario.html', context)


def producto_nuevo(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado.')
            return redirect('producto_detalle', pk=producto.pk)
    else:
        form = ProductoForm()

    context = {'active_view': 'inventario', 'form': form, 'modo': 'nuevo'}
    return render(request, 'producto_form.html', context)


def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    producto_form = ProductoForm(instance=producto)
    inventario_form = InventarioForm()

    if request.method == 'POST' and 'editar_producto' in request.POST:
        producto_form = ProductoForm(request.POST, request.FILES, instance=producto)
        if producto_form.is_valid():
            producto_form.save()
            messages.success(request, 'Producto actualizado. Las ventas ya registradas conservan los datos con los que se facturaron.')
            return redirect('producto_detalle', pk=producto.pk)

    elif request.method == 'POST' and 'agregar_variante' in request.POST:
        inventario_form = InventarioForm(request.POST)
        if inventario_form.is_valid():
            datos = inventario_form.cleaned_data
            existente = producto.inventarios.filter(
                talla=datos['talla'],
                color=datos['color'],
                seccion=datos['seccion'],
                genero=datos['genero'],
            ).first()
            if existente:
                existente.stock += datos['stock']
                existente.stock_minimo = datos['stock_minimo']
                existente.save(update_fields=['stock', 'stock_minimo'])
                messages.success(
                    request,
                    f'Esa variante ya existía: se sumaron {datos["stock"]} unidades '
                    f'(stock actual: {existente.stock}).',
                )
            else:
                variante = inventario_form.save(commit=False)
                variante.producto = producto
                variante.save()
                messages.success(request, 'Variante agregada al inventario.')
            return redirect('producto_detalle', pk=producto.pk)

    context = {
        'active_view': 'inventario',
        'producto': producto,
        'variantes': producto.inventarios.select_related('talla', 'color', 'seccion').all(),
        'inventario_form': inventario_form,
        'producto_form': producto_form,
    }
    return render(request, 'producto_detalle.html', context)


def proveedores(request):
    q = request.GET.get('q', '').strip()
    proveedores_qs = Proveedor.objects.all()
    if q:
        proveedores_qs = proveedores_qs.filter(nombre_proveedor__icontains=q)
    context = {'active_view': 'proveedores', 'proveedores': proveedores_qs, 'q': q}
    return render(request, 'proveedores.html', context)


def proveedor_nuevo(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre_proveedor}" creado.')
            return redirect('proveedores')
    else:
        form = ProveedorForm()
    context = {'active_view': 'proveedores', 'form': form, 'modo': 'nuevo'}
    return render(request, 'proveedor_form.html', context)


def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre_proveedor}" actualizado.')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    context = {'active_view': 'proveedores', 'form': form, 'modo': 'editar', 'proveedor': proveedor}
    return render(request, 'proveedor_form.html', context)


def categorias(request):
    q = request.GET.get('q', '').strip()
    categorias_qs = Categoria.objects.all()
    if q:
        categorias_qs = categorias_qs.filter(nombre_categoria__icontains=q)
    context = {'active_view': 'categorias', 'categorias': categorias_qs, 'q': q}
    return render(request, 'categorias.html', context)


def categoria_nueva(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre_categoria}" creada.')
            return redirect('categorias')
    else:
        form = CategoriaForm()
    context = {'active_view': 'categorias', 'form': form, 'modo': 'nuevo'}
    return render(request, 'categoria_form.html', context)


def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre_categoria}" actualizada.')
            return redirect('categorias')
    else:
        form = CategoriaForm(instance=categoria)
    context = {'active_view': 'categorias', 'form': form, 'modo': 'editar', 'categoria': categoria}
    return render(request, 'categoria_form.html', context)


def tallas(request):
    context = {'active_view': 'tallas', 'tallas': Talla.objects.all()}
    return render(request, 'tallas.html', context)


def talla_nueva(request):
    if request.method == 'POST':
        form = TallaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Talla creada.')
            return redirect('tallas')
    else:
        form = TallaForm()
    context = {'active_view': 'tallas', 'form': form, 'modo': 'nuevo'}
    return render(request, 'talla_form.html', context)


def talla_editar(request, pk):
    talla = get_object_or_404(Talla, pk=pk)
    if request.method == 'POST':
        form = TallaForm(request.POST, instance=talla)
        if form.is_valid():
            form.save()
            messages.success(request, 'Talla actualizada.')
            return redirect('tallas')
    else:
        form = TallaForm(instance=talla)
    context = {'active_view': 'tallas', 'form': form, 'modo': 'editar', 'talla': talla}
    return render(request, 'talla_form.html', context)


@require_POST
def talla_eliminar(request, pk):
    talla = get_object_or_404(Talla, pk=pk)
    try:
        talla.delete()
        messages.success(request, 'Talla eliminada.')
    except ProtectedError:
        messages.error(request, f'No se puede eliminar "{talla}" porque hay variantes de inventario que la usan.')
    return redirect('tallas')


def colores(request):
    context = {'active_view': 'colores', 'colores': Color.objects.all()}
    return render(request, 'colores.html', context)


def color_nuevo(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Color creado.')
            return redirect('colores')
    else:
        form = ColorForm()
    context = {'active_view': 'colores', 'form': form, 'modo': 'nuevo'}
    return render(request, 'color_form.html', context)


def color_editar(request, pk):
    color = get_object_or_404(Color, pk=pk)
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, 'Color actualizado.')
            return redirect('colores')
    else:
        form = ColorForm(instance=color)
    context = {'active_view': 'colores', 'form': form, 'modo': 'editar', 'color': color}
    return render(request, 'color_form.html', context)


@require_POST
def color_eliminar(request, pk):
    color = get_object_or_404(Color, pk=pk)
    try:
        color.delete()
        messages.success(request, 'Color eliminado.')
    except ProtectedError:
        messages.error(request, f'No se puede eliminar "{color}" porque hay variantes de inventario que lo usan.')
    return redirect('colores')


def secciones(request):
    context = {'active_view': 'secciones', 'secciones': Seccion.objects.all()}
    return render(request, 'secciones.html', context)


def seccion_nueva(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sección creada.')
            return redirect('secciones')
    else:
        form = SeccionForm()
    context = {'active_view': 'secciones', 'form': form, 'modo': 'nuevo'}
    return render(request, 'seccion_form.html', context)


def seccion_editar(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        form = SeccionForm(request.POST, instance=seccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sección actualizada.')
            return redirect('secciones')
    else:
        form = SeccionForm(instance=seccion)
    context = {'active_view': 'secciones', 'form': form, 'modo': 'editar', 'seccion': seccion}
    return render(request, 'seccion_form.html', context)


@require_POST
def seccion_eliminar(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    try:
        seccion.delete()
        messages.success(request, 'Sección eliminada.')
    except ProtectedError:
        messages.error(request, f'No se puede eliminar "{seccion}" porque hay variantes de inventario que la usan.')
    return redirect('secciones')


@require_GET
def tarea_alerta_stock(request):
    """Endpoint disparado por un cron externo (GitHub Actions, cron-job.org, etc.)
    para enviar el reporte diario de stock bajo, ya que el free tier de hosting
    no permite dejar un proceso en segundo plano corriendo.
    """
    token_esperado = settings.TASK_SECRET_TOKEN
    token_recibido = request.GET.get('token', '')
    if not token_esperado or not hmac.compare_digest(token_esperado, token_recibido):
        return HttpResponseForbidden('Token invalido.')

    _, detalle = enviar_alerta_stock()
    return HttpResponse(detalle)

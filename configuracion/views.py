from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import CasaUniformadoForm
from .models import CasaUniformado


def configuracion(request):
    instancia = CasaUniformado.get_solo()

    if request.method == 'POST':
        form = CasaUniformadoForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del negocio actualizados.')
            return redirect('configuracion')
    else:
        form = CasaUniformadoForm(instance=instancia)

    return render(request, 'configuracion.html', {'active_view': 'config', 'form': form})

from django import forms

from .models import CasaUniformado


class CasaUniformadoForm(forms.ModelForm):
    class Meta:
        model = CasaUniformado
        fields = ['nombre', 'ruc', 'direccion', 'correo', 'telefono']

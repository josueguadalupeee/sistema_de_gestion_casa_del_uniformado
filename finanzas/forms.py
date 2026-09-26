from django import forms

from .models import AbonoDeuda, Deuda


class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = ['cliente', 'monto_total', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej. Saldo pendiente antes de usar el sistema, acuerdo especial, etc.'}),
        }


class AbonoDeudaForm(forms.ModelForm):
    class Meta:
        model = AbonoDeuda
        fields = ['monto_abono']

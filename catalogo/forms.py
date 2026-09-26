from django import forms

from .models import Categoria, Color, Inventario, Producto, Proveedor, Seccion, Talla


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'imagen', 'codigo', 'precio_producto', 'iva_aplica', 'categoria', 'proveedor']


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['talla', 'genero', 'color', 'seccion', 'stock', 'stock_minimo']
        help_texts = {
            'talla': 'Si el artículo no usa talla (ej. accesorios), crea y elige una talla "N/A" desde el menú Inventario → Tallas.',
            'genero': 'Deja "No aplica" si el artículo no distingue hombre/mujer (ej. accesorios).',
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_proveedor', 'telefono', 'direccion']


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_categoria', 'descripcion']


class TallaForm(forms.ModelForm):
    class Meta:
        model = Talla
        fields = ['descripcion']


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['descripcion']


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre_seccion']

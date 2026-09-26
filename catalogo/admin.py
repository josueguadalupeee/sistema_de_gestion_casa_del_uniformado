from django.contrib import admin

from .models import Categoria, Color, Inventario, Producto, Proveedor, Seccion, Talla


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'descripcion')
    search_fields = ('nombre_categoria',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_proveedor', 'telefono', 'direccion')
    search_fields = ('nombre_proveedor',)


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre_seccion',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_producto', 'categoria', 'proveedor', 'precio_producto', 'iva_aplica')
    list_filter = ('categoria', 'proveedor', 'iva_aplica')
    search_fields = ('codigo', 'nombre_producto')


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'talla', 'genero', 'color', 'seccion', 'stock', 'stock_minimo', 'necesita_restock')
    list_filter = ('seccion', 'talla', 'color', 'genero')
    search_fields = ('producto__codigo', 'producto__nombre_producto')

    @admin.display(boolean=True, description='¿Restock?')
    def necesita_restock(self, obj):
        return obj.necesita_restock

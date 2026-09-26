from django.contrib import admin

from .models import Cliente, DetalleVenta, Venta


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'cedula', 'telefono', 'correo')
    search_fields = ('nombre_cliente', 'cedula')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'subtotal', 'total_iva', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente__nombre_cliente',)
    inlines = [DetalleVentaInline]

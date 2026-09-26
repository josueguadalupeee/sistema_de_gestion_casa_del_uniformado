from django.contrib import admin

from .models import DetalleFacturaProveedor, FacturaProveedor


class DetalleFacturaProveedorInline(admin.TabularInline):
    model = DetalleFacturaProveedor
    extra = 0


@admin.register(FacturaProveedor)
class FacturaProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'monto_total')
    list_filter = ('proveedor', 'fecha')
    inlines = [DetalleFacturaProveedorInline]

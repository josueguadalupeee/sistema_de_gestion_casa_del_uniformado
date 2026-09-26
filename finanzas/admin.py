from django.contrib import admin

from .models import AbonoDeuda, Deuda


class AbonoDeudaInline(admin.TabularInline):
    model = AbonoDeuda
    extra = 0


@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_deuda', 'monto_total', 'estado', 'saldo_pendiente')
    list_filter = ('estado', 'fecha_deuda')
    search_fields = ('cliente__nombre_cliente',)
    inlines = [AbonoDeudaInline]

    @admin.display(description='Saldo pendiente')
    def saldo_pendiente(self, obj):
        return obj.saldo_pendiente

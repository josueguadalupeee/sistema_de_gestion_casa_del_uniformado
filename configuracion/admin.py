from django.contrib import admin

from .models import CasaUniformado


@admin.register(CasaUniformado)
class CasaUniformadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'correo', 'telefono')

    def has_add_permission(self, request):
        return not CasaUniformado.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

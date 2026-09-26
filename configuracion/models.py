from django.db import models


class CasaUniformado(models.Model):
    """Datos del negocio para el encabezado de facturas. Registro único (pk=1).

    No tiene FK desde ninguna otra tabla: se consulta directo con
    CasaUniformado.get_solo() en la vista/template al generar la factura.
    """

    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Casa de uniformes'
        verbose_name_plural = 'Casa de uniformes'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'nombre': '', 'ruc': ''})
        return obj

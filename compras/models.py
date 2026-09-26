from django.db import models, transaction

from catalogo.models import Inventario, Proveedor


class FacturaProveedor(models.Model):
    imagen_factura = models.ImageField(upload_to='facturas_proveedor/', blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='facturas')
    fecha = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Factura de proveedor'
        verbose_name_plural = 'Facturas de proveedor'
        ordering = ['-fecha']

    def __str__(self):
        return f'Factura #{self.pk} - {self.proveedor}'


class DetalleFacturaProveedor(models.Model):
    factura_proveedor = models.ForeignKey(FacturaProveedor, on_delete=models.CASCADE, related_name='detalles')
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name='detalles_compra')
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de factura de proveedor'
        verbose_name_plural = 'Detalles de factura de proveedor'

    def __str__(self):
        return f'{self.inventario} x{self.cantidad}'

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        with transaction.atomic():
            super().save(*args, **kwargs)
            if es_nuevo:
                Inventario.objects.filter(pk=self.inventario_id).update(
                    stock=models.F('stock') + self.cantidad
                )

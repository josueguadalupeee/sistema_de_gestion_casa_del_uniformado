from django.db import models, transaction

from catalogo.models import Inventario


class Cliente(models.Model):
    nombre_cliente = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_cliente']

    def __str__(self):
        return self.nombre_cliente


class Venta(models.Model):
    class EstadoPago(models.TextChoices):
        PAGADA = 'PAGADA', 'Pagada'
        CREDITO = 'CREDITO', 'A crédito'

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_pago = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.PAGADA)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta #{self.pk} - {self.cliente}'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name='detalles_venta')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self):
        return f'{self.inventario} x{self.cantidad}'

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        with transaction.atomic():
            super().save(*args, **kwargs)
            if es_nuevo:
                Inventario.objects.filter(pk=self.inventario_id).update(
                    stock=models.F('stock') - self.cantidad
                )

from django.db import models

from config.utils import redondear_centavos
from ventas.models import Cliente, Venta


class Deuda(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ABONADA = 'ABONADA', 'Abonada parcialmente'
        PAGADA = 'PAGADA', 'Pagada'

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='deudas')
    venta = models.OneToOneField(
        Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name='deuda',
        help_text='Venta que originó esta deuda (vacío si se registró manualmente).',
    )
    fecha_deuda = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    descripcion = models.TextField(
        blank=True,
        help_text='Opcional. Útil para deudas anteriores a este sistema o cualquier detalle que no venga de una venta.',
    )

    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['-fecha_deuda']

    def __str__(self):
        return f'Deuda #{self.pk} - {self.cliente}'

    @property
    def total_abonado(self):
        return redondear_centavos(self.abonos.aggregate(total=models.Sum('monto_abono'))['total'])

    @property
    def saldo_pendiente(self):
        return self.monto_total - self.total_abonado

    @property
    def pct_abonado(self):
        if not self.monto_total:
            return 0
        return min(100, round((self.total_abonado / self.monto_total) * 100))


class AbonoDeuda(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='abonos')
    fecha_abono = models.DateTimeField(auto_now_add=True)
    monto_abono = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Abono a deuda'
        verbose_name_plural = 'Abonos a deudas'
        ordering = ['-fecha_abono']

    def __str__(self):
        return f'Abono {self.monto_abono} a deuda #{self.deuda_id}'

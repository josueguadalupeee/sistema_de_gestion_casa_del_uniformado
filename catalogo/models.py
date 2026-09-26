from django.db import models


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre_categoria']

    def __str__(self):
        return self.nombre_categoria


class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre_proveedor']

    def __str__(self):
        return self.nombre_proveedor


class Talla(models.Model):
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = 'Talla'
        verbose_name_plural = 'Tallas'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


class Color(models.Model):
    descripcion = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colores'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


class Seccion(models.Model):
    nombre_seccion = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['nombre_seccion']

    def __str__(self):
        return self.nombre_seccion


class Producto(models.Model):
    nombre_producto = models.CharField(max_length=150)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código/SKU')
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)
    iva_aplica = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='productos')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre_producto']

    def __str__(self):
        return f'{self.codigo} - {self.nombre_producto}'

    @property
    def stock_total(self):
        return sum(inv.stock for inv in self.inventarios.all())

    @property
    def stock_minimo_referencia(self):
        return sum(inv.stock_minimo for inv in self.inventarios.all())

    @property
    def variantes_disponibles(self):
        chips = []
        for inv in self.inventarios.all():
            if inv.stock <= 0:
                continue
            partes = [str(inv.color)]
            if str(inv.talla) != 'N/A':
                partes.insert(0, str(inv.talla))
            if inv.genero != Inventario.Genero.NO_APLICA:
                partes.append(inv.get_genero_display())
            chips.append(f'{" · ".join(partes)} · {inv.stock}u')
        return chips


class Inventario(models.Model):
    class Genero(models.TextChoices):
        HOMBRE = 'HOMBRE', 'Hombre'
        MUJER = 'MUJER', 'Mujer'
        UNISEX = 'UNISEX', 'Unisex'
        NO_APLICA = 'NO_APLICA', 'No aplica'

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='inventarios')
    talla = models.ForeignKey(Talla, on_delete=models.PROTECT, related_name='inventarios')
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='inventarios')
    seccion = models.ForeignKey(Seccion, on_delete=models.PROTECT, related_name='inventarios')
    genero = models.CharField(max_length=10, choices=Genero.choices, default=Genero.NO_APLICA)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventario'
        ordering = ['producto__nombre_producto']
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'talla', 'color', 'seccion', 'genero'],
                name='variante_unica_por_producto',
            )
        ]

    def __str__(self):
        return f'{self.producto.codigo} · {self.talla} · {self.color} · {self.seccion} (stock: {self.stock})'

    @property
    def necesita_restock(self):
        return self.stock <= self.stock_minimo

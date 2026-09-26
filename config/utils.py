from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal('0.01')


def redondear_centavos(valor):
    """Redondea un Decimal/int/None a 2 decimales.

    Los Sum() de Django sobre campos Decimal en SQLite a veces devuelven
    resultados con más de 2 decimales (arrastre de precisión); esto normaliza
    cualquier monto en dólares antes de guardarlo o mostrarlo.
    """
    return Decimal(valor or 0).quantize(CENTAVO, rounding=ROUND_HALF_UP)

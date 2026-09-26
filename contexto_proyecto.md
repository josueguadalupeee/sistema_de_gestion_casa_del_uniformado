# Sistema de Inventario y Facturación — Casa de Uniformes

## Contexto del negocio
Sistema para un local que vende uniformes y artículos para policía, agentes de tránsito, bomberos y guardias. Necesita: inventario con control de variantes (talla/color/sección), facturación con cálculo de IVA, alertas de restock por correo, y módulo de deudores.

## Stack técnico
- Python + Django
- PostgreSQL
- JS vanilla (fetch/AJAX) para partes dinámicas, sin framework JS pesado
- Entorno virtual ya creado en `sistema_casa_uniformado/venv`

## División de apps propuesta
- `catalogo`: Producto, Categoria, Proveedor, Talla, Color, Seccion, Inventario
- `ventas`: Venta, DetalleVenta, Cliente
- `compras`: FacturaProveedor, DetalleFacturaProveedor
- `finanzas`: Deuda, AbonoDeuda
- `configuracion`: CasaUniformado (modelo singleton, un solo registro con datos del negocio)

## Modelos y reglas de negocio clave

**Producto**: nombre, imagen, codigo/sku, precio_producto, iva_aplica (bool), FK categoria, FK proveedor. NO tiene talla/color directamente — esos son variantes que viven en Inventario.

**Inventario**: FK producto, FK talla, FK color, FK seccion, stock, stock_minimo (default 5). Cada combinación producto+talla+color+seccion es una fila con su propio stock. Cuando stock <= stock_minimo, debe dispararse alerta por correo (tarea programada recomendada: Celery + Celery Beat, resumen diario en vez de correo por venta).

**Cliente**: debe existir un registro fijo "Consumidor Final" (fixture inicial) para ventas sin datos del cliente.

**Venta** (cabecera): FK cliente, fecha, subtotal, total_iva, total. NO tiene FK a CasaUniformado (ver singleton abajo).

**DetalleVenta**: FK venta, FK inventario, cantidad, precio_unitario (histórico, no se recalcula del producto), iva (monto calculado por línea), subtotal. Al guardar, debe descontar stock del Inventario correspondiente.

**CasaUniformado**: modelo singleton (un solo registro, pk forzado a 1, sin FK desde ninguna otra tabla) con los datos del negocio (nombre, ruc, direccion, correo, telefono) para el encabezado de las facturas. Se consulta directo en la vista/template al generar la factura, nunca por relación.

**FacturaProveedor** (cabecera): imagen_factura, FK proveedor, fecha, monto_total.
**DetalleFacturaProveedor**: FK factura_proveedor, FK inventario (no producto directo, porque hay que saber a qué variante/sección entra el stock), cantidad, costo_unitario, subtotal. Al guardar, debe sumar stock al Inventario correspondiente.

**Deuda**: FK cliente, fecha_deuda, monto_total, estado.
**AbonoDeuda**: FK deuda, fecha_abono, monto_abono. Relación 1 a muchos (una deuda, varios abonos parciales). Saldo pendiente = monto_total - suma(abonos).

**IVA**: 15% fijo (Ecuador). Se calcula y se guarda el monto ya calculado en cada DetalleVenta (histórico), no se recalcula desde un porcentaje global — así si el % cambia a futuro, las ventas viejas no se alteran.

## Diseño de interfaz (ya prototipado en HTML)
Identidad visual: institucional/tipo placa, no genérica de SaaS.
- Colores: azul marino oscuro (sidebar/headers), acento dorado (alertas medias/insignia), rojo ladrillo apagado (alertas críticas/deudas), verde apagado (éxito/pagado)
- Tipografía: Oswald (condensada, mayúsculas, para títulos), Inter (cuerpo), IBM Plex Mono (precios, SKU, códigos, stock)
- Elemento de firma: líneas punteadas tipo "costura" de tela como separadores de sección
- Pantallas prototipadas: Panel general (dashboard con KPIs y alertas de stock), Inventario (grid de productos con variantes), Facturación (vista tipo POS con carrito), Clientes y deudores (cuentas por cobrar con progreso de abonos)

## Estado actual
- ERD completo y validado (todas las cardinalidades revisadas)
- Mockup de interfaz HTML ya creado como referencia visual
- Entorno virtual creado y Django listo para instalar/usar
- Pendiente: crear el proyecto Django, las apps, los modelos, migraciones, y luego las vistas

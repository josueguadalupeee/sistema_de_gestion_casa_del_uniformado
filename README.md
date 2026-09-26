# Sistema de Inventario y Facturación — Casa de Uniformes

Sistema de gestión para un local que vende uniformes y artículos para policía, agentes de tránsito, bomberos y guardias de seguridad. Controla inventario por variantes (talla/color/sección), factura con cálculo de IVA, envía alertas de restock por correo y lleva un módulo de deudores.

## Stack técnico

- Python + Django
- PostgreSQL (o SQLite en desarrollo)
- JavaScript vanilla (fetch/AJAX) para las partes dinámicas, sin framework pesado

## Módulos

- **catalogo** — Producto, Categoría, Proveedor, Talla, Color, Sección, Inventario
- **ventas** — Venta, DetalleVenta, Cliente
- **compras** — FacturaProveedor, DetalleFacturaProveedor
- **finanzas** — Deuda, AbonoDeuda
- **configuracion** — Datos del negocio (modelo singleton)

Reglas de negocio clave: el stock vive en `Inventario` (una fila por combinación producto+talla+color+sección), el IVA se calcula y guarda de forma histórica en cada línea de venta (15% fijo, Ecuador), y hay un cliente fijo "Consumidor Final" para ventas sin datos del cliente.

## Requisitos

- Python 3.12+
- pip
- PostgreSQL (opcional; por defecto usa SQLite)

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd sistema_casa_uniformado

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# editar .env con tus propios valores (ver sección siguiente)

# 5. Aplicar migraciones y cargar datos iniciales
python manage.py migrate
python manage.py loaddata cliente_consumidor_final

# 6. Crear un superusuario (para entrar al admin de Django)
python manage.py createsuperuser

# 7. Levantar el servidor de desarrollo
python manage.py runserver
```

## Variables de entorno

El proyecto usa [python-decouple](https://pypi.org/project/python-decouple/) para leer configuración desde un archivo `.env` (nunca se sube al repositorio — ver `.env.example` como plantilla).

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. Generar una nueva con `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma |
| `DB_ENGINE` | `sqlite` (por defecto) o `postgresql` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Credenciales de PostgreSQL (solo si `DB_ENGINE=postgresql`) |
| `EMAIL_BACKEND` | `console` (por defecto, imprime en consola) o `smtp` para enviar correos reales |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Configuración SMTP (solo si `EMAIL_BACKEND=smtp`) |
| `STOCK_ALERT_RECIPIENTS` | Correo(s) que reciben el reporte diario de stock bajo, separados por coma |
| `TASK_SECRET_TOKEN` | Token requerido por `/tareas/alerta-stock/?token=...` para disparar el reporte desde un cron externo |
| `IVA_PORCENTAJE` | Porcentaje de IVA aplicado (15.00 por defecto, Ecuador) |

**Importante:** genera tu propio `SECRET_KEY` y `TASK_SECRET_TOKEN`, y usa una contraseña de aplicación (no tu contraseña normal) si activas `EMAIL_BACKEND=smtp` con Gmail. Nunca subas el archivo `.env` real al repositorio.

## Alerta diaria de stock (GitHub Actions)

`.github/workflows/alerta-stock.yml` llama diariamente al endpoint `/tareas/alerta-stock/?token=...` mediante un cron de GitHub Actions (pensado para hosting gratuito que no permite procesos programados). Requiere configurar estos secretos en **Settings → Secrets and variables → Actions** del repositorio:

- `APP_URL` — URL base de la app desplegada
- `STOCK_ALERT_TOKEN` — mismo valor que `TASK_SECRET_TOKEN` en el `.env` de producción

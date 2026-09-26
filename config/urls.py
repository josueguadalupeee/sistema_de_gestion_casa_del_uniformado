from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('', include('catalogo.urls')),
    path('', include('ventas.urls')),
    path('', include('finanzas.urls')),
    path('', include('compras.urls')),
    path('', include('configuracion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

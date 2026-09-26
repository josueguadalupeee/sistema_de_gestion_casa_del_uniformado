from django.urls import path

from . import views

urlpatterns = [
    path('compras/facturas-proveedor/', views.facturas_proveedor, name='facturas_proveedor'),
]

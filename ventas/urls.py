from django.urls import path

from . import views

urlpatterns = [
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/nuevo/', views.cliente_nuevo, name='cliente_nuevo'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('ventas/', views.ventas_lista, name='ventas'),
    path('ventas/<int:pk>/', views.venta_detalle, name='venta_detalle'),
    path('facturacion/', views.facturacion, name='facturacion'),
    path('facturacion/buscar/', views.buscar_productos, name='buscar_productos'),
    path('facturacion/carrito/agregar/', views.carrito_agregar, name='carrito_agregar'),
    path('facturacion/carrito/actualizar/', views.carrito_actualizar, name='carrito_actualizar'),
    path('facturacion/carrito/vaciar/', views.carrito_vaciar, name='carrito_vaciar'),
    path('facturacion/cliente/', views.seleccionar_cliente, name='seleccionar_cliente'),
    path('facturacion/confirmar/', views.confirmar_venta, name='confirmar_venta'),
]

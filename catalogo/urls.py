from django.urls import path

from . import views

urlpatterns = [
    path('inventario/', views.inventario, name='inventario'),
    path('inventario/productos/nuevo/', views.producto_nuevo, name='producto_nuevo'),
    path('inventario/productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/nuevo/', views.proveedor_nuevo, name='proveedor_nuevo'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('categorias/', views.categorias, name='categorias'),
    path('categorias/nueva/', views.categoria_nueva, name='categoria_nueva'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('tallas/', views.tallas, name='tallas'),
    path('tallas/nueva/', views.talla_nueva, name='talla_nueva'),
    path('tallas/<int:pk>/editar/', views.talla_editar, name='talla_editar'),
    path('tallas/<int:pk>/eliminar/', views.talla_eliminar, name='talla_eliminar'),
    path('colores/', views.colores, name='colores'),
    path('colores/nuevo/', views.color_nuevo, name='color_nuevo'),
    path('colores/<int:pk>/editar/', views.color_editar, name='color_editar'),
    path('colores/<int:pk>/eliminar/', views.color_eliminar, name='color_eliminar'),
    path('secciones/', views.secciones, name='secciones'),
    path('secciones/nueva/', views.seccion_nueva, name='seccion_nueva'),
    path('secciones/<int:pk>/editar/', views.seccion_editar, name='seccion_editar'),
    path('secciones/<int:pk>/eliminar/', views.seccion_eliminar, name='seccion_eliminar'),
    path('tareas/alerta-stock/', views.tarea_alerta_stock, name='tarea_alerta_stock'),
]

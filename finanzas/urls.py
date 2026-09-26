from django.urls import path

from . import views

urlpatterns = [
    path('deudores/', views.deudores, name='deudores'),
    path('deudores/nueva/', views.deuda_nueva, name='deuda_nueva'),
    path('deudores/<int:pk>/', views.deuda_detalle, name='deuda_detalle'),
]

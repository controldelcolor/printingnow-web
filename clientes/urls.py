"""URLs de la app clientes (público)."""
from django.urls import path
from . import views

urlpatterns = [
    path('',               views.home,          name='home'),
    path('api/clientes/',  views.api_clientes,  name='api_clientes'),
]

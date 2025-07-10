from django.urls import path
from .views import report, index, motoristas, caminhoes

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("report/", views.report, name="report"),
    path("motoristas/", views.motoristas, name="motoristas"),
    path("caminhoes/", views.caminhoes, name="caminhoes"),
    path("grafico_pizza/", views.grafico_emissoes_por_marca, name='grafico_emissoes'),
]

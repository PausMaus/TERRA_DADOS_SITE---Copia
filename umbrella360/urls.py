from django.urls import path
from .views import report, index, motoristas, caminhoes

from . import views

urlpatterns = [
    path("umbrella/", views.index, name="index"),
    path("umbrella/report/", views.report, name="report"),
    path("umbrella/motoristas/", views.motoristas, name="motoristas"),
    path("umbrella/caminhoes/", views.caminhoes, name="caminhoes"),
]

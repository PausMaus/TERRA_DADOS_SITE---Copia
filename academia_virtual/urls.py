from django.urls import path

from . import views

app_name = 'academia_virtual'

urlpatterns = [
    path("", views.index, name="index"),
    path("item/<int:item_id>/", views.detalhe, name="detalhe"),
    path("exercicio/<int:exercicio_id>/", views.exercicio_detalhe, name="exercicio_detalhe"),
]
from django.urls import path
from .views import report, index, motoristas, caminhoes

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("report/", views.report, name="report"),
    path("report-novo/", views.report_novo, name="report_novo"),
    path("report-empresa/", views.report_empresa, name="report_empresa"),
    path("ranking/", views.ranking_empresa, name="ranking_empresa"),
    path("lista-unidades/", views.lista_unidades, name="lista_unidades"),
    path("unidade/<str:unidade_id>/", views.detalhes_unidade, name="detalhes_unidade"),
    path("motoristas/", views.motoristas, name="motoristas"),
    path("caminhoes/", views.caminhoes, name="caminhoes"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("grafico_pizza/", views.grafico_emissoes_por_marca, name='grafico_emissoes'),
    # APIs para filtros dinâmicos
    path("api/marcas/", views.api_marcas_todas, name="api_marcas_todas"),
    path("api/marcas/<int:empresa_id>/", views.api_marcas_por_empresa, name="api_marcas_por_empresa"),
]

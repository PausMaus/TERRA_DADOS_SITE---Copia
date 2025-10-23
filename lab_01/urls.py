from django.urls import path
from . import views

app_name = 'lab_01'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('importar/', views.importar_csv, name='importar'),
    path('correlacao/', views.correlacao, name='correlacao'),
]

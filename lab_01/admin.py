from django.contrib import admin
from .models import Regiao, GoogleTrendsData, Usuario, YouTubeData

@admin.register(Regiao)
class RegiaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla', 'populacao', 'area']
    search_fields = ['nome', 'sigla']

@admin.register(GoogleTrendsData)
class GoogleTrendsDataAdmin(admin.ModelAdmin):
    list_display = ['termo', 'regiao', 'interesse', 'data_inicial', 'data_final']
    list_filter = ['termo', 'data_inicial', 'regiao']
    search_fields = ['termo', 'regiao__nome']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', ]
    search_fields = ['username', 'email']
    
    def save_model(self, request, obj, form, change):
        """Ao salvar, faz hash da senha se foi modificada"""
        if 'senha' in form.changed_data:
            obj.set_senha(form.cleaned_data['senha'])
        super().save_model(request, obj, form, change)


@admin.register(YouTubeData)
class YoutubeDataAdmin(admin.ModelAdmin):
    list_display = ['termo','data_inicial']

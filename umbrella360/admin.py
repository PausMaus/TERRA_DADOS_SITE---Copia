from django.contrib import admin
from .models import Motorista, Caminhao





# Register your models here.





class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('agrupamento','quilometragem', 'Consumido', 'Quilometragem_média',
                    'Horas_de_motor', 'Velocidade_média', 'Emissões_CO2')
    search_fields = ('agrupamento',)
    ordering = ('agrupamento',)


class CaminhaoAdmin(admin.ModelAdmin):
    list_display = ('agrupamento', 'marca', 'quilometragem', 'Consumido', 'Quilometragem_média',
                    'Horas_de_motor', 'Velocidade_média', 'RPM_médio',
                    'Temperatura_média', 'Emissões_CO2')
    search_fields = ('agrupamento', 'marca')
    ordering = ('agrupamento',)


admin.site.register(Motorista, MotoristaAdmin)
admin.site.register(Caminhao, CaminhaoAdmin)

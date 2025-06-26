from django.contrib import admin
from .models import Motorista, Caminhao, Calculo_Scania, Calculo_Volvo





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


class Calculo_ScaniaAdmin(admin.ModelAdmin):
    list_display = ('quilometragem', 'Consumido', 'Quilometragem_média',
                    'Velocidade_média', 'RPM_médio',
                    'Temperatura_média', 'Emissões_CO2')

class Calculo_VolvoAdmin(admin.ModelAdmin):
    list_display = ('quilometragem', 'Consumido', 'Quilometragem_média',
                    'Velocidade_média', 'RPM_médio',
                    'Temperatura_média', 'Emissões_CO2')


admin.site.register(Motorista, MotoristaAdmin)
admin.site.register(Caminhao, CaminhaoAdmin)
admin.site.register(Calculo_Scania, Calculo_ScaniaAdmin)
admin.site.register(Calculo_Volvo, Calculo_VolvoAdmin)

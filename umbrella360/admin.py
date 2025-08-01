from django.contrib import admin
from .models import Motorista, Caminhao, Viagem_CAM, Viagem_MOT, ConfiguracaoSistema, Empresa, Unidade, Viagem_Base

# Register your models here.

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'categoria', 'data_modificacao')
    list_filter = ('categoria', 'data_modificacao')
    search_fields = ('chave', 'descricao')
    ordering = ('categoria', 'chave')
    readonly_fields = ('data_modificacao',)
    
    fieldsets = (
        ('Configuração', {
            'fields': ('chave', 'valor')
        }),
        ('Informações', {
            'fields': ('descricao', 'categoria', 'data_modificacao')
        })
    )


class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('agrupamento',)
    search_fields = ('agrupamento',)
    ordering = ('agrupamento',)
    list_filter = ('agrupamento',)


class CaminhaoAdmin(admin.ModelAdmin):
    list_display = ('agrupamento', 'marca')
    search_fields = ('agrupamento', 'marca')
    ordering = ('agrupamento',)
    list_filter = ('marca',)

class ViagemMOTAdmin(admin.ModelAdmin):
    list_display = ('agrupamento', 'quilometragem', 'Consumido', 'Quilometragem_média',
                    'Horas_de_motor', 'Velocidade_média', 'Emissões_CO2', 'mês')
    search_fields = ('agrupamento__agrupamento',)
    ordering = ('agrupamento',)
    list_filter = ('mês', 'agrupamento')
    list_editable = ('quilometragem', 'Consumido')
    
    def get_motorista_nome(self, obj):
        return obj.agrupamento.agrupamento
    get_motorista_nome.short_description = 'Motorista'
    get_motorista_nome.admin_order_field = 'agrupamento__agrupamento'

class ViagemCAMAdmin(admin.ModelAdmin):
    list_display = ('agrupamento',  'quilometragem', 'Consumido', 'Quilometragem_média',
                    'Horas_de_motor', 'Velocidade_média', 'RPM_médio',
                    'Temperatura_média', 'Emissões_CO2', 'mês')
    list_filter = ('mês',  'Quilometragem_média')
    list_editable = ('quilometragem', 'Consumido')





admin.site.register(Motorista, MotoristaAdmin)
admin.site.register(Caminhao, CaminhaoAdmin)
admin.site.register(Viagem_CAM, ViagemCAMAdmin)
admin.site.register(Viagem_MOT, ViagemMOTAdmin)



##############################################################################
#novos modelos para o sistema UMBRELLA 360
##############################################################################
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    ordering = ('nome',)




@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nm', 'cls', 'placa', 'marca')
    list_filter = ('cls', 'marca', 'empresa')
    ordering = ('nm',)



@admin.register(Viagem_Base)
class ViagemBaseAdmin(admin.ModelAdmin):
    list_display = ('unidade', 'quilometragem', 'Consumido', 'Quilometragem_média',
                    'Horas_de_motor', 'Velocidade_média', 'RPM_médio',
                    'Temperatura_média', 'Emissões_CO2', 'período')
    list_filter = ('período',  'Quilometragem_média','unidade__empresa')
    list_editable = ('quilometragem', 'Consumido')
    

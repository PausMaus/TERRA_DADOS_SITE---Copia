from django.contrib import admin
from .models import Motorista,  ConfiguracaoSistema, Empresa, Unidade, Viagem_Base, CheckPoint, Infrações, Viagem_eco
from .models import Veiculo
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



##############################################################################
#novos modelos para o sistema UMBRELLA 360
##############################################################################
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome','senha')
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
    list_filter = ('período','unidade__empresa')
    list_editable = ('quilometragem', 'Consumido')


@admin.register(CheckPoint)
class CheckPointAdmin(admin.ModelAdmin):
    list_display = ('unidade', 'cerca', 'data_entrada', 'data_saida', 'duracao')
    list_filter = ('unidade__empresa', 'cerca')
    search_fields = ('unidade__nm', 'cerca')
    ordering = ('unidade', 'data_entrada')
    readonly_fields = ('duracao',)


    
@admin.register(Infrações)
class InfracoesAdmin(admin.ModelAdmin):
    list_display = ('unidade', 'limite', 'velocidade', 'localizacao', 'data')
    list_filter = ('unidade__empresa', 'data')
    search_fields = ('unidade__nm', 'localizacao')
    ordering = ('unidade', 'data')


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('nm','placa', 'marca', 'modelo', 'ano', 'empresa')
    list_filter = ('marca', 'modelo', 'ano', 'empresa')
    search_fields = ('placa', 'marca', 'modelo')
    ordering = ('placa',)

@admin.register(Viagem_eco)
class ViagemEcoAdmin(admin.ModelAdmin):
    list_display = ('unidade', 'timestamp', 'rpm')

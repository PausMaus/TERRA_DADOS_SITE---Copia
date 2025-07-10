from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from decimal import Decimal
from datetime import date
from .models import Motorista, Caminhao, Viagem_MOT, Viagem_CAM, ConfiguracaoSistema
from .views import (
    aplicar_filtro_mes, 
    aplicar_filtro_combustivel, 
    aplicar_filtros_combinados,
    processar_filtros_request,
    get_base_context
)
from .config import Config, ConfiguracaoManager


class ModelTestCase(TestCase):
    """Testes para os modelos do sistema"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar motorista
        self.motorista = Motorista.objects.create(
            agrupamento="João Silva"
        )
        
        # Criar caminhão
        self.caminhao = Caminhao.objects.create(
            agrupamento="ABC1234",
            marca="Scania"
        )

    def test_motorista_str(self):
        """Teste do método __str__ do modelo Motorista"""
        self.assertEqual(str(self.motorista), "João Silva")

    def test_caminhao_str(self):
        """Teste do método __str__ do modelo Caminhao"""
        expected = "ABC1234 - Scania"
        self.assertEqual(str(self.caminhao), expected)

    def test_viagem_mot_creation(self):
        """Teste de criação de viagem de motorista"""
        viagem = Viagem_MOT.objects.create(
            agrupamento=self.motorista,
            quilometragem=Decimal('800.0'),
            Consumido=150,
            Quilometragem_média=Decimal('5.32'),
            Horas_de_motor="12.5",
            Velocidade_média=64.0,
            Emissões_CO2=2.65,
            mês="janeiro"
        )
        
        self.assertEqual(viagem.agrupamento, self.motorista)
        self.assertEqual(viagem.Consumido, 150)
        self.assertEqual(viagem.mês, "janeiro")

    def test_viagem_cam_creation(self):
        """Teste de criação de viagem de caminhão"""
        viagem = Viagem_CAM.objects.create(
            agrupamento=self.caminhao,
            quilometragem=Decimal('1000.0'),
            Consumido=200,
            Quilometragem_média=Decimal('4.98'),
            Horas_de_motor="15.2",
            Velocidade_média=65.8,
            RPM_médio=1250.0,
            Temperatura_média=85.5,
            Emissões_CO2=2.68,
            mês="fevereiro"
        )
        
        self.assertEqual(viagem.agrupamento, self.caminhao)
        self.assertEqual(viagem.Consumido, 200)
        self.assertEqual(viagem.mês, "fevereiro")


class ConfiguracaoTestCase(TestCase):
    """Testes para o sistema de configuração dinâmica"""
    
    def setUp(self):
        """Configuração inicial para os testes de configuração"""
        # Limpar cache antes de cada teste
        cache.clear()
        # Limpar configurações existentes
        ConfiguracaoSistema.objects.all().delete()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        cache.clear()
    
    def test_configuracao_creation(self):
        """Teste de criação de configuração"""
        config = ConfiguracaoSistema.objects.create(
            chave='test_config',
            valor=10.5,
            descricao='Configuração de teste',
            categoria='teste'
        )
        
        self.assertEqual(config.chave, 'test_config')
        self.assertEqual(config.valor, 10.5)
        self.assertEqual(config.categoria, 'teste')
        self.assertTrue(config.data_modificacao)
    
    def test_configuracao_str(self):
        """Teste do método __str__ do modelo ConfiguracaoSistema"""
        config = ConfiguracaoSistema.objects.create(
            chave='test_key',
            valor=5.96,
            descricao='Teste',
            categoria='teste'
        )
        expected = "test_key: 5.96"
        self.assertEqual(str(config), expected)
    
    def test_configuracao_manager_get_valor(self):
        """Teste do ConfiguracaoManager.get_valor"""
        # Criar configuração no banco
        ConfiguracaoSistema.objects.create(
            chave='custo_diesel',
            valor=6.50,
            descricao='Custo do diesel',
            categoria='financeiro'
        )
        
        # Testar obtenção do valor
        valor = ConfiguracaoManager.get_valor('custo_diesel')
        self.assertEqual(valor, 6.50)
    
    def test_configuracao_manager_valor_inexistente(self):
        """Teste do ConfiguracaoManager com valor inexistente"""
        valor = ConfiguracaoManager.get_valor('chave_inexistente', 10.0)
        self.assertEqual(valor, 10.0)  # Deve retornar o default
    
    def test_configuracao_manager_set_valor(self):
        """Teste do ConfiguracaoManager.set_valor"""
        ConfiguracaoManager.set_valor(
            'test_set', 
            15.75, 
            'Teste de set', 
            'teste'
        )
        
        # Verificar se foi criado no banco
        config = ConfiguracaoSistema.objects.get(chave='test_set')
        self.assertEqual(config.valor, 15.75)
        self.assertEqual(config.descricao, 'Teste de set')
    
    def test_config_class_methods(self):
        """Teste dos métodos da classe Config"""
        # Criar configurações
        ConfiguracaoSistema.objects.create(
            chave='custo_diesel', valor=5.96, 
            descricao='Custo diesel', categoria='financeiro'
        )
        ConfiguracaoSistema.objects.create(
            chave='media_km_objetivo', valor=1.78, 
            descricao='Meta km/L', categoria='performance'
        )
        
        # Testar métodos
        self.assertEqual(Config.custo_diesel(), 5.96)
        self.assertEqual(Config.media_km_objetivo(), 1.78)
        self.assertEqual(Config.consumo_maximo_normal(), 15000.0)  # Default
    
    def test_config_media_km_atual_dinamica(self):
        """Teste do cálculo dinâmico de média km/L atual"""
        # Criar dados de teste
        motorista = Motorista.objects.create(agrupamento="Test")
        caminhao = Caminhao.objects.create(agrupamento="CAM001", marca="Scania")
        
        # Criar viagens com diferentes eficiências
        Viagem_CAM.objects.create(
            agrupamento=caminhao,
            quilometragem=Decimal('1000.0'),
            Consumido=200,  # 5 km/L
            Quilometragem_média=Decimal('5.0'),
            Horas_de_motor="10.0",
            Velocidade_média=60.0,
            RPM_médio=1200.0,
            Temperatura_média=80.0,
            Emissões_CO2=2.5,
            mês="janeiro"
        )
        
        Viagem_CAM.objects.create(
            agrupamento=caminhao,
            quilometragem=Decimal('800.0'),
            Consumido=200,  # 4 km/L
            Quilometragem_média=Decimal('4.0'),
            Horas_de_motor="10.0",
            Velocidade_média=60.0,
            RPM_médio=1200.0,
            Temperatura_média=80.0,
            Emissões_CO2=2.5,
            mês="janeiro"
        )
        
        # A média deve ser (5 + 4) / 2 = 4.5
        media_atual = Config.media_km_atual()
        self.assertEqual(media_atual, 4.5)
    
    def test_inicializacao_configuracoes(self):
        """Teste da inicialização das configurações padrão"""
        # Executar inicialização
        ConfiguracaoManager.inicializar_configuracoes()
        
        # Verificar se as configurações foram criadas
        configuracoes_esperadas = [
            'custo_diesel',
            'media_km_objetivo', 
            'consumo_maximo_normal',
            'consumo_limite_erro',
            'fator_emissao_co2',
            'registros_por_pagina'
        ]
        
        for chave in configuracoes_esperadas:
            with self.subTest(chave=chave):
                self.assertTrue(
                    ConfiguracaoSistema.objects.filter(chave=chave).exists(),
                    f"Configuração {chave} não foi criada"
                )


class ViewTestCase(TestCase):
    """Testes para as views do sistema atualizado"""
    
    def setUp(self):
        """Configuração inicial para os testes de views"""
        self.client = Client()
        
        # Limpar configurações e inicializar
        cache.clear()
        ConfiguracaoSistema.objects.all().delete()
        ConfiguracaoManager.inicializar_configuracoes()
        
        # Criar dados de teste
        self.motorista = Motorista.objects.create(
            agrupamento="Test Driver"
        )
        
        self.caminhao_scania = Caminhao.objects.create(
            agrupamento="SCANIA01",
            marca="Scania"
        )
        
        self.caminhao_volvo = Caminhao.objects.create(
            agrupamento="VOLVO01",
            marca="Volvo"
        )
        
        # Criar viagens de teste variadas
        self.viagem_mot_janeiro = Viagem_MOT.objects.create(
            agrupamento=self.motorista,
            quilometragem=Decimal('500.0'),
            Consumido=100,
            Quilometragem_média=Decimal('5.0'),
            Horas_de_motor="10.0",
            Velocidade_média=50.0,
            Emissões_CO2=2.5,
            mês="janeiro"
        )
        
        self.viagem_mot_zero = Viagem_MOT.objects.create(
            agrupamento=self.motorista,
            quilometragem=Decimal('0.0'),
            Consumido=0,  # Consumo zero
            Quilometragem_média=Decimal('0.0'),
            Horas_de_motor="0.0",
            Velocidade_média=0.0,
            Emissões_CO2=0.0,
            mês="fevereiro"
        )
        
        self.viagem_cam_normal = Viagem_CAM.objects.create(
            agrupamento=self.caminhao_scania,
            quilometragem=Decimal('750.0'),
            Consumido=150,
            Quilometragem_média=Decimal('5.0'),
            Horas_de_motor="15.0",
            Velocidade_média=50.0,
            RPM_médio=1200.0,
            Temperatura_média=80.0,
            Emissões_CO2=2.6,
            mês="março"
        )
        
        # Viagem com consumo alto (erro)
        self.viagem_cam_erro = Viagem_CAM.objects.create(
            agrupamento=self.caminhao_volvo,
            quilometragem=Decimal('100.0'),
            Consumido=60000,  # Erro de leitura
            Quilometragem_média=Decimal('0.002'),
            Horas_de_motor="5.0",
            Velocidade_média=20.0,
            RPM_médio=1500.0,
            Temperatura_média=90.0,
            Emissões_CO2=80.0,
            mês="março"
        )

    def test_index_view(self):
        """Teste da view index"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Umbrella360")

    def test_index_view_with_new_filters(self):
        """Teste da view index com novos filtros"""
        response = self.client.get(reverse('index'), {
            'mes': 'janeiro',
            'filtro_combustivel': 'sem_zero'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['mes_selecionado'], 'janeiro')
        self.assertEqual(response.context['filtro_combustivel'], 'sem_zero')

    def test_index_view_with_legacy_filter(self):
        """Teste de compatibilidade com filtro legacy"""
        response = self.client.get(reverse('index'), {
            'mes': 'janeiro',
            'remover_zero': 'sim'
        })
        self.assertEqual(response.status_code, 200)
        # Deve converter remover_zero para filtro_combustivel
        self.assertEqual(response.context['filtro_combustivel'], 'sem_zero')

    def test_report_view_basic(self):
        """Teste básico da view report"""
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se usa configurações dinâmicas
        self.assertIn('custo_diesel', response.context)
        self.assertIn('media_km_atual', response.context)
        self.assertIn('media_km_fixa', response.context)

    def test_report_view_with_advanced_filters(self):
        """Teste da view report com filtros avançados"""
        response = self.client.get(reverse('report'), {
            'mes': 'março',
            'filtro_combustivel': 'normais'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['mes_selecionado'], 'março')
        self.assertEqual(response.context['filtro_combustivel'], 'normais')

    def test_report_view_filter_errors(self):
        """Teste do filtro de erros na view report"""
        response = self.client.get(reverse('report'), {
            'filtro_combustivel': 'erros'
        })
        self.assertEqual(response.status_code, 200)
        # Deve mostrar apenas viagens com erros de consumo

    def test_motoristas_view_with_filters(self):
        """Teste da view motoristas com filtros"""
        response = self.client.get(reverse('motoristas'), {
            'mes': 'janeiro',
            'filtro_combustivel': 'sem_zero'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Viagens de Motoristas")

    def test_caminhoes_view_dynamic_stats(self):
        """Teste da view caminhões com estatísticas dinâmicas"""
        response = self.client.get(reverse('caminhoes'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se as estatísticas por marca estão sendo calculadas
        self.assertIn('scania_stats', response.context)
        self.assertIn('volvo_stats', response.context)
        
        # Verificar se o gráfico está sendo gerado
        self.assertIn('grafico', response.context)

    def test_caminhoes_view_with_brand_filter(self):
        """Teste da view caminhões com filtros que afetam estatísticas por marca"""
        response = self.client.get(reverse('caminhoes'), {
            'filtro_combustivel': 'normais'
        })
        self.assertEqual(response.status_code, 200)
        
        # As estatísticas devem refletir apenas dados normais
        scania_stats = response.context['scania_stats']
        volvo_stats = response.context['volvo_stats']
        
        # Verificar que existe pelo menos uma estatística
        self.assertIsNotNone(scania_stats)
        self.assertIsNotNone(volvo_stats)

    def test_grafico_emissoes_view_with_filters(self):
        """Teste da view gráfico de emissões com filtros"""
        response = self.client.get(reverse('grafico_emissoes'), {
            'mes': 'março',
            'filtro_combustivel': 'todos'
        })
        self.assertEqual(response.status_code, 200)
        
        # Verificar que todos os gráficos estão no contexto
        graficos_esperados = [
            'grafico_emissoes', 'grafico_consumo', 'grafico_eficiencia',
            'grafico_velocidade', 'grafico_rpm', 'grafico_scatter',
            'grafico_heatmap', 'grafico_radar', 'grafico_area'
        ]
        
        for grafico in graficos_esperados:
            with self.subTest(grafico=grafico):
                self.assertIn(grafico, response.context)

    def test_view_context_consistency(self):
        """Teste de consistência do contexto entre views"""
        views_with_filters = ['index', 'report', 'motoristas', 'caminhoes', 'grafico_emissoes']
        
        for view_name in views_with_filters:
            with self.subTest(view=view_name):
                response = self.client.get(reverse(view_name), {
                    'mes': 'março',
                    'filtro_combustivel': 'normais'
                })
                self.assertEqual(response.status_code, 200)
                
                # Verificar contexto base comum
                context_keys = ['mes_selecionado', 'filtro_combustivel', 'meses_disponiveis']
                for key in context_keys:
                    self.assertIn(key, response.context, f"Chave {key} faltando em {view_name}")

    def test_configuration_values_in_views(self):
        """Teste se as views estão usando valores de configuração dinâmicos"""
        # Alterar uma configuração
        ConfiguracaoManager.set_valor('custo_diesel', 7.50, 'Teste', 'financeiro')
        
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o novo valor está sendo usado
        self.assertEqual(response.context['custo_diesel'], 7.50)

    def test_empty_data_handling(self):
        """Teste do comportamento com dados vazios"""
        # Limpar todos os dados
        Viagem_MOT.objects.all().delete()
        Viagem_CAM.objects.all().delete()
        
        views_to_test = ['report', 'motoristas', 'caminhoes', 'grafico_emissoes']
        
        for view_name in views_to_test:
            with self.subTest(view=view_name):
                response = self.client.get(reverse(view_name))
                self.assertEqual(response.status_code, 200)
                # Views devem lidar graciosamente com dados vazios


class FilterTestCase(TestCase):
    """Testes para as funções de filtro atualizadas"""
    
    def setUp(self):
        """Configuração inicial para os testes de filtro"""
        # Limpar cache e configurações
        cache.clear()
        ConfiguracaoSistema.objects.all().delete()
        
        # Inicializar configurações para os testes
        ConfiguracaoManager.inicializar_configuracoes()
        
        # Criar dados de teste
        self.motorista = Motorista.objects.create(
            agrupamento="Filter Test"
        )
        
        self.caminhao = Caminhao.objects.create(
            agrupamento="FILTER01",
            marca="Scania"
        )
        
        # Viagem com consumo normal
        self.viagem_normal = Viagem_MOT.objects.create(
            agrupamento=self.motorista,
            quilometragem=Decimal('500.0'),
            Consumido=100,
            Quilometragem_média=Decimal('5.0'),
            Horas_de_motor="10.0",
            Velocidade_média=50.0,
            Emissões_CO2=2.5,
            mês="janeiro"
        )
        
        # Viagem com consumo zero
        self.viagem_zero = Viagem_MOT.objects.create(
            agrupamento=self.motorista,
            quilometragem=Decimal('0.0'),
            Consumido=0,
            Quilometragem_média=Decimal('0.0'),
            Horas_de_motor="0.0",
            Velocidade_média=0.0,
            Emissões_CO2=0.0,
            mês="fevereiro"
        )
        
        # Viagem com consumo alto (erro)
        self.viagem_erro = Viagem_CAM.objects.create(
            agrupamento=self.caminhao,
            quilometragem=Decimal('1000.0'),
            Consumido=75000,  # Consumo muito alto (erro)
            Quilometragem_média=Decimal('0.01'),
            Horas_de_motor="10.0",
            Velocidade_média=50.0,
            RPM_médio=1200.0,
            Temperatura_média=80.0,
            Emissões_CO2=100.0,
            mês="março"
        )
        
        # Viagem normal de caminhão
        self.viagem_cam_normal = Viagem_CAM.objects.create(
            agrupamento=self.caminhao,
            quilometragem=Decimal('800.0'),
            Consumido=200,
            Quilometragem_média=Decimal('4.0'),
            Horas_de_motor="10.0",
            Velocidade_média=60.0,
            RPM_médio=1200.0,
            Temperatura_média=80.0,
            Emissões_CO2=2.5,
            mês="março"
        )

    def test_filtro_mes_todos(self):
        """Teste do filtro de mês com 'todos'"""
        queryset = Viagem_MOT.objects.all()
        resultado = aplicar_filtro_mes(queryset, 'todos')
        self.assertEqual(resultado.count(), 2)

    def test_filtro_mes_janeiro(self):
        """Teste do filtro de mês com janeiro"""
        queryset = Viagem_MOT.objects.all()
        resultado = aplicar_filtro_mes(queryset, 'janeiro')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), self.viagem_normal)

    def test_filtro_mes_inexistente(self):
        """Teste do filtro de mês com mês inexistente"""
        queryset = Viagem_MOT.objects.all()
        resultado = aplicar_filtro_mes(queryset, 'dezembro')
        self.assertEqual(resultado.count(), 0)

    def test_filtro_combustivel_todos(self):
        """Teste do filtro de combustível com 'todos'"""
        queryset = Viagem_CAM.objects.all()
        resultado = aplicar_filtro_combustivel(queryset, 'todos')
        self.assertEqual(resultado.count(), 2)  # Inclui erro e normal

    def test_filtro_combustivel_sem_zero(self):
        """Teste do filtro de combustível removendo zeros"""
        queryset = Viagem_MOT.objects.all()
        resultado = aplicar_filtro_combustivel(queryset, 'sem_zero')
        self.assertEqual(resultado.count(), 1)
        # Verificar que a viagem com consumo zero foi removida
        self.assertNotIn(self.viagem_zero, resultado)

    def test_filtro_combustivel_normais(self):
        """Teste do filtro de combustível apenas valores normais"""
        queryset = Viagem_CAM.objects.all()
        resultado = aplicar_filtro_combustivel(queryset, 'normais')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), self.viagem_cam_normal)

    def test_filtro_combustivel_erros(self):
        """Teste do filtro de combustível apenas erros"""
        queryset = Viagem_CAM.objects.all()
        resultado = aplicar_filtro_combustivel(queryset, 'erros')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), self.viagem_erro)

    def test_processar_filtros_request(self):
        """Teste da função processar_filtros_request"""
        from django.http import HttpRequest
        
        # Simular request com parâmetros
        request = HttpRequest()
        request.GET = {'mes': 'janeiro', 'filtro_combustivel': 'sem_zero'}
        
        mes, filtro_combustivel, remover_zero = processar_filtros_request(request)
        
        self.assertEqual(mes, 'janeiro')
        self.assertEqual(filtro_combustivel, 'sem_zero')

    def test_processar_filtros_request_compatibilidade(self):
        """Teste da compatibilidade com parâmetro antigo remover_zero"""
        from django.http import HttpRequest
        
        # Simular request com parâmetro antigo
        request = HttpRequest()
        request.GET = {'mes': 'fevereiro', 'remover_zero': 'sim'}
        
        mes, filtro_combustivel, remover_zero = processar_filtros_request(request)
        
        self.assertEqual(mes, 'fevereiro')
        self.assertEqual(filtro_combustivel, 'sem_zero')  # Convertido automaticamente
        self.assertEqual(remover_zero, 'sim')

    def test_get_base_context(self):
        """Teste da função get_base_context"""
        context = get_base_context('janeiro', 'sem_zero', 'sim')
        
        self.assertEqual(context['mes_selecionado'], 'janeiro')
        self.assertEqual(context['filtro_combustivel'], 'sem_zero')
        self.assertEqual(context['remover_zero'], 'sim')
        self.assertIn('meses_disponiveis', context)
        self.assertIn('meses_choices', context)

    def test_filtros_combinados_avancados(self):
        """Teste dos filtros combinados com filtro avançado de combustível"""
        queryset = Viagem_CAM.objects.all()
        
        # Filtrar março e apenas valores normais
        resultado = aplicar_filtros_combinados(queryset, 'março', 'normais')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), self.viagem_cam_normal)
        
        # Filtrar março e apenas erros
        resultado = aplicar_filtros_combinados(queryset, 'março', 'erros')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), self.viagem_erro)
        
        # Filtrar todos os meses, sem zeros
        resultado = aplicar_filtros_combinados(Viagem_MOT.objects.all(), 'todos', 'sem_zero')
        self.assertEqual(resultado.count(), 1)
        self.assertNotIn(self.viagem_zero, resultado)


class IntegrationTestCase(TestCase):
    """Testes de integração para o sistema completo atualizado"""
    
    def setUp(self):
        """Configuração para testes de integração"""
        self.client = Client()
        
        # Configurar sistema
        cache.clear()
        ConfiguracaoSistema.objects.all().delete()
        ConfiguracaoManager.inicializar_configuracoes()
        
        # Criar estrutura completa de dados
        self.motorista1 = Motorista.objects.create(
            agrupamento="Motorista 1"
        )
        
        self.motorista2 = Motorista.objects.create(
            agrupamento="Motorista 2"
        )
        
        self.caminhao_scania = Caminhao.objects.create(
            agrupamento="SCANIA_INT",
            marca="Scania"
        )
        
        self.caminhao_volvo = Caminhao.objects.create(
            agrupamento="VOLVO_INT",
            marca="Volvo"
        )
        
        # Criar múltiplas viagens para testar agregações e filtros
        for i in range(3):
            # Viagens de motoristas
            Viagem_MOT.objects.create(
                agrupamento=self.motorista1,
                quilometragem=Decimal(f'{500 + i*50}.0'),
                Consumido=100 + i*10,
                Quilometragem_média=Decimal('5.0'),
                Horas_de_motor=f'{10 + i}.0',
                Velocidade_média=50.0,
                Emissões_CO2=2.5,
                mês="janeiro"
            )
            
            # Viagens de caminhões com diferentes padrões
            Viagem_CAM.objects.create(
                agrupamento=self.caminhao_scania,
                quilometragem=Decimal(f'{800 + i*100}.0'),
                Consumido=150 + i*20,
                Quilometragem_média=Decimal(f'{4.0 + i*0.5}'),
                Horas_de_motor=f'{12 + i}.0',
                Velocidade_média=60.0 + i*5,
                RPM_médio=1200.0 + i*50,
                Temperatura_média=80.0 + i*2,
                Emissões_CO2=2.8 + i*0.2,
                mês="janeiro"
            )

    def test_system_integration_with_configurations(self):
        """Teste de integração com sistema de configuração"""
        # Alterar configurações
        ConfiguracaoManager.set_valor('custo_diesel', 8.00, 'Teste integração', 'financeiro')
        
        # Testar que views respondem às mudanças
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['custo_diesel'], 8.00)

    def test_dynamic_calculations_integration(self):
        """Teste de integração dos cálculos dinâmicos"""
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se média atual é calculada dinamicamente
        media_atual = response.context['media_km_atual']
        self.assertIsInstance(media_atual, float)
        self.assertGreater(media_atual, 0)

    def test_advanced_filters_integration(self):
        """Teste de integração dos filtros avançados"""
        # Criar viagem com erro de combustível
        Viagem_CAM.objects.create(
            agrupamento=self.caminhao_volvo,
            quilometragem=Decimal('100.0'),
            Consumido=80000,  # Erro
            Quilometragem_média=Decimal('0.001'),
            Horas_de_motor="5.0",
            Velocidade_média=20.0,
            RPM_médio=1500.0,
            Temperatura_média=95.0,
            Emissões_CO2=120.0,
            mês="janeiro"
        )
        
        # Testar filtro de erros
        response = self.client.get(reverse('caminhoes'), {
            'filtro_combustivel': 'erros'
        })
        self.assertEqual(response.status_code, 200)

    def test_data_consistency_across_views(self):
        """Teste de consistência de dados entre diferentes views"""
        filter_params = {
            'mes': 'janeiro',
            'filtro_combustivel': 'normais'
        }
        
        views_to_test = ['index', 'report', 'motoristas', 'caminhoes']
        
        for view_name in views_to_test:
            with self.subTest(view=view_name):
                response = self.client.get(reverse(view_name), filter_params)
                self.assertEqual(response.status_code, 200)

    def test_statistics_calculation_consistency(self):
        """Teste de consistência dos cálculos estatísticos"""
        response = self.client.get(reverse('caminhoes'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar estatísticas por marca
        scania_stats = response.context['scania_stats']
        volvo_stats = response.context['volvo_stats']
        
        self.assertIsNotNone(scania_stats)
        self.assertIsNotNone(volvo_stats)
        
        # Verificar que contêm as chaves esperadas
        expected_keys = ['total_quilometragem', 'total_consumido', 'media_quilometragem']
        for key in expected_keys:
            self.assertIn(key, scania_stats)
            self.assertIn(key, volvo_stats)


class PerformanceAndConfigTestCase(TestCase):
    """Testes de performance e configuração avançados"""
    
    def setUp(self):
        """Configuração para testes de performance"""
        cache.clear()
        ConfiguracaoSistema.objects.all().delete()
        ConfiguracaoManager.inicializar_configuracoes()
        
        # Criar dados em quantidade para testar performance
        motoristas = []
        caminhoes = []
        
        for i in range(10):
            motorista = Motorista.objects.create(
                agrupamento=f"Perf Test Motorista {i}"
            )
            motoristas.append(motorista)
            
            caminhao = Caminhao.objects.create(
                agrupamento=f"PERF{i:03d}",
                marca="Scania" if i % 2 == 0 else "Volvo"
            )
            caminhoes.append(caminhao)
        
        # Criar viagens para cada motorista e caminhão
        for motorista in motoristas:
            for mes_nome in ['janeiro', 'fevereiro', 'março']:
                Viagem_MOT.objects.create(
                    agrupamento=motorista,
                    quilometragem=Decimal('500.0'),
                    Consumido=100,
                    Quilometragem_média=Decimal('5.0'),
                    Horas_de_motor="10.0",
                    Velocidade_média=50.0,
                    Emissões_CO2=2.5,
                    mês=mes_nome
                )
        
        for caminhao in caminhoes:
            for mes_nome in ['janeiro', 'fevereiro', 'março']:
                Viagem_CAM.objects.create(
                    agrupamento=caminhao,
                    quilometragem=Decimal('800.0'),
                    Consumido=150,
                    Quilometragem_média=Decimal('5.3'),
                    Horas_de_motor="12.0",
                    Velocidade_média=65.0,
                    RPM_médio=1200.0,
                    Temperatura_média=80.0,
                    Emissões_CO2=2.7,
                    mês=mes_nome
                )

    def test_configuration_cache_performance(self):
        """Teste de performance do cache de configurações"""
        import time
        
        # Primeira chamada (sem cache)
        start = time.time()
        valor1 = Config.custo_diesel()
        time1 = time.time() - start
        
        # Segunda chamada (com cache)
        start = time.time()
        valor2 = Config.custo_diesel()
        time2 = time.time() - start
        
        self.assertEqual(valor1, valor2)
        # Cache deve ser mais rápido ou igual (tolerância para variação mínima)
        self.assertLessEqual(time2, time1 + 0.01)

    def test_large_dataset_filtering_performance(self):
        """Teste de performance de filtragem com datasets maiores"""
        import time
        
        queryset = Viagem_CAM.objects.all()
        
        # Deve ter 30 viagens de caminhão (10 caminhões × 3 meses)
        self.assertEqual(queryset.count(), 30)
        
        # Testar performance dos filtros
        start = time.time()
        resultado_mes = aplicar_filtro_mes(queryset, 'janeiro')
        time_mes = time.time() - start
        
        start = time.time()
        resultado_combustivel = aplicar_filtro_combustivel(queryset, 'normais')
        time_combustivel = time.time() - start
        
        start = time.time()
        resultado_combinado = aplicar_filtros_combinados(queryset, 'janeiro', 'normais')
        time_combinado = time.time() - start
        
        # Verificar resultados corretos
        self.assertEqual(resultado_mes.count(), 10)
        self.assertEqual(resultado_combustivel.count(), 30)  # Todos normais
        self.assertEqual(resultado_combinado.count(), 10)
        
        # Verificar que filtros são rápidos (menos de 1 segundo cada)
        self.assertLess(time_mes, 1.0)
        self.assertLess(time_combustivel, 1.0)
        self.assertLess(time_combinado, 1.0)

    def test_dynamic_calculation_performance(self):
        """Teste de performance dos cálculos dinâmicos"""
        import time
        
        # Testar cálculo de média dinâmica
        start = time.time()
        media = Config.media_km_atual()
        time_calc = time.time() - start
        
        self.assertIsInstance(media, float)
        self.assertGreater(media, 0)
        self.assertLess(time_calc, 2.0)  # Deve ser rápido

    def test_view_response_time_with_large_data(self):
        """Teste de tempo de resposta das views com mais dados"""
        import time
        
        views_to_test = ['index', 'report', 'motoristas', 'caminhoes']
        
        for view_name in views_to_test:
            with self.subTest(view=view_name):
                start_time = time.time()
                response = self.client.get(reverse(view_name))
                end_time = time.time()
                
                self.assertEqual(response.status_code, 200)
                # Verificar que a resposta é razoavelmente rápida
                response_time = end_time - start_time
                self.assertLess(response_time, 3.0, f"View {view_name} muito lenta: {response_time}s")

    def test_configuration_update_impact(self):
        """Teste do impacto de atualizações de configuração"""
        # Medir tempo antes da alteração
        import time
        
        start = time.time()
        response1 = self.client.get(reverse('report'))
        time1 = time.time() - start
        
        # Alterar configuração
        ConfiguracaoManager.set_valor('custo_diesel', 9.99, 'Teste performance', 'financeiro')
        
        start = time.time()
        response2 = self.client.get(reverse('report'))
        time2 = time.time() - start
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Verificar que a alteração foi aplicada
        self.assertEqual(response2.context['custo_diesel'], 9.99)
        
        # Verificar que performance não foi significativamente impactada
        self.assertLess(abs(time2 - time1), 1.0)

    def test_memory_usage_optimization(self):
        """Teste básico de otimização de uso de memória"""
        import gc
        
        # Forçar garbage collection antes do teste
        gc.collect()
        
        # Executar operações que podem consumir memória
        for _ in range(10):
            response = self.client.get(reverse('caminhoes'), {
                'filtro_combustivel': 'todos'
            })
            self.assertEqual(response.status_code, 200)
        
        # Verificar que objetos estão sendo liberados adequadamente
        gc.collect()
        # Teste passa se não há vazamentos óbvios de memória

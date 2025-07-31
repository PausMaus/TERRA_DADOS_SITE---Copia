from django.db.models import F, Avg, Sum, Q, Count, Max, Min
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import (
    Motorista, Caminhao, Viagem_MOT, Viagem_CAM,
    Empresa, Unidade, Viagem_Base
)
from .config import Config, ConfiguracaoManager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Constantes para meses
MESES_CHOICES = [
    ('todos', 'Todos os Meses'),
    ('janeiro', 'Janeiro'),
    ('fevereiro', 'Fevereiro'),
    ('março', 'Março'),
    ('abril', 'Abril'),
    ('maio', 'Maio'),
    ('junho', 'Junho'),
    ('julho', 'Julho'),
    ('agosto', 'Agosto'),
    ('setembro', 'Setembro'),
    ('outubro', 'Outubro'),
    ('novembro', 'Novembro'),
    ('dezembro', 'Dezembro'),
]

# ========== FUNÇÕES AUXILIARES PARA NOVO SISTEMA ==========

def get_empresas_disponiveis():
    """Retorna lista de empresas disponíveis no sistema"""
    return Empresa.objects.all().order_by('nome')

def get_marcas_por_empresa(empresa_id=None):
    """Retorna lista de marcas disponíveis para uma empresa específica"""
    if empresa_id and empresa_id != 'todas':
        return Unidade.objects.filter(empresa_id=empresa_id).values_list('marca', flat=True).distinct().order_by('marca')
    return Unidade.objects.values_list('marca', flat=True).distinct().order_by('marca')

def get_periodos_disponiveis():
    """Retorna lista de períodos disponíveis nos dados unificados"""
    return Viagem_Base.objects.values_list('período', flat=True).distinct().order_by('período')

def aplicar_filtro_empresa(queryset, empresa_selecionada):
    """Aplica filtro de empresa no queryset de Viagem_Base"""
    if empresa_selecionada and empresa_selecionada != 'todas':
        return queryset.filter(unidade__empresa_id=empresa_selecionada)
    return queryset

def aplicar_filtro_marca_novo(queryset, marca_selecionada):
    """Aplica filtro de marca no queryset de Viagem_Base"""
    if marca_selecionada and marca_selecionada != 'todas':
        return queryset.filter(unidade__marca__icontains=marca_selecionada)
    return queryset

def aplicar_filtro_periodo(queryset, periodo_selecionado):
    """Aplica filtro de período no queryset de Viagem_Base"""
    if periodo_selecionado and periodo_selecionado != 'todos':
        return queryset.filter(período__iexact=periodo_selecionado)
    return queryset

def aplicar_filtro_combustivel_novo(queryset, filtro_combustivel):
    """Aplica filtro de combustível no queryset de Viagem_Base"""
    if filtro_combustivel == 'sem_zero':
        return queryset.exclude(Consumido=0).exclude(Quilometragem_média=0)
    elif filtro_combustivel == 'normais':
        consumo_max = Config.consumo_maximo_normal()
        return queryset.filter(
            Consumido__gt=0, 
            Consumido__lte=consumo_max,
            Quilometragem_média__gt=0.5,
            Quilometragem_média__lte=3.5
        )
    elif filtro_combustivel == 'erros':
        consumo_limite = Config.consumo_limite_erro()
        return queryset.filter(
            Q(Consumido__gt=consumo_limite) |
            Q(Quilometragem_média__gt=8.0) |
            Q(Quilometragem_média=0) |
            Q(Quilometragem_média__lt=0.5)
        )
    return queryset

def aplicar_filtro_classe_unidade(queryset, classe_selecionada):
    """Aplica filtro de classe de unidade no queryset de Viagem_Base"""
    if classe_selecionada and classe_selecionada != 'todas':
        if classe_selecionada == 'veiculo':
            return queryset.filter(unidade__cls__icontains='veículo')
        elif classe_selecionada == 'motorista':
            return queryset.filter(unidade__cls__icontains='motorista')
    return queryset

def aplicar_filtros_combinados_novo(queryset, empresa_selecionada, marca_selecionada, periodo_selecionado, filtro_combustivel, classe_selecionada=None):
    """Aplica todos os filtros no queryset de Viagem_Base"""
    queryset = aplicar_filtro_empresa(queryset, empresa_selecionada)
    queryset = aplicar_filtro_marca_novo(queryset, marca_selecionada)
    queryset = aplicar_filtro_periodo(queryset, periodo_selecionado)
    queryset = aplicar_filtro_combustivel_novo(queryset, filtro_combustivel)
    if classe_selecionada:
        queryset = aplicar_filtro_classe_unidade(queryset, classe_selecionada)
    return queryset

def processar_filtros_request_novo(request):
    """Processa filtros da requisição para o novo sistema"""
    empresa_selecionada = request.GET.get('empresa', 'todas')
    marca_selecionada = request.GET.get('marca', 'todas')
    periodo_selecionado = request.GET.get('periodo', 'todos')
    filtro_combustivel = request.GET.get('filtro_combustivel', 'todos')
    classe_selecionada = request.GET.get('classe_unidade', 'todas')
    
    # Manter compatibilidade com parâmetro antigo
    remover_zero = request.GET.get('remover_zero', 'nao')
    if remover_zero == 'sim' and filtro_combustivel == 'todos':
        filtro_combustivel = 'sem_zero'
    
    return empresa_selecionada, marca_selecionada, periodo_selecionado, filtro_combustivel, classe_selecionada, remover_zero

def get_base_context_novo(empresa_selecionada, marca_selecionada, periodo_selecionado, filtro_combustivel, classe_selecionada, remover_zero):
    """Retorna contexto base para o novo sistema"""
    return {
        'empresa_selecionada': empresa_selecionada,
        'empresas_disponiveis': get_empresas_disponiveis(),
        'marca_selecionada': marca_selecionada,
        'marcas_disponiveis': get_marcas_por_empresa(empresa_selecionada),
        'periodo_selecionado': periodo_selecionado,
        'periodos_disponiveis': get_periodos_disponiveis(),
        'filtro_combustivel': filtro_combustivel,
        'classe_selecionada': classe_selecionada,
        'remover_zero': remover_zero,
    }

# ========== FUNÇÕES AUXILIARES PARA SISTEMA ANTIGO ==========

def get_meses_disponiveis():
    """Retorna lista de meses disponíveis nos dados"""
    meses_mot = Viagem_MOT.objects.values_list('mês', flat=True).distinct()
    meses_cam = Viagem_CAM.objects.values_list('mês', flat=True).distinct()
    todos_meses = set(meses_mot) | set(meses_cam)
    return sorted([m for m in todos_meses if m])

def aplicar_filtro_mes(queryset, mes_selecionado):
    """Aplica filtro de mês no queryset"""
    if mes_selecionado and mes_selecionado != 'todos':
        return queryset.filter(mês__iexact=mes_selecionado)
    return queryset

def aplicar_filtro_combustivel(queryset, filtro_combustivel):
    """Aplica filtro de combustível baseado no tipo selecionado usando configuração dinâmica"""
    if filtro_combustivel == 'sem_zero':
        # Remove apenas zeros de consumo E média
        return queryset.exclude(Consumido=0).exclude(Quilometragem_média=0)
    elif filtro_combustivel == 'normais':
        # Valores normais: 
        # - Consumo total: maior que 0 e menor ou igual ao limite configurado
        # - Média de consumo: entre 0.5 e 3.5 km/l (valores realistas para caminhões)
        consumo_max = Config.consumo_maximo_normal()
        return queryset.filter(
            Consumido__gt=0, 
            Consumido__lte=consumo_max,
            Quilometragem_média__gt=0.5,  # Mínimo realista para caminhões
            Quilometragem_média__lte=3.5   # Máximo realista para caminhões
        )
    elif filtro_combustivel == 'erros':
        # Erros de leitura: consumo muito alto OU média muito alta/baixa
        consumo_limite = Config.consumo_limite_erro()
        return queryset.filter(
            Q(Consumido__gt=consumo_limite) |  # Consumo excessivo
            Q(Quilometragem_média__gt=8.0) |   # Média muito alta (suspeita)
            Q(Quilometragem_média=0) |         # Média zero
            Q(Quilometragem_média__lt=0.5)     # Média muito baixa
        )
    else:
        # 'todos' - inclui todos os valores
        return queryset

def aplicar_filtros_combinados(queryset, mes_selecionado, filtro_combustivel):
    """Aplica filtros de mês e combustível no queryset"""
    queryset = aplicar_filtro_mes(queryset, mes_selecionado)
    queryset = aplicar_filtro_combustivel(queryset, filtro_combustivel)
    return queryset

def processar_filtros_request(request):
    """Processa e normaliza filtros da requisição"""
    mes_selecionado = request.GET.get('mes', 'todos')
    filtro_combustivel = request.GET.get('filtro_combustivel', 'todos')
    
    # Manter compatibilidade com parâmetro antigo
    remover_zero = request.GET.get('remover_zero', 'nao')
    if remover_zero == 'sim' and filtro_combustivel == 'todos':
        filtro_combustivel = 'sem_zero'
    
    return mes_selecionado, filtro_combustivel, remover_zero

def get_base_context(mes_selecionado, filtro_combustivel, remover_zero):
    """Retorna contexto base comum a todas as views"""
    return {
        'mes_selecionado': mes_selecionado,
        'meses_disponiveis': get_meses_disponiveis(),
        'meses_choices': MESES_CHOICES,
        'filtro_combustivel': filtro_combustivel,
        'remover_zero': remover_zero,  # Manter compatibilidade
    }




def index(request):
    # This view can be used to render the main page of the application
    mes_selecionado, filtro_combustivel, remover_zero = processar_filtros_request(request)
    context = get_base_context(mes_selecionado, filtro_combustivel, remover_zero)
    return render(request, "umbrella360/index.html", context)

# ========== NOVA VIEW PARA RELATÓRIO UNIFICADO ==========

def report_novo(request):
    """Nova view para relatórios usando dados unificados com suporte a múltiplas empresas"""
    # Obter filtros
    empresa_selecionada, marca_selecionada, periodo_selecionado, filtro_combustivel, classe_selecionada, remover_zero = processar_filtros_request_novo(request)
    
    # Contadores gerais
    total_empresas = Empresa.objects.count()
    total_unidades = Unidade.objects.count()
    
    # Aplicar filtros nas viagens da tabela unificada
    viagens_base = Viagem_Base.objects.select_related('unidade', 'unidade__empresa')
    viagens_filtradas = aplicar_filtros_combinados_novo(
        viagens_base, empresa_selecionada, marca_selecionada, 
        periodo_selecionado, filtro_combustivel, classe_selecionada
    )
    
    # Separar por tipo de unidade (motoristas e veículos)
    viagens_motoristas = viagens_filtradas.filter(unidade__cls__icontains='motorista').order_by('-Quilometragem_média')[:10]
    viagens_veiculos = viagens_filtradas.filter(unidade__cls__icontains='veículo').order_by('-Quilometragem_média')[:10]
    
    # Cálculos agregados
    total_quilometragem = viagens_filtradas.aggregate(total=Sum('quilometragem'))['total'] or 0
    total_emissoes = viagens_filtradas.aggregate(total=Sum('Emissões_CO2'))['total'] or 0
    rpm_medio = viagens_filtradas.aggregate(media=Avg('RPM_médio'))['media'] or 0
    velocidade_media = viagens_filtradas.aggregate(media=Avg('Velocidade_média'))['media'] or 0
    
    # Consumo com limite configurável
    consumo_max_normal = Config.consumo_maximo_normal()
    total_consumo = viagens_filtradas.filter(Consumido__lte=consumo_max_normal).aggregate(total=Sum('Consumido'))['total'] or 0
    
    # Calculadora de custos
    custo_diesel = Config.custo_diesel()
    
    # Calcular média real de eficiência dos dados filtrados
    media_km_atual_calculada = viagens_filtradas.filter(
        Consumido__gt=0, Consumido__lte=consumo_max_normal
    ).aggregate(media=Avg('Quilometragem_média'))['media']
    
    media_km_atual = float(media_km_atual_calculada) if media_km_atual_calculada and media_km_atual_calculada > 0 else Config.media_km_atual()
    media_km_objetivo = Config.media_km_objetivo()
    
    # Cálculos de economia
    km_atual_litros = float(total_quilometragem) / media_km_atual if media_km_atual > 0 else 0
    km_objetivo_litros = float(total_quilometragem) / media_km_objetivo if media_km_objetivo > 0 else 0
    
    custo_atual = km_atual_litros * custo_diesel
    custo_objetivo = km_objetivo_litros * custo_diesel
    economia_potencial = custo_atual - custo_objetivo
    
    # Estatísticas por marca (dinâmicas baseadas nos dados filtrados)
    marcas_stats = {}
    marcas_disponiveis = viagens_filtradas.values_list('unidade__marca', flat=True).distinct()
    
    for marca in marcas_disponiveis:
        if marca:  # Evitar valores None
            stats = calcular_stats_marca_novo(viagens_filtradas, marca)
            stats['marca'] = marca
            marcas_stats[marca] = stats
    
    # Estatísticas por empresa
    empresas_stats = {}
    if empresa_selecionada == 'todas':
        empresas_disponiveis = viagens_filtradas.values_list('unidade__empresa__nome', flat=True).distinct()
        for empresa_nome in empresas_disponiveis:
            if empresa_nome:
                stats = calcular_stats_empresa(viagens_filtradas, empresa_nome)
                stats['nome'] = empresa_nome
                empresas_stats[empresa_nome] = stats
    
    # Aplicar filtros na busca de unidades
    unidades_filtradas = Unidade.objects.select_related('empresa').all()
    if empresa_selecionada != 'todas':
        unidades_filtradas = unidades_filtradas.filter(empresa_id=empresa_selecionada)
    if classe_selecionada != 'todas':
        if classe_selecionada == 'veiculo':
            unidades_filtradas = unidades_filtradas.filter(cls__icontains='veículo')
        elif classe_selecionada == 'motorista':
            unidades_filtradas = unidades_filtradas.filter(cls__icontains='motorista')
    
    todas_unidades = []
    for unidade in unidades_filtradas.order_by('empresa__nome', 'cls', 'id'):
        # Buscar estatísticas da unidade
        viagens_unidade = Viagem_Base.objects.filter(unidade=unidade)
        
        stats = viagens_unidade.aggregate(
            total_viagens=Count('id'),
            eficiencia_media=Avg('Quilometragem_média'),
            ultima_viagem_periodo=Max('período')
        )
        
        # Buscar a última viagem completa
        ultima_viagem = viagens_unidade.order_by('-período').first()
        
        # Adicionar dados calculados à unidade
        unidade.total_viagens = stats['total_viagens'] or 0
        unidade.eficiencia_media = stats['eficiencia_media']
        unidade.ultima_viagem = ultima_viagem
        
        todas_unidades.append(unidade)
    
    context = get_base_context_novo(empresa_selecionada, marca_selecionada, periodo_selecionado, filtro_combustivel, classe_selecionada, remover_zero)
    context.update({
        'viagens_motoristas': viagens_motoristas,
        'viagens_veiculos': viagens_veiculos,
        'marcas_stats': marcas_stats,
        'empresas_stats': empresas_stats,
        'todas_unidades': todas_unidades,
        'total_empresas': total_empresas,
        'total_unidades': total_unidades,
        'total_quilometragem': total_quilometragem,
        'total_consumo': total_consumo,
        'total_emissoes': total_emissoes,
        'rpm_medio': rpm_medio,
        'velocidade_media': velocidade_media,
        'custo_diesel': custo_diesel,
        'media_km_objetivo': media_km_objetivo,
        'media_km_atual': media_km_atual,
        'custo_atual': custo_atual,
        'custo_objetivo': custo_objetivo,
        'economia_potencial': economia_potencial,
    })
    
    return render(request, 'umbrella360/report_novo.html', context)

def lista_unidades(request):
    """View simples para listar todas as unidades do sistema"""
    # Buscar todas as unidades sem filtros
    todas_unidades = obter_unidades_com_stats(None)
    
    # Contadores básicos
    total_unidades = len(todas_unidades)
    total_empresas = Empresa.objects.count()
    motoristas_count = len([u for u in todas_unidades if u.cls == 'Motorista'])
    veiculos_count = len([u for u in todas_unidades if u.cls == 'Veículo'])

    context = {
        'todas_unidades': todas_unidades,
        'total_unidades': total_unidades,
        'total_empresas': total_empresas,
        'motoristas_count': motoristas_count,
        'veiculos_count': veiculos_count,
    }
    
    return render(request, 'umbrella360/lista_unidades.html', context)

# ========== APIs PARA FILTROS DINÂMICOS ==========

def api_marcas_todas(request):
    """API que retorna todas as marcas disponíveis"""
    from django.http import JsonResponse
    marcas = list(Unidade.objects.values_list('marca', flat=True).distinct())
    marcas = [marca for marca in marcas if marca]  # Remove valores None
    return JsonResponse(marcas, safe=False)

def api_marcas_por_empresa(request, empresa_id):
    """API que retorna marcas disponíveis para uma empresa específica"""
    from django.http import JsonResponse
    marcas = list(Unidade.objects.filter(empresa_id=empresa_id).values_list('marca', flat=True).distinct())
    marcas = [marca for marca in marcas if marca]  # Remove valores None
    return JsonResponse(marcas, safe=False)





#view to show all Motoristas and Caminhoes organized by highest media_consumo
def report(request):
    # Obter filtros
    mes_selecionado, filtro_combustivel, remover_zero = processar_filtros_request(request)
    
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()

    # Aplicar filtros nas viagens
    viagens_motoristas_base = Viagem_MOT.objects.select_related('agrupamento')
    viagens_caminhoes_base = Viagem_CAM.objects.select_related('agrupamento')
    
    viagens_motoristas_filtradas = aplicar_filtros_combinados(viagens_motoristas_base, mes_selecionado, filtro_combustivel)
    viagens_caminhoes_filtradas = aplicar_filtros_combinados(viagens_caminhoes_base, mes_selecionado, filtro_combustivel)

    # Get top 5 viagens de motoristas e caminhões ordenadas por média de consumo
    viagens_motoristas = viagens_motoristas_filtradas.order_by('-Quilometragem_média')[:5]
    viagens_caminhoes = viagens_caminhoes_filtradas.order_by('-Quilometragem_média')[:5]

    # Cálculos com base nas viagens de caminhões filtradas
    total_quilometragem_caminhoes = viagens_caminhoes_filtradas.aggregate(total=Sum('quilometragem'))['total']

    total_emissoes_caminhoes = viagens_caminhoes_filtradas.aggregate(total=Sum('Emissões_CO2'))['total']
    rpm_medio_caminhoes = viagens_caminhoes_filtradas.aggregate(media=Avg('RPM_médio'))['media']
    velocidade_media_caminhoes = viagens_caminhoes_filtradas.aggregate(media=Avg('Velocidade_média'))['media']


    
    # Usar limite de consumo configurável
    consumo_max_normal = Config.consumo_maximo_normal()
    total_consumo_caminhoes = viagens_caminhoes_filtradas.filter(Consumido__lte=consumo_max_normal).aggregate(total=Sum('Consumido'))['total']

    # Calculadora Monetária
    custo_diesel = Config.custo_diesel()
    
    # Calcular média real de quilometragem por litro dos dados filtrados
    media_km_atual_calculada = viagens_caminhoes_filtradas.filter(Consumido__gt=0, Consumido__lte=consumo_max_normal).aggregate(
        media=Avg('Quilometragem_média')
    )['media']
    
    # Usar média calculada dinamicamente, ou obter da configuração como fallback
    media_km_atual = float(media_km_atual_calculada) if media_km_atual_calculada and media_km_atual_calculada > 0 else Config.media_km_atual()
    media_km_fixa = Config.media_km_objetivo()
    
    # Cálculos de economia
    km = float(total_quilometragem_caminhoes) if total_quilometragem_caminhoes is not None else 0.0
    km_objetivo = km / media_km_fixa if media_km_fixa > 0 else 0.0
    km_atual = km / media_km_atual if media_km_atual > 0 else 0.0
    
    custo_objetivo = km_objetivo * custo_diesel
    custo_atual = km_atual * custo_diesel
    economia_potencial = custo_atual - custo_objetivo

    
    # Get aggregated data by brand (através das viagens filtradas)
    scania_stats = calcular_stats_marca(viagens_caminhoes_filtradas, 'Scania')
    volvo_stats = calcular_stats_marca(viagens_caminhoes_filtradas, 'Volvo')
    
    # Add brand name to the stats dictionaries
    scania_stats['marca'] = 'Scania'
    volvo_stats['marca'] = 'Volvo'
    
    context = get_base_context(mes_selecionado, filtro_combustivel, remover_zero)
    context.update({
        'viagens_motoristas': viagens_motoristas,
        'viagens_caminhoes': viagens_caminhoes,
        'scania_stats': scania_stats,
        'volvo_stats': volvo_stats,
        'total_motoristas': total_motoristas,
        'total_caminhoes': total_caminhoes,
        'total_quilometragem_caminhoes': total_quilometragem_caminhoes,
        'total_consumo_caminhoes': total_consumo_caminhoes,
        'custo_diesel': custo_diesel,
        'media_km_fixa': media_km_fixa,
        'media_km_atual': media_km_atual,
        'km_objetivo': km_objetivo,
        'custo_objetivo': custo_objetivo,
        'custo_atual': custo_atual,
        'km_atual': km_atual,
        'economia_potencial': economia_potencial,
        'emissoes_caminhoes': total_emissoes_caminhoes,
        'rpm_medio_caminhoes': rpm_medio_caminhoes,
        'velocidade_media_caminhoes': velocidade_media_caminhoes,
    })

    return render(request, 'umbrella360/report.html', context)


def motoristas(request):
    # Obter filtros
    mes_selecionado, filtro_combustivel, remover_zero = processar_filtros_request(request)
    
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()
    
    # Aplicar filtros nas viagens de motoristas
    viagens_motoristas_base = Viagem_MOT.objects.select_related('agrupamento')
    viagens_motoristas = aplicar_filtros_combinados(viagens_motoristas_base, mes_selecionado, filtro_combustivel).order_by('-Quilometragem_média')
    
    context = get_base_context(mes_selecionado, filtro_combustivel, remover_zero)
    context.update({
        'viagens_motoristas': viagens_motoristas, 
        'total_motoristas': total_motoristas, 
        'total_caminhoes': total_caminhoes,
    })
    
    return render(request, 'umbrella360/motoristas.html', context)


def caminhoes(request):
    # Obter filtros
    mes_selecionado, filtro_combustivel, remover_zero = processar_filtros_request(request)
    
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()
    
    # Aplicar filtros nas viagens de caminhões
    viagens_caminhoes_base = Viagem_CAM.objects.select_related('agrupamento')
    viagens_caminhoes_filtradas = aplicar_filtros_combinados(viagens_caminhoes_base, mes_selecionado, filtro_combustivel)
    viagens_caminhoes = viagens_caminhoes_filtradas.order_by('-Quilometragem_média')
    
    # Calculate statistics for each brand dynamically usando viagens filtradas
    scania_stats = calcular_stats_marca(viagens_caminhoes_filtradas, 'Scania')
    volvo_stats = calcular_stats_marca(viagens_caminhoes_filtradas, 'Volvo')
    
    # Count vehicles by brand
    scania_count = Caminhao.objects.filter(marca='Scania').count()
    volvo_count = Caminhao.objects.filter(marca='Volvo').count()
    
    # Add brand name and vehicle count to the stats dictionaries
    scania_stats['marca'] = 'Scania'
    scania_stats['count_veiculos'] = scania_count
    volvo_stats['marca'] = 'Volvo'
    volvo_stats['count_veiculos'] = volvo_count

    # Generate emissions chart usando dados das viagens filtradas
    dados = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Emissões_CO2')
    df = pd.DataFrame(dados)
    
    if not df.empty:
        df = df.groupby('agrupamento__marca', as_index=False).sum()
        df.columns = ['marca', 'Emissões_CO2']

        fig = px.pie(df, names='marca', values='Emissões_CO2',
                     title='',  # Remove title since we'll add it in HTML
                     hole=0.4)  # Donut style chart
        
        # Update layout to make it smaller and change background color
        fig.update_layout(
            width=350,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='lightblue',  # Light blue background
            plot_bgcolor='lightblue',   # Light blue plot area
            font=dict(size=10)
        )

        chart = fig.to_html(full_html=False)
    else:
        chart = '<p>Sem dados disponíveis para o mês selecionado.</p>'

    context = get_base_context(mes_selecionado, filtro_combustivel, remover_zero)
    context.update({
        'viagens_caminhoes': viagens_caminhoes, 
        'total_motoristas': total_motoristas, 
        'total_caminhoes': total_caminhoes,
        'scania_stats': scania_stats,
        'volvo_stats': volvo_stats,
        'grafico': chart,
    })

    return render(request, 'umbrella360/caminhoes.html', context)


def calculo(request):
    # This view can be used to perform calculations or display results
    caminhoes_scania = Caminhao.objects.filter(marca='Scania')
    caminhoes_volvo = Caminhao.objects.filter(marca='Volvo')
    return render(request, "umbrella360/report.html", {'caminhoes_scania': caminhoes_scania, 'caminhoes_volvo': caminhoes_volvo})


def scania(request):
    # This view can be used to display Scania specific calculations or data
    caminhoes_scania = Caminhao.objects.filter(marca='Scania')
    return render(request, "umbrella360/scania.html", {'caminhoes_scania': caminhoes_scania})

def volvo(request):
    # This view can be used to display Volvo specific calculations or data
    caminhoes_volvo = Caminhao.objects.filter(marca='Volvo')
    return render(request, "umbrella360/volvo.html", {'caminhoes_volvo': caminhoes_volvo})




def grafico_emissoes_por_marca(request):
    # Obter filtros
    mes_selecionado, filtro_combustivel, remover_zero = processar_filtros_request(request)
    
    # Aplicar filtros nas viagens
    viagens_caminhoes_base = Viagem_CAM.objects.select_related('agrupamento')
    viagens_caminhoes_filtradas = aplicar_filtros_combinados(viagens_caminhoes_base, mes_selecionado, filtro_combustivel)
    
    # Gráfico 1: Emissões de CO2 por Marca (Pizza) - usando dados das viagens filtradas
    dados_emissoes = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Emissões_CO2')
    df_emissoes = pd.DataFrame(dados_emissoes)
    
    if not df_emissoes.empty:
        df_emissoes = df_emissoes.groupby('agrupamento__marca', as_index=False).sum()
        df_emissoes.columns = ['marca', 'Emissões_CO2']

        grafico_emissoes = px.pie(df_emissoes, names='marca', values='Emissões_CO2',
                     title='Distribuição das Emissões de CO₂ por Marca',
                     hole=0.4,
                     color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
    else:
        grafico_emissoes = go.Figure()
        grafico_emissoes.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 2: Consumo de Combustível por Marca (Barras) - usando dados das viagens filtradas
    dados_consumo = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Consumido')
    df_consumo = pd.DataFrame(dados_consumo)
    
    if not df_consumo.empty:
        df_consumo = df_consumo.groupby('agrupamento__marca', as_index=False).sum()
        df_consumo.columns = ['marca', 'Consumido']

        grafico_consumo = px.bar(df_consumo, x='marca', y='Consumido',
                               title='Consumo Total de Combustível por Marca',
                               color='marca',
                               color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
        grafico_consumo.update_layout(showlegend=False)
    else:
        grafico_consumo = go.Figure()
        grafico_consumo.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 3: Eficiência por Marca (Média de Km/L) - usando dados das viagens filtradas
    dados_eficiencia = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Quilometragem_média')
    df_eficiencia = pd.DataFrame(dados_eficiencia)
    
    if not df_eficiencia.empty:
        df_eficiencia = df_eficiencia.groupby('agrupamento__marca', as_index=False).mean()
        df_eficiencia.columns = ['marca', 'Quilometragem_média']

        grafico_eficiencia = px.bar(df_eficiencia, x='marca', y='Quilometragem_média',
                                  title='Eficiência Média por Marca (Km/L)',
                                  color='marca',
                                  color_discrete_sequence=['#FFA726', '#66BB6A'])
        grafico_eficiencia.update_layout(showlegend=False)
    else:
        grafico_eficiencia = go.Figure()
        grafico_eficiencia.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 4: Distribuição de Velocidade Média - usando dados das viagens filtradas
    dados_velocidade = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Velocidade_média')
    df_velocidade = pd.DataFrame(dados_velocidade)
    
    if not df_velocidade.empty:
        df_velocidade.columns = ['marca', 'Velocidade_média']

        grafico_velocidade = px.box(df_velocidade, x='marca', y='Velocidade_média',
                                  title='Distribuição da Velocidade Média por Marca',
                                  color='marca',
                                  color_discrete_sequence=['#AB47BC', '#29B6F6'])
    else:
        grafico_velocidade = go.Figure()
        grafico_velocidade.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 5: RPM Médio por Marca - usando dados das viagens filtradas
    dados_rpm = viagens_caminhoes_filtradas.values('agrupamento__marca', 'RPM_médio')
    df_rpm = pd.DataFrame(dados_rpm)
    
    if not df_rpm.empty:
        df_rpm = df_rpm.groupby('agrupamento__marca', as_index=False).mean()
        df_rpm.columns = ['marca', 'RPM_médio']

        grafico_rpm = px.bar(df_rpm, x='marca', y='RPM_médio',
                            title='RPM Médio por Marca',
                            color='marca',
                            color_discrete_sequence=['#FF7043', '#26A69A'])
        grafico_rpm.update_layout(showlegend=False)
    else:
        grafico_rpm = go.Figure()
        grafico_rpm.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 6: Scatter Plot - Consumo vs Quilometragem - usando dados das viagens filtradas
    dados_scatter = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Consumido', 'quilometragem', 'agrupamento__agrupamento')
    df_scatter = pd.DataFrame(dados_scatter)
    
    if not df_scatter.empty:
        df_scatter.columns = ['marca', 'Consumido', 'quilometragem', 'agrupamento']

        grafico_scatter = px.scatter(df_scatter, x='quilometragem', y='Consumido',
                                   color='marca', size='Consumido',
                                   title='Relação: Quilometragem vs Consumo',
                                   hover_data=['agrupamento'],
                                   color_discrete_sequence=['#E91E63', '#00BCD4'])
    else:
        grafico_scatter = go.Figure()
        grafico_scatter.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 7: Heatmap - Correlação entre Métricas - usando dados das viagens filtradas
    dados_heatmap = viagens_caminhoes_filtradas.values('Consumido', 'quilometragem', 'Velocidade_média', 'RPM_médio', 'Emissões_CO2')
    df_heatmap = pd.DataFrame(dados_heatmap)
    
    if not df_heatmap.empty and len(df_heatmap) > 1:
        # Calcular matriz de correlação
        correlacao = df_heatmap.corr()
        
        grafico_heatmap = go.Figure(data=go.Heatmap(
            z=correlacao.values,
            x=correlacao.columns,
            y=correlacao.columns,
            colorscale='RdYlBu',
            zmid=0,
            text=correlacao.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        grafico_heatmap.update_layout(
            title='Matriz de Correlação entre Métricas',
            xaxis_title='Métricas',
            yaxis_title='Métricas'
        )
    else:
        grafico_heatmap = go.Figure()
        grafico_heatmap.update_layout(title='Sem dados suficientes para correlação')

    # Gráfico 8: Radar Chart - Performance por Marca - usando dados das viagens filtradas
    dados_radar = viagens_caminhoes_filtradas.values('agrupamento__marca', 'Consumido', 'Velocidade_média', 'RPM_médio', 'Quilometragem_média')
    df_radar = pd.DataFrame(dados_radar)
    
    if not df_radar.empty:
        df_radar.columns = ['marca', 'Consumido', 'Velocidade_média', 'RPM_médio', 'Quilometragem_média']
        df_radar_agg = df_radar.groupby('marca').mean()
        
        # Normalizar dados para escala 0-100
        for col in df_radar_agg.columns:
            df_radar_agg[col] = (df_radar_agg[col] / df_radar_agg[col].max()) * 100
        
        grafico_radar = go.Figure()
        
        for marca in df_radar_agg.index:
            grafico_radar.add_trace(go.Scatterpolar(
                r=df_radar_agg.loc[marca].values,
                theta=['Consumo', 'Velocidade', 'RPM', 'Eficiência'],
                fill='toself',
                name=marca,
                line=dict(width=2)
            ))
        
        grafico_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Radar de Performance por Marca"
        )
    else:
        grafico_radar = go.Figure()
        grafico_radar.update_layout(title='Sem dados para o mês selecionado')

    # Gráfico 9: Area Chart - Tendência de Consumo ao Longo do Tempo - usando dados das viagens filtradas
    dados_area = viagens_caminhoes_filtradas.values('agrupamento__marca', 'agrupamento__agrupamento', 'Consumido').order_by('agrupamento__agrupamento')
    df_area = pd.DataFrame(dados_area)
    
    if not df_area.empty:
        df_area.columns = ['marca', 'agrupamento', 'Consumido']
        
        grafico_area = px.area(df_area, x='agrupamento', y='Consumido', color='marca',
                              title='Tendência de Consumo por Agrupamento',
                              color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
    else:
        grafico_area = go.Figure()
        grafico_area.update_layout(title='Sem dados para o mês selecionado')

    # Configurar todos os gráficos com tamanho otimizado
    graficos = [grafico_emissoes, grafico_consumo, grafico_eficiencia, 
                grafico_velocidade, grafico_rpm, grafico_scatter,
                grafico_heatmap, grafico_radar, grafico_area]
    
    for grafico in graficos:
        grafico.update_layout(
            width=500,
            height=350,
            margin=dict(l=40, r=40, t=50, b=40),
            font=dict(size=11),
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(255,255,255,0.95)'
        )

    context = get_base_context(mes_selecionado, filtro_combustivel, remover_zero)
    context.update({
        'grafico_emissoes': grafico_emissoes.to_html(full_html=False),
        'grafico_consumo': grafico_consumo.to_html(full_html=False),
        'grafico_eficiencia': grafico_eficiencia.to_html(full_html=False),
        'grafico_velocidade': grafico_velocidade.to_html(full_html=False),
        'grafico_rpm': grafico_rpm.to_html(full_html=False),
        'grafico_scatter': grafico_scatter.to_html(full_html=False),
        'grafico_heatmap': grafico_heatmap.to_html(full_html=False),
        'grafico_radar': grafico_radar.to_html(full_html=False),
        'grafico_area': grafico_area.to_html(full_html=False),
    })

    return render(request, 'umbrella360/grafico_pizza.html', context)

def calcular_stats_marca(viagens_filtradas, marca):
    """Calcula estatísticas agregadas para uma marca específica"""
    return viagens_filtradas.filter(agrupamento__marca=marca).aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2')
    )

def calcular_stats_marca_novo(viagens_filtradas, marca):
    """Calcula estatísticas agregadas para uma marca específica usando dados unificados"""
    return viagens_filtradas.filter(unidade__marca=marca).aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2')
    )

def calcular_stats_empresa(viagens_filtradas, empresa_nome):
    """Calcula estatísticas agregadas para uma empresa específica"""
    return viagens_filtradas.filter(unidade__empresa__nome=empresa_nome).aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2'),
        total_unidades=Count('unidade', distinct=True)
    )

def obter_unidades_com_stats(empresa_selecionada=None):
    """Obtém todas as unidades com suas estatísticas básicas"""
    # TESTE: Sempre retornar todas as unidades
    unidades_query = Unidade.objects.select_related('empresa').all()
    
    # Comentando filtro temporariamente para teste
    # if empresa_selecionada and empresa_selecionada != 'todas':
    #     unidades_query = unidades_query.filter(empresa_id=empresa_selecionada)
    
    unidades_list = []
    
    for unidade in unidades_query.order_by('empresa__nome', 'cls', 'id'):
        # Buscar estatísticas da unidade
        viagens_unidade = Viagem_Base.objects.filter(unidade=unidade)
        
        stats = viagens_unidade.aggregate(
            total_viagens=Count('id'),
            eficiencia_media=Avg('Quilometragem_média'),
            ultima_viagem_periodo=Max('período')
        )
        
        # Buscar a última viagem completa
        ultima_viagem = viagens_unidade.order_by('-período').first()
        
        # Adicionar dados calculados à unidade
        unidade.total_viagens = stats['total_viagens'] or 0
        unidade.eficiencia_media = stats['eficiencia_media']
        unidade.ultima_viagem = ultima_viagem
        
        unidades_list.append(unidade)
    
    return unidades_list

def detalhes_unidade(request, unidade_id):
    """View para mostrar detalhes completos de uma unidade específica"""
    unidade = get_object_or_404(Unidade, id=unidade_id)
    
    # Obter todas as viagens da unidade
    viagens = Viagem_Base.objects.filter(unidade=unidade).order_by('-período')

    # Calcular estatísticas gerais
    stats_gerais = viagens.aggregate(
        total_viagens=Count('id'),
        total_quilometragem=Sum('quilometragem'),
        total_consumo=Sum('Consumido'),
        media_eficiencia=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2'),
        melhor_eficiencia=Max('Quilometragem_média'),
        pior_eficiencia=Min('Quilometragem_média')
    )
    #estatisticas filtradas
    viagens = Viagem_Base.objects.filter(unidade=unidade).order_by('-período')
    #filtrar viagens pelo período dos "Últimos 30 dias"
    viagens_filtradas = viagens.filter(período="Últimos 30 dias")
    stats_filtrados = viagens_filtradas.aggregate(
        total_viagens=Count('id'),
        total_quilometragem=Sum('quilometragem'),
        total_consumo=Sum('Consumido'),
        media_eficiencia=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2'),
        melhor_eficiencia=Max('Quilometragem_média'),
        pior_eficiencia=Min('Quilometragem_média')
    )


    # Estatísticas por período
    stats_por_periodo = viagens.values('período').annotate(
        viagens_periodo=Count('id'),
        quilometragem_periodo=Sum('quilometragem'),
        consumo_periodo=Sum('Consumido'),
        eficiencia_periodo=Avg('Quilometragem_média')
    ).order_by('-período')
    
    # Calcular custos
    custo_diesel = Config.custo_diesel()
    custo_total = (stats_gerais['total_consumo'] or 0) * custo_diesel
    
    # Comparar com médias do sistema
    media_sistema = Viagem_Base.objects.filter(
        unidade__cls=unidade.cls
    ).aggregate(
        media_eficiencia_sistema=Avg('Quilometragem_média')
    )['media_eficiencia_sistema'] or 0
    
    context = {
        'unidade': unidade,
        'viagens': viagens[:20],  # Últimas 20 viagens
        'stats_gerais': stats_gerais,
        'stats_filtrados': stats_filtrados,
        'stats_por_periodo': stats_por_periodo,
        'custo_total': custo_total,
        'custo_diesel': custo_diesel,
        'media_sistema': media_sistema,
        'total_viagens': viagens.count(),
    }
    
    return render(request, 'umbrella360/detalhes_unidade.html', context)

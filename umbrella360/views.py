from django.db.models import F, Avg
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from .models import Motorista, Caminhao, Viagem_MOT, Viagem_CAM
from .config import Config, ConfiguracaoManager
from django.db.models import Sum
import plotly.express as px
import plotly.graph_objects as go
from django.shortcuts import render
from .models import Caminhao, Viagem_CAM
import pandas as pd

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
        # Remove apenas zeros
        return queryset.exclude(Consumido=0)
    elif filtro_combustivel == 'normais':
        # Valores normais: maior que 0 e menor ou igual ao limite configurado
        consumo_max = Config.consumo_maximo_normal()
        return queryset.filter(Consumido__gt=0, Consumido__lte=consumo_max)
    elif filtro_combustivel == 'erros':
        # Apenas erros de leitura: maior que o limite configurado
        consumo_limite = Config.consumo_limite_erro()
        return queryset.filter(Consumido__gt=consumo_limite)
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

    # Calculadora Monetária - usar custo configurável
    custo_diesel = Config.custo_diesel()

    km = float(total_quilometragem_caminhoes) if total_quilometragem_caminhoes is not None else 0.0
    consumo_total = float(total_consumo_caminhoes) if total_consumo_caminhoes is not None else 0.0
    
    # Calcular média real de quilometragem por litro dos dados filtrados
    media_km_atual_calculada = viagens_caminhoes_filtradas.filter(Consumido__gt=0, Consumido__lte=consumo_max_normal).aggregate(
        media=Avg('Quilometragem_média')
    )['media']
    
    # Usar média calculada dinamicamente, ou obter da configuração como fallback
    if media_km_atual_calculada and media_km_atual_calculada > 0:
        media_km_atual = float(media_km_atual_calculada)
    else:
        media_km_atual = Config.media_km_atual()
    
    # Média de quilometragem objetivo da empresa (valor configurável)
    media_km_fixa = Config.media_km_objetivo()
    
    # Cálculos baseados na quilometragem total
    km_objetivo = km / media_km_fixa if media_km_fixa > 0 else 0.0
    custo_objetivo = km_objetivo * custo_diesel
    
    km_atual = km / media_km_atual if media_km_atual > 0 else 0.0
    custo_atual = km_atual * custo_diesel

    economia_potencial = custo_atual - custo_objetivo
    ##########################################
    #calculadora de emissões
    # carbono = 



    #objetivo_gasto = (total_quilometragem_caminhoes / media_km_fixa) * custo_diesel
    #gasto_atual = total_consumo_caminhoes * media

    
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

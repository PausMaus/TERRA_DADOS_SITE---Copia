from django.db.models import F, Avg
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from .models import Motorista, Caminhao
from django.db.models import Sum
import plotly.express as px
import plotly.graph_objects as go
from django.shortcuts import render
from .models import Caminhao
import pandas as pd




def index(request):
    # This view can be used to render the main page of the application

    return render(request, "umbrella360/index.html")





#view to show all Motoristas and Caminhoes organized by highest media_consumo
def report(request):
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()

    # Get top 5 motoristas and caminhoes by average consumption
    # Note: Adjust the field names according to your model definitions

    #pontos_motoristas = Motorista.Quilometragem_média*Motorista.quilometragem
    motoristas = Motorista.objects.all().order_by('-Quilometragem_média')[:5]
    caminhoes = Caminhao.objects.all().order_by('-Quilometragem_média')[:5]



    #custos gerais
    #calculos
    total_quilometragem_caminhoes = Caminhao.objects.aggregate(total=Sum('quilometragem'))['total']
    total_consumo_caminhoes = Caminhao.objects.filter(Consumido__lte=15000).aggregate(total=Sum('Consumido'))['total']

    #Calculadora Monetaria
    custo_diesel = 5.96
    #change to float division to avoid integer division in Python 3

    km = float(total_quilometragem_caminhoes) if total_quilometragem_caminhoes is not None else 0.0
    media_km_fixa = 1.78
    km_objetivo = km / media_km_fixa
    custo_objetivo = km_objetivo * custo_diesel

    ##########################################
    
    media_km_atual = 1.26
    km_atual = km/ media_km_atual 
    custo_atual = km_atual * custo_diesel


    economia_potencial =custo_atual - custo_objetivo
    ##########################################
    #calculadora de emissões
    # carbono = 



    #objetivo_gasto = (total_quilometragem_caminhoes / media_km_fixa) * custo_diesel
    #gasto_atual = total_consumo_caminhoes * media

    
    # Get aggregated data by brand
    scania_stats = Caminhao.objects.filter(marca='Scania').aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2')
    )
    
    volvo_stats = Caminhao.objects.filter(marca='Volvo').aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2')
    )
    
    # Add brand name to the stats dictionaries
    scania_stats['marca'] = 'Scania'
    volvo_stats['marca'] = 'Volvo'
    
    context = {
        'motoristas': motoristas,
        'caminhoes': caminhoes,
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
        

        #'objetivo_gasto': objetivo_gasto,
    }

    return render(request, 'umbrella360/report.html', context)


def motoristas(request):
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()
    motoristas = Motorista.objects.all().order_by('-Quilometragem_média') # Get top 10 motoristas by average consumption
    # You can also add pagination or filtering here if needed


    return render(request, 'umbrella360/motoristas.html', {'motoristas': motoristas, 'total_motoristas': total_motoristas, 'total_caminhoes': total_caminhoes})


def caminhoes(request):
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()
    caminhoes = Caminhao.objects.all().order_by('-Quilometragem_média')  # Get top 10 caminhões by average consumption
    
    # Calculate statistics for each brand dynamically
    scania_stats = Caminhao.objects.filter(marca='Scania').aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2'),
        count_veiculos=Sum('agrupamento')  # Count of vehicles
    )
    
    volvo_stats = Caminhao.objects.filter(marca='Volvo').aggregate(
        total_quilometragem=Sum('quilometragem'),
        total_consumido=Sum('Consumido'),
        media_quilometragem=Avg('Quilometragem_média'),
        media_velocidade=Avg('Velocidade_média'),
        media_rpm=Avg('RPM_médio'),
        media_temperatura=Avg('Temperatura_média'),
        total_emissoes=Sum('Emissões_CO2'),
        count_veiculos=Sum('agrupamento')  # Count of vehicles
    )
    
    # Count vehicles by brand
    scania_count = Caminhao.objects.filter(marca='Scania').count()
    volvo_count = Caminhao.objects.filter(marca='Volvo').count()
    
    # Add brand name and vehicle count to the stats dictionaries
    scania_stats['marca'] = 'Scania'
    scania_stats['count_veiculos'] = scania_count
    volvo_stats['marca'] = 'Volvo'
    volvo_stats['count_veiculos'] = volvo_count

    # Generate emissions chart
    dados = Caminhao.objects.all().values('marca', 'Emissões_CO2')
    df = pd.DataFrame(dados)
    df = df.groupby('marca', as_index=False).sum()

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

    return render(request, 'umbrella360/caminhoes.html', {
        'caminhoes': caminhoes, 
        'total_motoristas': total_motoristas, 
        'total_caminhoes': total_caminhoes,
        'scania_stats': scania_stats,
        'volvo_stats': volvo_stats,
        'grafico': chart
    })


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
    # Gráfico 1: Emissões de CO2 por Marca (Pizza)
    dados_emissoes = Caminhao.objects.all().values('marca', 'Emissões_CO2')
    df_emissoes = pd.DataFrame(dados_emissoes)
    df_emissoes = df_emissoes.groupby('marca', as_index=False).sum()

    grafico_emissoes = px.pie(df_emissoes, names='marca', values='Emissões_CO2',
                 title='Distribuição das Emissões de CO₂ por Marca',
                 hole=0.4,
                 color_discrete_sequence=['#FF6B6B', '#4ECDC4'])

    # Gráfico 2: Consumo de Combustível por Marca (Barras)
    dados_consumo = Caminhao.objects.all().values('marca', 'Consumido')
    df_consumo = pd.DataFrame(dados_consumo)
    df_consumo = df_consumo.groupby('marca', as_index=False).sum()

    grafico_consumo = px.bar(df_consumo, x='marca', y='Consumido',
                           title='Consumo Total de Combustível por Marca',
                           color='marca',
                           color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
    grafico_consumo.update_layout(showlegend=False)

    # Gráfico 3: Eficiência por Marca (Média de Km/L)
    dados_eficiencia = Caminhao.objects.all().values('marca', 'Quilometragem_média')
    df_eficiencia = pd.DataFrame(dados_eficiencia)
    df_eficiencia = df_eficiencia.groupby('marca', as_index=False).mean()

    grafico_eficiencia = px.bar(df_eficiencia, x='marca', y='Quilometragem_média',
                              title='Eficiência Média por Marca (Km/L)',
                              color='marca',
                              color_discrete_sequence=['#FFA726', '#66BB6A'])
    grafico_eficiencia.update_layout(showlegend=False)

    # Gráfico 4: Distribuição de Velocidade Média
    dados_velocidade = Caminhao.objects.all().values('marca', 'Velocidade_média')
    df_velocidade = pd.DataFrame(dados_velocidade)

    grafico_velocidade = px.box(df_velocidade, x='marca', y='Velocidade_média',
                              title='Distribuição da Velocidade Média por Marca',
                              color='marca',
                              color_discrete_sequence=['#AB47BC', '#29B6F6'])

    # Gráfico 5: RPM Médio por Marca
    dados_rpm = Caminhao.objects.all().values('marca', 'RPM_médio')
    df_rpm = pd.DataFrame(dados_rpm)
    df_rpm = df_rpm.groupby('marca', as_index=False).mean()

    grafico_rpm = px.bar(df_rpm, x='marca', y='RPM_médio',
                        title='RPM Médio por Marca',
                        color='marca',
                        color_discrete_sequence=['#FF7043', '#26A69A'])
    grafico_rpm.update_layout(showlegend=False)

    # Gráfico 6: Scatter Plot - Consumo vs Quilometragem
    dados_scatter = Caminhao.objects.all().values('marca', 'Consumido', 'quilometragem', 'agrupamento')
    df_scatter = pd.DataFrame(dados_scatter)

    grafico_scatter = px.scatter(df_scatter, x='quilometragem', y='Consumido',
                               color='marca', size='Consumido',
                               title='Relação: Quilometragem vs Consumo',
                               hover_data=['agrupamento'],
                               color_discrete_sequence=['#E91E63', '#00BCD4'])

    # Gráfico 7: Heatmap - Correlação entre Métricas
    dados_heatmap = Caminhao.objects.all().values('Consumido', 'quilometragem', 'Velocidade_média', 'RPM_médio', 'Emissões_CO2')
    df_heatmap = pd.DataFrame(dados_heatmap)
    
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

    # Gráfico 8: Radar Chart - Performance por Marca
    dados_radar = Caminhao.objects.all().values('marca', 'Consumido', 'Velocidade_média', 'RPM_médio', 'Quilometragem_média')
    df_radar = pd.DataFrame(dados_radar)
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

    # Gráfico 9: Area Chart - Tendência de Consumo ao Longo do Tempo
    dados_area = Caminhao.objects.all().values('marca', 'agrupamento', 'Consumido').order_by('agrupamento')
    df_area = pd.DataFrame(dados_area)
    
    grafico_area = px.area(df_area, x='agrupamento', y='Consumido', color='marca',
                          title='Tendência de Consumo por Agrupamento',
                          color_discrete_sequence=['#FF6B6B', '#4ECDC4'])

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

    context = {
        'grafico_emissoes': grafico_emissoes.to_html(full_html=False),
        'grafico_consumo': grafico_consumo.to_html(full_html=False),
        'grafico_eficiencia': grafico_eficiencia.to_html(full_html=False),
        'grafico_velocidade': grafico_velocidade.to_html(full_html=False),
        'grafico_rpm': grafico_rpm.to_html(full_html=False),
        'grafico_scatter': grafico_scatter.to_html(full_html=False),
        'grafico_heatmap': grafico_heatmap.to_html(full_html=False),
        'grafico_radar': grafico_radar.to_html(full_html=False),
        'grafico_area': grafico_area.to_html(full_html=False),
    }

    return render(request, 'umbrella360/grafico_pizza.html', context)

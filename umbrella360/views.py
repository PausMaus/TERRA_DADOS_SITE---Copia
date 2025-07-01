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
    # You can also add pagination or filtering here if needed

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
    dados = Caminhao.objects.all().values('marca', 'Emissões_CO2')

    # Convertendo para DataFrame para facilitar a agregação
    df = pd.DataFrame(dados)
    df = df.groupby('marca', as_index=False).sum()

    fig = px.pie(df, names='marca', values='Emissões_CO2',
                 title='Distribuição das Emissões de CO₂ por Marca',
                 hole=0.4)  # Deixe como 0 para pizza tradicional, ou 0.4 para estilo donut

    chart = fig.to_html(full_html=False)
    return render(request, 'umbrella360/grafico_pizza.html', {'grafico': chart})

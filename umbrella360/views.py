from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from .models import Motorista, Caminhao, Calculo_Scania, Calculo_Volvo




def index(request):
    # This view can be used to render the main page of the application

    return render(request, "umbrella360/index.html")





#view to show all Motoristas and Caminhoes organized by highest media_consumo
def report(request):
    total_motoristas = Motorista.objects.count()
    total_caminhoes = Caminhao.objects.count()
    motoristas = Motorista.objects.all().order_by('-Quilometragem_média')[:10]
    caminhoes = Caminhao.objects.all().order_by('-Quilometragem_média')[:10]
    calculo_scania = Calculo_Scania.objects.all()
    calculo_volvo = Calculo_Volvo.objects.all()
    context = {
        'motoristas': motoristas,
        'caminhoes': caminhoes,
        'calculo_scania': calculo_scania,
        'calculo_volvo': calculo_volvo,
        'total_motoristas': total_motoristas,
        'total_caminhoes': total_caminhoes,
    }
    return render(request, 'umbrella360/report.html', context)


def motoristas(request):
    motoristas = Motorista.objects.all().order_by('-Quilometragem_média')[:10]  # Get top 10 motoristas by average consumption
    # You can also add pagination or filtering here if needed


    return render(request, 'umbrella360/motoristas.html', {'motoristas': motoristas})


def caminhoes(request):
    caminhoes = Caminhao.objects.all().order_by('-Quilometragem_média')[:10]  # Get top 10 caminhões by average consumption
    # You can also add pagination or filtering here if needed

    return render(request, 'umbrella360/caminhoes.html', {'caminhoes': caminhoes})


def calculo(request):
    # This view can be used to perform calculations or display results
    calculo_scania = Calculo_Scania.objects.all().order_by()
    calculo_volvo = Calculo_Volvo.objects.all()
    return render(request, "umbrella360/report.html", {'calculo_scania': calculo_scania, 'calculo_volvo': calculo_volvo})


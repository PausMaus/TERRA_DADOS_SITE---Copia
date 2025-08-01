from django.shortcuts import render, get_object_or_404
from .models import ItemAcademia, Equipamento, Area, Exercicio

# Create your views here.

def index(request):
    # Buscar a área Cardio
    try:
        area_cardio = Area.objects.get(nome="Cardio")
        equipamentos_cardio = Equipamento.objects.filter(area=area_cardio)
    except Area.DoesNotExist:
        area_cardio = None
        equipamentos_cardio = []
    
    # Buscar a área Musculação
    try:
        area_musculacao = Area.objects.get(nome="Musculação")
        equipamentos_musculacao = Equipamento.objects.filter(area=area_musculacao)
    except Area.DoesNotExist:
        area_musculacao = None
        equipamentos_musculacao = []
    
    # Buscar a área Fitness
    try:
        area_fitness = Area.objects.get(nome="Fitness")
        equipamentos_fitness = Equipamento.objects.filter(area=area_fitness)
    except Area.DoesNotExist:
        area_fitness = None
        equipamentos_fitness = []
    
    context = {
        'area_cardio': area_cardio,
        'equipamentos_cardio': equipamentos_cardio,
        'area_musculacao': area_musculacao,
        'equipamentos_musculacao': equipamentos_musculacao,
        'area_fitness': area_fitness,
        'equipamentos_fitness': equipamentos_fitness,
    }
    return render(request, "academia_virtual/index.html", context)

def detalhe(request, item_id):
    item = get_object_or_404(ItemAcademia, pk=item_id)
    
    # Buscar exercícios relacionados se o item for um equipamento
    exercicios_relacionados = []
    if hasattr(item, 'equipamento'):
        # Se for um equipamento, buscar exercícios que usam este equipamento
        exercicios_relacionados = Exercicio.objects.filter(equipamento=item.equipamento)
    
    context = {
        'item': item,
        'exercicios_relacionados': exercicios_relacionados,
    }
    return render(request, "academia_virtual/detalhe.html", context)
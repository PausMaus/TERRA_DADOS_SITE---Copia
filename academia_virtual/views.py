from django.shortcuts import render, get_object_or_404
from .models import ItemAcademia, Equipamento, Area

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
    
    # Buscar outros itens para os corredores (dividimos entre as três áreas)
    equipamentos_outros = Equipamento.objects.filter(area__isnull=True)
    outros_itens = ItemAcademia.objects.exclude(
        id__in=Equipamento.objects.values_list('itemacademia_ptr_id', flat=True)
    )
    
    # Dividir os itens do corredor entre as seções (terço para cada)
    total_outros = list(equipamentos_outros) + list(outros_itens)
    terco = len(total_outros) // 3
    corredor_cardio = total_outros[:terco] if total_outros else []
    corredor_musculacao = total_outros[terco:terco*2] if total_outros else []
    corredor_fitness = total_outros[terco*2:] if total_outros else []
    
    context = {
        'area_cardio': area_cardio,
        'equipamentos_cardio': equipamentos_cardio,
        'corredor_cardio': corredor_cardio,
        'area_musculacao': area_musculacao,
        'equipamentos_musculacao': equipamentos_musculacao,
        'corredor_musculacao': corredor_musculacao,
        'area_fitness': area_fitness,
        'equipamentos_fitness': equipamentos_fitness,
        'corredor_fitness': corredor_fitness,
    }
    return render(request, "academia_virtual/index.html", context)

def detalhe(request, item_id):
    item = get_object_or_404(ItemAcademia, pk=item_id)
    return render(request, "academia_virtual/detalhe.html", {'item': item})
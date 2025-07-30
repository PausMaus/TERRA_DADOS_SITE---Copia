from django.shortcuts import render, get_object_or_404
from .models import ItemAcademia

# Create your views here.

def index(request):
    itens = ItemAcademia.objects.all()
    return render(request, "academia_virtual/index.html", {'itens': itens})

def detalhe(request, item_id):
    item = get_object_or_404(ItemAcademia, pk=item_id)
    return render(request, "academia_virtual/detalhe.html", {'item': item})
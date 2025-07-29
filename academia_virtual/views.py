from django.shortcuts import render
from .models import ItemAcademia

# Create your views here.

def index(request):
    itens = ItemAcademia.objects.all()
    return render(request, "academia_virtual/index.html", {'itens': itens})
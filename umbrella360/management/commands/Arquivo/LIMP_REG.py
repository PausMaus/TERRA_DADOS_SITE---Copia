
import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Caminhao, Motorista
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Deleta todos os caminhões do banco de dados'
    # Exclui todos os registros existentes

    def handle(self, *args, **kwargs):
        Caminhao.objects.all().delete()
        Motorista.objects.all().delete()

    


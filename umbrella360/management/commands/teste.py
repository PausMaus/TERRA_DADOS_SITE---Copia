import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Viagem_Base, Unidade
import os

class Command(BaseCommand):
    help = 'Importa viagens únicas dos motoristas de um arquivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')


    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']


        if not os.path.isfile(caminho):
            self.stderr.write(f'Arquivo não encontrado: {caminho}')
            return


        df = pd.read_excel(caminho, engine='openpyxl')
        print(df)
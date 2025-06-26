import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Motorista  # ajuste para o nome correto do seu model e app
import os

class Command(BaseCommand):
    help = 'Importa motoristas de um arquivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')

    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']

        if not os.path.isfile(caminho):
            self.stderr.write(f'Arquivo não encontrado: {caminho}')
            return
        
        # Exclui todos os registros existentes
        Motorista.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Todos os motoristas foram deletados com sucesso."))

        try:
            df = pd.read_excel(caminho, engine='openpyxl')
            if 'Motorista' not in df.columns:
                self.stderr.write('A coluna "Motorista" não foi encontrada na planilha.')
                return

            motoristas = [Motorista(nome=linha['Motorista']) for _, linha in df.iterrows()]
            Motorista.objects.bulk_create(motoristas)

            self.stdout.write(self.style.SUCCESS(f'{len(motoristas)} motoristas importados com sucesso!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))
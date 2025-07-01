import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Caminhao
import os

class Command(BaseCommand):
    help = 'Importa caminhões de um arquivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')

    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']

        if not os.path.isfile(caminho):
            self.stderr.write(f'Arquivo não encontrado: {caminho}')
            return
        

        try:
            df = pd.read_excel(caminho, engine='openpyxl')
            # Checagem das colunas necessárias
            required_columns = [
                'Agrupamento',
                'Quilometragem', 
                'Consumido por AbsFCS',
                'Quilometragem média por unidade de combustível por AbsFCS',
                'Horas de motor',
                'Velocidade média',
                'RPM médio do motor',
                'Temperatura média',
                'Emissões de CO2',
                'Marca',



            ]
            for col in required_columns:
                if col not in df.columns:
                    self.stderr.write(f'A coluna "{col}" não foi encontrada na planilha.')
                    return

            caminhoes = [
                Caminhao(
                    agrupamento=str(linha['Agrupamento']),
                    marca=linha['Marca'] if not pd.isna(linha['Marca']) else '',
                    quilometragem=linha['Quilometragem'] if not pd.isna(linha['Quilometragem']) else 0,
                    Consumido=linha['Consumido por AbsFCS'] if not pd.isna(linha['Consumido por AbsFCS']) else 0,
                    Quilometragem_média=linha['Quilometragem média por unidade de combustível por AbsFCS'] if not pd.isna(linha['Quilometragem média por unidade de combustível por AbsFCS']) else 0,
                    Horas_de_motor=linha['Horas de motor'] if not pd.isna(linha['Horas de motor']) else 0,
                    Velocidade_média=linha['Velocidade média'] if not pd.isna(linha['Velocidade média']) else 0,
                    RPM_médio=linha['RPM médio do motor'] if not pd.isna(linha['RPM médio do motor']) else 0,
                    Temperatura_média=linha['Temperatura média'] if not pd.isna(linha['Temperatura média']) else 0,
                    Emissões_CO2=linha['Emissões de CO2'] if not pd.isna(linha['Emissões de CO2']) else 0
                )
                for _, linha in df.iterrows()
            ]
            Caminhao.objects.bulk_create(caminhoes)

            self.stdout.write(self.style.SUCCESS(f'{len(caminhoes)} caminhões importados com sucesso!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))
import os
import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Motorista  # ajuste conforme o nome do seu app/modelo

class Command(BaseCommand):
    help = 'Exclui todos os motoristas e importa novos dados de um arquivo, que pode ser Excel ou CSV'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo a ser importado')

    def handle(self, *args, **kwargs):
        arquivo = kwargs['arquivo']
        
        if not os.path.isfile(arquivo):
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {arquivo}"))
            return
        
        # Exclui todos os registros existentes
        Motorista.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Todos os motoristas foram deletados com sucesso."))

        # Verifica a extensão do arquivo e lê-o utilizando o pandas
        try:
            _, ext = os.path.splitext(arquivo)
            ext = ext.lower()
            if ext == '.csv':
                df = pd.read_csv(arquivo, encoding='utf-8')
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(arquivo, engine='openpyxl')
            else:
                self.stderr.write(self.style.ERROR(f"Extensão {ext} não suportada. Utilize CSV ou Excel."))
                return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao ler o arquivo: {e}"))
            return

        # Renomeia as colunas para que correspondam aos campos do modelo
        df.rename(columns={
            "Motorista": "nome",
            "Quilometragem": "quilometragem_total",
            "Consumido por AbsFCS": "combustivel_total"
        }, inplace=True)

        motoristas = []
        for _, row in df.iterrows():
            try:
                km = float(row["quilometragem_total"])
            except Exception:
                km = 0.0
            try:
                combustivel = float(row["combustivel_total"])
            except Exception:
                combustivel = 0.0

            # Calcula a média de consumo
            media = km / combustivel if combustivel > 0 else 0.0

            motoristas.append(Motorista(
                nome=row["nome"],
                quilometragem_total=km,
                combustivel_total=combustivel,
                media_consumo=media
            ))

        Motorista.objects.bulk_create(motoristas)
        self.stdout.write(self.style.SUCCESS(f"{len(motoristas)} motoristas importados com sucesso!"))
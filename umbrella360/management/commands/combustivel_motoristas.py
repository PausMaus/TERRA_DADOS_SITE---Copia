import os
import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Motorista  # ajuste para o nome correto do seu app/modelo

class Command(BaseCommand):
    help = 'Exclui todos os motoristas e importa novos dados de um arquivo Excel'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel a ser importado')

    def handle(self, *args, **kwargs):
        arquivo = kwargs['arquivo']
        
        if not os.path.isfile(arquivo):
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {arquivo}"))
            return

        # Exclui todos os registros do modelo Motorista
        Motorista.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Todos os motoristas foram deletados com sucesso."))

        try:
            # Lê o arquivo Excel (o pandas assume o cabeçalho na primeira linha)
            df = pd.read_excel(arquivo, engine='openpyxl')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao ler o arquivo: {e}"))
            return

        # Renomeia as colunas para que correspondam aos nomes do seu modelo
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

            # Calcula a média de consumo (caso combustivel seja zero, mantém 0.0)
            media = km / combustivel if combustivel > 0 else 0.0

            motoristas.append(Motorista(
                nome=row["nome"],
                quilometragem_total=km,
                combustivel_total=combustivel,
                media_consumo=media
            ))
        
        Motorista.objects.bulk_create(motoristas)
        self.stdout.write(self.style.SUCCESS(f"{len(motoristas)} motoristas importados com sucesso!"))
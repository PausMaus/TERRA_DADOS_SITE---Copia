import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Viagem_Base, Unidade, Empresa
import os
from decimal import Decimal
import decimal
from django.db import transaction



class Command(BaseCommand):
    help = 'Importa viagens para o modelo Viagem_Base de arquivos Excel (.xlsx)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Caminho para o arquivo Excel',
            required=True
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_path}'))
            return
        
        try:
            # Lê o arquivo Excel
            self.stdout.write(f'Lendo arquivo: {file_path}')
            processamento_df = pd.read_excel(file_path, engine='openpyxl')
            
            # Debug: mostra as colunas presentes no arquivo
            self.stdout.write(f'Colunas encontradas no arquivo: {list(processamento_df.columns)}')
            
            # Verifica se as colunas esperadas estão presentes
            colunas_esperadas = [
                'Agrupamento',
                'Quilometragem', 
                'Consumido por AbsFCS',
                'Quilometragem média por unidade de combustível por AbsFCS',
                'Velocidade média',
                'Emissões de CO2',
                'Período'
            ]
            
            colunas_faltantes = [col for col in colunas_esperadas if col not in processamento_df.columns]
            if colunas_faltantes:
                self.stdout.write(self.style.ERROR(f'Colunas faltantes no arquivo: {", ".join(colunas_faltantes)}'))
                self.stdout.write(self.style.WARNING(f'Colunas disponíveis: {", ".join(processamento_df.columns)}'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Arquivo carregado com sucesso. {len(processamento_df)} registros encontrados.'))
            
            # Chama o método para processar os dados
            self.update_or_create_trip(processamento_df)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler o arquivo: {str(e)}'))

    def update_or_create_trip(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    unidade_instance = Unidade.objects.get(nm=row['Agrupamento'])
                    
                    # Processa os valores numericos
                    quilometragem = self.processar_valor_numerico(row.get('Quilometragem', '0'))
                    consumo = self.processar_valor_numerico(row.get('Consumido por AbsFCS', '0'))
                    km_media = self.processar_valor_numerico(row.get('Quilometragem média por unidade de combustível por AbsFCS', '0'))
                    velocidade_media = self.processar_valor_numerico(row.get('Velocidade média', '0'))
                    co2 = self.processar_valor_numerico(row.get('Emissões de CO2', '0'))

                    try:
                        quilometragem_value = float(quilometragem)
                        consumo_value = float(consumo)
                        km_media_value = float(km_media)
                        velocidade_media_value = float(velocidade_media)
                        co2_value = float(co2)
                    except (ValueError, TypeError):
                        quilometragem_value = 0.00
                        consumo_value = 0.00
                        km_media_value = 0.00
                        velocidade_media_value = 0.00
                        co2_value = 0.00

                    Viagem_Base.objects.update_or_create(
                        unidade=unidade_instance,
                        período=row['Período'],
                        defaults={
                            'quilometragem': quilometragem_value,
                            'Consumido': consumo_value,
                            'Quilometragem_média': km_media_value,
                            'Velocidade_média': velocidade_media_value,
                            'Emissões_CO2': co2_value,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Viagem atualizada ou criada para a unidade {row["Agrupamento"]} no período {row["Período"]} com quilometragem {quilometragem_value}'))
                
                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Agrupamento"]}" não encontrada no banco de dados.'))
                    continue
                    
    def processar_valor_numerico(self, valor_str, unidade='', valor_padrao=0.0):
        """
        Processa valores string para numérico, removendo unidades e tratando casos especiais
        """
        try:
            # Verifica valores nulos ou vazios
            if pd.isna(valor_str) or valor_str == '-----' or valor_str == '' or valor_str is None:
                return Decimal(str(valor_padrao))
            
            # Converte para string se não for
            valor_str = str(valor_str).strip()
            
            # Verifica se é vazio após strip
            if not valor_str:
                return Decimal(str(valor_padrao))
            
            # Remove unidades de medida comuns
            valor_limpo = valor_str.replace(' km', '').replace(' l', '').replace(' km/h', '').replace(' °C', '').replace(' t', '').replace(' g/km', '').replace(' rpm', '')
            valor_limpo = valor_limpo.replace(',', '.').strip()
            
            # Verifica se ainda tem conteúdo válido
            if not valor_limpo or valor_limpo == '.' or valor_limpo == '-':
                return Decimal(str(valor_padrao))
            
            # Remove caracteres não numéricos (exceto ponto e sinal negativo)
            import re
            valor_limpo = re.sub(r'[^\d\.\-]', '', valor_limpo)
            
            # Verifica se o valor resultante é válido
            if not valor_limpo or valor_limpo == '.' or valor_limpo == '-':
                return Decimal(str(valor_padrao))
            
            # Converte para Decimal
            decimal_value = Decimal(valor_limpo)
            return decimal_value
            
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            # Log do erro para debug
            self.stdout.write(self.style.WARNING(f'Erro ao processar valor "{valor_str}": {e}. Usando valor padrão {valor_padrao}'))
            return Decimal(str(valor_padrao))

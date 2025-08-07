import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Viagem_Base, Unidade, Empresa
import os
from decimal import Decimal
import decimal
from django.db import transaction


class Command(BaseCommand):
    help = 'Importa viagens para o modelo Viagem_Base de arquivos Excel (.xlsx) de uma pasta, usando o nome da pasta como período'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help='Caminho para a pasta contendo os arquivos Excel (o nome da pasta será usado como período)',
            required=True
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Caminho para um arquivo Excel específico (use com --periodo)',
            required=False
        )
        parser.add_argument(
            '--periodo',
            type=str,
            help='Período a ser usado (obrigatório apenas quando usar --file)',
            required=False
        )

    def handle(self, *args, **options):
        folder_path = options.get('folder')
        file_path = options.get('file')
        periodo = options.get('periodo')
        
        # Modo 1: Processar uma pasta inteira (novo modo)
        if folder_path:
            self.process_folder(folder_path)
        # Modo 2: Processar um arquivo específico (modo antigo)
        elif file_path and periodo:
            self.process_single_file(file_path, periodo)
        else:
            self.stdout.write(self.style.ERROR('Use --folder para processar uma pasta ou --file e --periodo para um arquivo específico'))
            return

    def process_folder(self, folder_path):
        """Processa todos os arquivos Excel de uma pasta usando o nome da pasta como período"""
        # Verifica se a pasta existe
        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f'Pasta não encontrada: {folder_path}'))
            return
        
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'O caminho especificado não é uma pasta: {folder_path}'))
            return
        
        # Extrai o nome da pasta como período
        periodo = os.path.basename(folder_path.rstrip(os.sep))
        self.stdout.write(self.style.SUCCESS(f'Processando pasta: {folder_path}'))
        self.stdout.write(self.style.SUCCESS(f'Período definido como: {periodo}'))
        
        # Lista todos os arquivos Excel da pasta
        excel_files = []
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(folder_path, file_name))
        
        if not excel_files:
            self.stdout.write(self.style.WARNING(f'Nenhum arquivo Excel encontrado na pasta: {folder_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(excel_files)} arquivo(s) Excel para processar'))
        
        # Processa cada arquivo
        for file_path in excel_files:
            self.stdout.write(f'\n--- Processando arquivo: {os.path.basename(file_path)} ---')
            self.process_single_file(file_path, periodo)

    def process_single_file(self, file_path, periodo):
        """Processa um único arquivo Excel"""
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_path}'))
            return
        
        try:
            # Lê o arquivo Excel - segunda planilha (index 1)
            self.stdout.write(f'Lendo arquivo: {file_path} (segunda planilha)')
            processamento_df = pd.read_excel(file_path, sheet_name=1, engine='openpyxl')
            
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
            ]
            
            colunas_faltantes = [col for col in colunas_esperadas if col not in processamento_df.columns]
            if colunas_faltantes:
                self.stdout.write(self.style.ERROR(f'Colunas faltantes no arquivo: {", ".join(colunas_faltantes)}'))
                self.stdout.write(self.style.WARNING(f'Colunas disponíveis: {", ".join(processamento_df.columns)}'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Arquivo carregado com sucesso. {len(processamento_df)} registros encontrados.'))
            
            # Chama o método para processar os dados
            self.update_or_create_trip(processamento_df, periodo)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler o arquivo: {str(e)}'))

    def update_or_create_trip(self, processamento_df, periodo):
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
                        período=periodo,
                        defaults={
                            'quilometragem': quilometragem_value,
                            'Consumido': consumo_value,
                            'Quilometragem_média': km_media_value,
                            'Velocidade_média': velocidade_media_value,
                            'Emissões_CO2': co2_value,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Viagem atualizada ou criada para a unidade {row["Agrupamento"]} no período {periodo} com quilometragem {quilometragem_value}'))
                
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

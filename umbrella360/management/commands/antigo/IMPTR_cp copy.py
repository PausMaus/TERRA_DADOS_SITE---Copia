import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import CheckPoint, Unidade, Empresa
import os
from decimal import Decimal
import decimal
from django.db import transaction
from datetime import datetime


class Command(BaseCommand):
    help = 'Importa dados de CheckPoint de arquivos Excel (.xlsx) de uma pasta, usando o nome da pasta como período'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help='Caminho para a pasta contendo os arquivos Excel (o nome da pasta será usado como período)',
            required=False
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
            # Lê o arquivo Excel - primeira planilha (index 0)
            self.stdout.write(f'Lendo arquivo: {file_path} (primeira planilha)')
            checkpoint_df = pd.read_excel(file_path, sheet_name=1, engine='openpyxl')
            
            # Debug: mostra as colunas presentes no arquivo
            self.stdout.write(f'Colunas encontradas no arquivo: {list(checkpoint_df.columns)}')
            
            # Verifica se as colunas esperadas estão presentes
            colunas_esperadas = [
                'Agrupamento',
                'Cerca eletrônica', 
                'Hora de entrada',
                'Hora de saída',
                'Duração em',
            ]
            
            colunas_faltantes = [col for col in colunas_esperadas if col not in checkpoint_df.columns]
            if colunas_faltantes:
                self.stdout.write(self.style.ERROR(f'Colunas faltantes no arquivo: {", ".join(colunas_faltantes)}'))
                self.stdout.write(self.style.WARNING(f'Colunas disponíveis: {", ".join(checkpoint_df.columns)}'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Arquivo carregado com sucesso. {len(checkpoint_df)} registros encontrados.'))
            
            # Chama o método para processar os dados
            self.update_or_create_checkpoint(checkpoint_df, periodo)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler o arquivo: {str(e)}'))

    def update_or_create_checkpoint(self, checkpoint_df, periodo):
        if not checkpoint_df.empty:
            for index, row in checkpoint_df.iterrows():
                try:
                    unidade_instance = Unidade.objects.get(nm=row['Agrupamento'])
                    
                    # Processa os valores de data/hora
                    hora_entrada = self.processar_datetime(row.get('Hora de entrada'))
                    hora_saida = self.processar_datetime(row.get('Hora de saída'))
                    duracao = self.processar_duracao(row.get('Duração em', ''))
                    
                    # Processa a cerca eletrônica (texto)
                    cerca_eletronica = str(row.get('Cerca eletrônica', '')).strip()

                    CheckPoint.objects.update_or_create(
                        unidade=unidade_instance,
                        período=periodo,
                        cerca=cerca_eletronica,
                    )
                    self.stdout.write(self.style.SUCCESS(f'CheckPoint atualizado ou criado para a unidade {row["Agrupamento"]} no período {periodo}'))
                
                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Agrupamento"]}" não encontrada no banco de dados.'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao processar linha {index + 1}: {str(e)}'))
                    continue

    def processar_datetime(self, valor_datetime):
        """
        Processa valores de data/hora do Excel
        """
        try:
            if pd.isna(valor_datetime) or valor_datetime == '' or valor_datetime is None:
                return None
            
            # Se já é um datetime do pandas
            if isinstance(valor_datetime, pd.Timestamp):
                return valor_datetime.to_pydatetime()
            
            # Se é string, tenta converter
            if isinstance(valor_datetime, str):
                # Tenta alguns formatos comuns
                formatos = [
                    '%d.%m.%Y %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%d/%m/%Y %H:%M:%S',
                    '%d.%m.%Y %H:%M',
                    '%Y-%m-%d %H:%M',
                    '%d/%m/%Y %H:%M',
                ]
                
                for formato in formatos:
                    try:
                        return datetime.strptime(valor_datetime.strip(), formato)
                    except ValueError:
                        continue
                
                # Se não conseguiu converter, retorna None
                self.stdout.write(self.style.WARNING(f'Formato de data/hora não reconhecido: {valor_datetime}'))
                return None
            
            return None
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao processar data/hora "{valor_datetime}": {e}'))
            return None

    def processar_duracao(self, valor_duracao):
        """
        Processa valores de duração (formato HH:MM:SS ou similar)
        """
        try:
            if pd.isna(valor_duracao) or valor_duracao == '' or valor_duracao is None:
                return '00:00:00'
            
            # Converte para string
            duracao_str = str(valor_duracao).strip()
            
            # Se está vazio após strip
            if not duracao_str:
                return '00:00:00'
            
            # Se já está no formato HH:MM:SS, retorna como está
            if ':' in duracao_str:
                return duracao_str
            
            # Se é um número (minutos), converte para HH:MM:SS
            try:
                minutos = float(duracao_str)
                horas = int(minutos // 60)
                mins = int(minutos % 60)
                return f'{horas:02d}:{mins:02d}:00'
            except ValueError:
                pass
            
            return '00:00:00'
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao processar duração "{valor_duracao}": {e}'))
            return '00:00:00'

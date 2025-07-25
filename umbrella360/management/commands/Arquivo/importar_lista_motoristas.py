import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Motorista  # ajuste para o nome correto do seu model e app
import os

class Command(BaseCommand):
    help = 'Importa motoristas únicos de um arquivo Excel (.xlsx) - evita duplicatas'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Atualiza motoristas existentes em vez de pular'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a importação sem salvar no banco de dados'
        )

    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']
        update_existing = kwargs['update']
        dry_run = kwargs['dry_run']

        if not os.path.isfile(caminho):
            self.stderr.write(f'Arquivo não encontrado: {caminho}')
            return
        
        try:
            # Lê o arquivo Excel
            df = pd.read_excel(caminho, engine='openpyxl')
            
            # Verifica se a coluna existe
            if 'Agrupamento' not in df.columns:
                self.stderr.write('A coluna "Agrupamento" não foi encontrada na planilha.')
                self.stdout.write('Colunas disponíveis: ' + ', '.join(df.columns.tolist()))
                return

            # Remove linhas com valores nulos ou vazios
            df = df.dropna(subset=['Agrupamento'])
            df = df[df['Agrupamento'].str.strip() != '']
            
            # Remove duplicatas do próprio arquivo (mantém a primeira ocorrência)
            df_original_count = len(df)
            df = df.drop_duplicates(subset=['Agrupamento'], keep='first')
            duplicatas_arquivo = df_original_count - len(df)
            
            if duplicatas_arquivo > 0:
                self.stdout.write(
                    self.style.WARNING(f'Removidas {duplicatas_arquivo} duplicatas do arquivo Excel')
                )

            # Lista de agrupamentos únicos do arquivo
            agrupamentos_arquivo = df['Agrupamento'].str.strip().tolist()
            
            # Verifica quais já existem no banco de dados
            agrupamentos_existentes = set(
                Motorista.objects.filter(
                    agrupamento__in=agrupamentos_arquivo
                ).values_list('agrupamento', flat=True)
            )
            
            # Separa motoristas novos dos existentes
            motoristas_novos = []
            motoristas_existentes = []
            
            for agrupamento in agrupamentos_arquivo:
                agrupamento = agrupamento.strip()
                if agrupamento in agrupamentos_existentes:
                    motoristas_existentes.append(agrupamento)
                else:
                    motoristas_novos.append(agrupamento)
            
            # Relatório do que será processado
            self.stdout.write(f'\n📊 RELATÓRIO DE IMPORTAÇÃO:')
            self.stdout.write(f'Total no arquivo (após limpar duplicatas): {len(agrupamentos_arquivo)}')
            self.stdout.write(f'Motoristas novos para importar: {len(motoristas_novos)}')
            self.stdout.write(f'Motoristas já existentes no banco: {len(motoristas_existentes)}')
            
            if duplicatas_arquivo > 0:
                self.stdout.write(f'Duplicatas removidas do arquivo: {duplicatas_arquivo}')
            
            # Mostra alguns exemplos dos motoristas existentes
            if motoristas_existentes:
                self.stdout.write(f'\n⚠️  MOTORISTAS JÁ EXISTENTES (primeiros 5):')
                for mot in motoristas_existentes[:5]:
                    self.stdout.write(f'  - {mot}')
                if len(motoristas_existentes) > 5:
                    self.stdout.write(f'  ... e mais {len(motoristas_existentes) - 5}')
            
            # Modo dry-run - apenas simula
            if dry_run:
                self.stdout.write(f'\n🧪 MODO SIMULAÇÃO (DRY-RUN):')
                self.stdout.write('Nenhum dado foi salvo no banco de dados.')
                if motoristas_novos:
                    self.stdout.write(f'Seriam importados {len(motoristas_novos)} motoristas novos.')
                return
            
            # Importa apenas motoristas novos
            novos_criados = 0
            if motoristas_novos:
                objetos_motoristas = [
                    Motorista(agrupamento=agrupamento) 
                    for agrupamento in motoristas_novos
                ]
                
                Motorista.objects.bulk_create(objetos_motoristas)
                novos_criados = len(objetos_motoristas)
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {novos_criados} motoristas novos importados com sucesso!')
                )
            
            # Atualiza motoristas existentes se solicitado
            atualizados = 0
            if update_existing and motoristas_existentes:
                # Por enquanto, apenas log - você pode adicionar lógica de atualização aqui
                self.stdout.write(
                    self.style.WARNING(f'📝 Modo atualização ativado, mas não há campos adicionais para atualizar.')
                )
                # Exemplo de como atualizar se houvesse outros campos:
                # for agrupamento in motoristas_existentes:
                #     Motorista.objects.filter(agrupamento=agrupamento).update(
                #         campo_extra='novo_valor'
                #     )
                #     atualizados += 1
            
            # Resumo final
            self.stdout.write(f'\n📋 RESUMO FINAL:')
            self.stdout.write(f'✅ Novos importados: {novos_criados}')
            self.stdout.write(f'⚠️  Já existiam: {len(motoristas_existentes)}')
            if atualizados > 0:
                self.stdout.write(f'📝 Atualizados: {atualizados}')
            
            total_banco = Motorista.objects.count()
            self.stdout.write(f'📊 Total no banco agora: {total_banco}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Erro ao importar: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
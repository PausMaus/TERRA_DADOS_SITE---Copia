import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Caminhao
import os

class Command(BaseCommand):
    help = 'Importa caminhões únicos de um arquivo Excel (.xlsx) - evita duplicatas'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Atualiza caminhões existentes em vez de pular'
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
            
            # Verifica se as colunas existem (apenas Agrupamento e Marca são necessárias para Caminhao)
            required_columns = ['Agrupamento', 'Marca']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stderr.write(f'Colunas não encontradas: {", ".join(missing_columns)}')
                self.stdout.write('Colunas disponíveis: ' + ', '.join(df.columns.tolist()))
                return

            # Remove linhas com valores nulos ou vazios nas colunas obrigatórias
            df = df.dropna(subset=required_columns)
            df = df[(df['Agrupamento'].str.strip() != '') & (df['Marca'].str.strip() != '')]
            
            # Remove duplicatas do próprio arquivo (mantém a primeira ocorrência)
            df_original_count = len(df)
            df = df.drop_duplicates(subset=['Agrupamento'], keep='first')
            duplicatas_arquivo = df_original_count - len(df)
            
            if duplicatas_arquivo > 0:
                self.stdout.write(
                    self.style.WARNING(f'Removidas {duplicatas_arquivo} duplicatas do arquivo Excel')
                )

            # Lista de agrupamentos únicos do arquivo
            dados_arquivo = []
            for _, linha in df.iterrows():
                dados_arquivo.append({
                    'agrupamento': str(linha['Agrupamento']).strip(),
                    'marca': str(linha['Marca']).strip()
                })
            
            # Verifica quais já existem no banco de dados
            agrupamentos_arquivo = [item['agrupamento'] for item in dados_arquivo]
            agrupamentos_existentes = set(
                Caminhao.objects.filter(
                    agrupamento__in=agrupamentos_arquivo
                ).values_list('agrupamento', flat=True)
            )
            
            # Separa caminhões novos dos existentes
            caminhoes_novos = []
            caminhoes_existentes = []
            
            for item in dados_arquivo:
                if item['agrupamento'] in agrupamentos_existentes:
                    caminhoes_existentes.append(item)
                else:
                    caminhoes_novos.append(item)
            
            # Relatório do que será processado
            self.stdout.write(f'\n📊 RELATÓRIO DE IMPORTAÇÃO:')
            self.stdout.write(f'Total no arquivo (após limpar duplicatas): {len(dados_arquivo)}')
            self.stdout.write(f'Caminhões novos para importar: {len(caminhoes_novos)}')
            self.stdout.write(f'Caminhões já existentes no banco: {len(caminhoes_existentes)}')
            
            if duplicatas_arquivo > 0:
                self.stdout.write(f'Duplicatas removidas do arquivo: {duplicatas_arquivo}')
            
            # Mostra alguns exemplos dos caminhões existentes
            if caminhoes_existentes:
                self.stdout.write(f'\n⚠️  CAMINHÕES JÁ EXISTENTES (primeiros 5):')
                for cam in caminhoes_existentes[:5]:
                    self.stdout.write(f'  - {cam["agrupamento"]} ({cam["marca"]})')
                if len(caminhoes_existentes) > 5:
                    self.stdout.write(f'  ... e mais {len(caminhoes_existentes) - 5}')
            
            # Modo dry-run - apenas simula
            if dry_run:
                self.stdout.write(f'\n🧪 MODO SIMULAÇÃO (DRY-RUN):')
                self.stdout.write('Nenhum dado foi salvo no banco de dados.')
                if caminhoes_novos:
                    self.stdout.write(f'Seriam importados {len(caminhoes_novos)} caminhões novos.')
                    self.stdout.write('Primeiros 3 que seriam importados:')
                    for cam in caminhoes_novos[:3]:
                        self.stdout.write(f'  - {cam["agrupamento"]} ({cam["marca"]})')
                return
            
            # Importa apenas caminhões novos
            novos_criados = 0
            if caminhoes_novos:
                objetos_caminhoes = [
                    Caminhao(
                        agrupamento=item['agrupamento'],
                        marca=item['marca']
                    ) 
                    for item in caminhoes_novos
                ]
                
                Caminhao.objects.bulk_create(objetos_caminhoes)
                novos_criados = len(objetos_caminhoes)
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {novos_criados} caminhões novos importados com sucesso!')
                )
            
            # Atualiza caminhões existentes se solicitado
            atualizados = 0
            if update_existing and caminhoes_existentes:
                for item in caminhoes_existentes:
                    # Atualiza a marca se for diferente
                    caminhao = Caminhao.objects.get(agrupamento=item['agrupamento'])
                    if caminhao.marca != item['marca']:
                        caminhao.marca = item['marca']
                        caminhao.save()
                        atualizados += 1
                        self.stdout.write(f'📝 Atualizado: {item["agrupamento"]} - nova marca: {item["marca"]}')
                
                if atualizados > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'📝 {atualizados} caminhões atualizados!')
                    )
            
            # Resumo final
            self.stdout.write(f'\n📋 RESUMO FINAL:')
            self.stdout.write(f'✅ Novos importados: {novos_criados}')
            self.stdout.write(f'⚠️  Já existiam: {len(caminhoes_existentes)}')
            if atualizados > 0:
                self.stdout.write(f'📝 Atualizados: {atualizados}')
            
            total_banco = Caminhao.objects.count()
            self.stdout.write(f'📊 Total no banco agora: {total_banco}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Erro ao importar: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
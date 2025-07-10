import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Viagem_MOT, Motorista
import os

class Command(BaseCommand):
    help = 'Importa viagens únicas dos motoristas de um arquivo Excel (.xlsx) - evita duplicatas'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Atualiza viagens existentes em vez de pular'
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
            df = pd.read_excel(caminho, engine='openpyxl')
            
            # Checagem das colunas necessárias
            required_columns = [
                'Agrupamento',
                'Quilometragem', 
                'Consumido por AbsFCS',
                'Quilometragem média por unidade de combustível por AbsFCS',
                'Horas de motor',
                'Velocidade média',
                'Emissões de CO2',
                'Mês'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.stderr.write(f'Colunas não encontradas: {", ".join(missing_columns)}')
                self.stdout.write('Colunas disponíveis: ' + ', '.join(df.columns.tolist()))
                return

            # Remove linhas com valores nulos na coluna Agrupamento
            df = df.dropna(subset=['Agrupamento'])
            df = df[df['Agrupamento'].str.strip() != '']

            # Buscar todos os motoristas existentes
            motoristas_dict = {
                motorista.agrupamento: motorista 
                for motorista in Motorista.objects.all()
            }

            # Verificar motoristas que não existem no banco
            agrupamentos_arquivo = df['Agrupamento'].str.strip().unique()
            motoristas_nao_encontrados = []
            
            for agrupamento in agrupamentos_arquivo:
                if agrupamento not in motoristas_dict:
                    motoristas_nao_encontrados.append(agrupamento)

            if motoristas_nao_encontrados:
                self.stderr.write(f'❌ Motoristas não encontrados no banco de dados:')
                for motorista in motoristas_nao_encontrados[:10]:  # Mostra apenas os primeiros 10
                    self.stderr.write(f'  - {motorista}')
                if len(motoristas_nao_encontrados) > 10:
                    self.stderr.write(f'  ... e mais {len(motoristas_nao_encontrados) - 10}')
                self.stderr.write(f'Total de motoristas não encontrados: {len(motoristas_nao_encontrados)}')
                self.stderr.write('Execute primeiro o comando IMP_L_MOT para importar os motoristas.')
                return

            # Criar objetos de viagem
            viagens_para_criar = []
            viagens_existentes = []
            viagens_com_erro = []

            for _, linha in df.iterrows():
                agrupamento_nome = str(linha['Agrupamento']).strip()
                mes = str(linha['Mês']).strip() if not pd.isna(linha['Mês']) else 'Maio'
                
                # Buscar motorista
                motorista_obj = motoristas_dict.get(agrupamento_nome)
                if not motorista_obj:
                    viagens_com_erro.append(f'{agrupamento_nome} (não encontrado)')
                    continue

                # Verificar se já existe uma viagem para este motorista e mês
                viagem_existente = Viagem_MOT.objects.filter(
                    agrupamento=motorista_obj,
                    mês=mes
                ).first()

                if viagem_existente:
                    viagens_existentes.append(f'{agrupamento_nome} - {mes}')
                    continue

                # Criar nova viagem
                try:
                    viagem = Viagem_MOT(
                        agrupamento=motorista_obj,
                        quilometragem=linha['Quilometragem'] if not pd.isna(linha['Quilometragem']) else 0,
                        Consumido=linha['Consumido por AbsFCS'] if not pd.isna(linha['Consumido por AbsFCS']) else 0,
                        Quilometragem_média=linha['Quilometragem média por unidade de combustível por AbsFCS'] if not pd.isna(linha['Quilometragem média por unidade de combustível por AbsFCS']) else 0,
                        Horas_de_motor=str(linha['Horas de motor']) if not pd.isna(linha['Horas de motor']) else '0',
                        Velocidade_média=linha['Velocidade média'] if not pd.isna(linha['Velocidade média']) else 0,
                        Emissões_CO2=linha['Emissões de CO2'] if not pd.isna(linha['Emissões de CO2']) else 0,
                        mês=mes
                    )
                    viagens_para_criar.append(viagem)
                except Exception as e:
                    viagens_com_erro.append(f'{agrupamento_nome} - {mes} (erro: {e})')

            # Relatório
            self.stdout.write(f'\n📊 RELATÓRIO DE IMPORTAÇÃO:')
            self.stdout.write(f'Total de registros no arquivo: {len(df)}')
            self.stdout.write(f'Viagens novas para importar: {len(viagens_para_criar)}')
            self.stdout.write(f'Viagens já existentes no banco: {len(viagens_existentes)}')
            
            if viagens_com_erro:
                self.stdout.write(f'Viagens com erro: {len(viagens_com_erro)}')
                self.stdout.write('Primeiros erros:')
                for erro in viagens_com_erro[:5]:
                    self.stdout.write(f'  - {erro}')

            if viagens_existentes:
                self.stdout.write(f'\n⚠️  VIAGENS JÁ EXISTENTES (primeiras 5):')
                for viagem in viagens_existentes[:5]:
                    self.stdout.write(f'  - {viagem}')
                if len(viagens_existentes) > 5:
                    self.stdout.write(f'  ... e mais {len(viagens_existentes) - 5}')

            # Dry-run
            if dry_run:
                self.stdout.write(f'\n🧪 MODO SIMULAÇÃO (DRY-RUN):')
                self.stdout.write('Nenhum dado foi salvo no banco de dados.')
                if viagens_para_criar:
                    self.stdout.write(f'Seriam importadas {len(viagens_para_criar)} viagens novas.')
                return

            # Importar viagens novas
            novos_criados = 0
            if viagens_para_criar:
                Viagem_MOT.objects.bulk_create(viagens_para_criar)
                novos_criados = len(viagens_para_criar)
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {novos_criados} viagens novas importadas com sucesso!')
                )

            # Resumo final
            self.stdout.write(f'\n📋 RESUMO FINAL:')
            self.stdout.write(f'✅ Novas importadas: {novos_criados}')
            self.stdout.write(f'⚠️  Já existiam: {len(viagens_existentes)}')
            if viagens_com_erro:
                self.stdout.write(f'❌ Com erro: {len(viagens_com_erro)}')
            
            total_banco = Viagem_MOT.objects.count()
            self.stdout.write(f'📊 Total no banco agora: {total_banco}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Erro ao importar: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
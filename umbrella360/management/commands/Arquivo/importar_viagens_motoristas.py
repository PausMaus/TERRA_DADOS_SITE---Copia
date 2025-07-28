import pandas as pd
from django.core.management.base import BaseCommand
from umbrella360.models import Viagem_Base, Unidade
import os

class Command(BaseCommand):
    help = 'Importa viagens únicas dos motoristas para Viagem_Base - sobrescreve dados existentes para o mesmo período'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho completo para o arquivo Excel')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a importação sem salvar no banco de dados'
        )

    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']
        dry_run = kwargs['dry_run']

        if not os.path.isfile(caminho):
            self.stderr.write(f'❌ Arquivo não encontrado: {caminho}')
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
                'Período'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.stderr.write(f'❌ Colunas não encontradas: {", ".join(missing_columns)}')
                self.stdout.write('📋 Colunas disponíveis: ' + ', '.join(df.columns.tolist()))
                return

            # Remove linhas com valores nulos na coluna Agrupamento
            df = df.dropna(subset=['Agrupamento'])
            df = df[df['Agrupamento'].str.strip() != '']

            self.stdout.write(f'📂 Importando viagens de motoristas')
            self.stdout.write(f'📊 Total de registros no arquivo: {len(df)}')

            # Buscar todas as unidades que são motoristas (classe = 'motorista')
            motoristas_dict = {
                unidade.nm: unidade 
                for unidade in Unidade.objects.filter(cls='motorista')
                if unidade.nm  # Apenas unidades com nome definido
            }

            self.stdout.write(f'👨‍💼 Motoristas encontrados no banco: {len(motoristas_dict)}')

            # Verificar motoristas que não existem no banco
            agrupamentos_arquivo = df['Agrupamento'].str.strip().unique()
            motoristas_nao_encontrados = []
            
            for agrupamento in agrupamentos_arquivo:
                if agrupamento not in motoristas_dict:
                    motoristas_nao_encontrados.append(agrupamento)

            if motoristas_nao_encontrados:
                self.stderr.write(f'⚠️  Motoristas não encontrados no banco de dados:')
                for motorista in motoristas_nao_encontrados[:10]:  # Mostra apenas os primeiros 10
                    self.stderr.write(f'  - {motorista}')
                if len(motoristas_nao_encontrados) > 10:
                    self.stderr.write(f'  ... e mais {len(motoristas_nao_encontrados) - 10}')
                self.stderr.write(f'Total de motoristas não encontrados: {len(motoristas_nao_encontrados)}')
                self.stderr.write('💡 Execute primeiro o comando para importar as unidades de motoristas.')

            # Criar objetos de viagem
            viagens_para_criar = []
            viagens_para_atualizar = []
            viagens_com_erro = []

            for _, linha in df.iterrows():
                agrupamento_nome = str(linha['Agrupamento']).strip()
                periodo = str(linha['Período']).strip() if not pd.isna(linha['Período']) else 'Maio'
                
                # Buscar motorista (unidade)
                motorista_obj = motoristas_dict.get(agrupamento_nome)
                if not motorista_obj:
                    viagens_com_erro.append(f'{agrupamento_nome} (motorista não encontrado)')
                    continue

                # Verificar se já existe uma viagem para este motorista e período
                viagem_existente = Viagem_Base.objects.filter(
                    unidade=motorista_obj,
                    período=periodo
                ).first()

                # Preparar dados da viagem
                try:
                    dados_viagem = {
                        'unidade': motorista_obj,
                        'quilometragem': linha['Quilometragem'] if not pd.isna(linha['Quilometragem']) else 0,
                        'Consumido': linha['Consumido por AbsFCS'] if not pd.isna(linha['Consumido por AbsFCS']) else 0,
                        'Quilometragem_média': linha['Quilometragem média por unidade de combustível por AbsFCS'] if not pd.isna(linha['Quilometragem média por unidade de combustível por AbsFCS']) else 0,
                        'Horas_de_motor': str(linha['Horas de motor']) if not pd.isna(linha['Horas de motor']) else '0',
                        'Velocidade_média': linha['Velocidade média'] if not pd.isna(linha['Velocidade média']) else 0,
                        'Emissões_CO2': linha['Emissões de CO2'] if not pd.isna(linha['Emissões de CO2']) else 0,
                        'período': periodo,
                        'RPM_médio': 0,  # Valor padrão para motoristas
                        'Temperatura_média': 0,  # Valor padrão para motoristas
                    }

                    if viagem_existente:
                        # Atualizar viagem existente (sobrescrever)
                        for campo, valor in dados_viagem.items():
                            if campo != 'unidade':  # Não atualizar a FK
                                setattr(viagem_existente, campo, valor)
                        viagens_para_atualizar.append(viagem_existente)
                    else:
                        # Criar nova viagem
                        viagem = Viagem_Base(**dados_viagem)
                        viagens_para_criar.append(viagem)

                except Exception as e:
                    viagens_com_erro.append(f'{agrupamento_nome} - {periodo} (erro: {e})')

            # Relatório
            self.stdout.write(f'\n📊 RELATÓRIO DE IMPORTAÇÃO - MOTORISTAS:')
            self.stdout.write(f'📄 Total de registros no arquivo: {len(df)}')
            self.stdout.write(f'✅ Viagens novas para criar: {len(viagens_para_criar)}')
            self.stdout.write(f'🔄 Viagens para atualizar (sobrescrever): {len(viagens_para_atualizar)}')
            
            if viagens_com_erro:
                self.stdout.write(f'❌ Viagens com erro: {len(viagens_com_erro)}')
                self.stdout.write('🔍 Primeiros erros:')
                for erro in viagens_com_erro[:5]:
                    self.stdout.write(f'  - {erro}')

            # Dry-run
            if dry_run:
                self.stdout.write(f'\n🧪 MODO SIMULAÇÃO (DRY-RUN):')
                self.stdout.write('Nenhum dado foi salvo no banco de dados.')
                if viagens_para_criar:
                    self.stdout.write(f'Seriam criadas {len(viagens_para_criar)} viagens novas.')
                if viagens_para_atualizar:
                    self.stdout.write(f'Seriam atualizadas {len(viagens_para_atualizar)} viagens existentes.')
                return

            # Importar/atualizar viagens
            novos_criados = 0
            atualizados = 0

            if viagens_para_criar:
                Viagem_Base.objects.bulk_create(viagens_para_criar)
                novos_criados = len(viagens_para_criar)
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {novos_criados} viagens novas de motoristas criadas com sucesso!')
                )

            if viagens_para_atualizar:
                for viagem in viagens_para_atualizar:
                    viagem.save()
                atualizados = len(viagens_para_atualizar)
                self.stdout.write(
                    self.style.SUCCESS(f'🔄 {atualizados} viagens de motoristas atualizadas (sobrescritas)!')
                )

            # Resumo final
            self.stdout.write(f'\n📋 RESUMO FINAL - MOTORISTAS:')
            self.stdout.write(f'✅ Novas criadas: {novos_criados}')
            self.stdout.write(f'🔄 Atualizadas: {atualizados}')
            if viagens_com_erro:
                self.stdout.write(f'❌ Com erro: {len(viagens_com_erro)}')
            
            total_motoristas_banco = Viagem_Base.objects.filter(unidade__cls='motorista').count()
            self.stdout.write(f'📊 Total de viagens de motoristas no banco agora: {total_motoristas_banco}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Erro ao importar: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade, Viagem_Base, Viagem_CAM, Caminhao
import json
import pandas as pd
import time
from termcolor import colored
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass



deposito = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"

WIALON_TOKEN_BRAS = "517e0e42b9a966f628a9b8cffff3ffc3F57FA748F075501F5667A26AFA278AC983E1C616"

WIALON_TOKEN_PLAC = "82fee29da11ea1312f1c8235247a0d82DC991707A4435C60FE7FFB27BD0D0F32BF59B709"


# Tokens para diferentes ambientes
Tokens_Wialon = {
    "CPBRASCELL": WIALON_TOKEN_BRAS,
    "PLACIDO": WIALON_TOKEN_PLAC
}


class Command(BaseCommand):
    help = 'Importa dados da API Wialon'
    def handle(self, *args, **kwargs):
        start_time = datetime.now()
        self.stdout.write(self.style.SUCCESS(f'Iniciando comando às {start_time.strftime("%H:%M:%S")}'))
        
        self.principal(WIALON_TOKEN_BRAS, "CPBRASCELL")
        #self.principal(WIALON_TOKEN_PLAC, "PLACIDO")
        
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f'Comando concluído às {end_time.strftime("%H:%M:%S")}'))
        self.stdout.write(self.style.SUCCESS(f'Tempo total de execução: {execution_time}'))


    def principal(self, token, empresa_nome):
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de dados para a empresa: {empresa_nome}'))


        # Inicia a sessão Wialon
        self.stdout.write(self.style.SUCCESS(f'Iniciando sessão Wialon para {empresa_nome}...'))

        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        self.atualiza_unidades(sid, empresa_nome)

        #processa as unidades
        #self.process_units(sid)

        #self.comparar_unidades_caminhoes()







        # Encerra a sessão Wialon
        Wialon.wialon_logout(sid)

        self.stdout.write(self.style.SUCCESS(f'Sessão Wialon encerrada para {empresa_nome}.'))


        #######################################################################################

    def atualiza_unidades(self, sid, empresa_nome):
                 # Busca unidades
        unidades = unidades_simples(sid)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return
        


        #coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        print(f'Unidades encontradas:' , colored(f'{len(df_unidades)}', 'green'))
        print(f'Unidades: {df_unidades}')
        for unidade in df_unidades.itertuples(index=False):
            unidade_id = unidade.id
            unidade_nome = unidade.nm
            #separa o nome da unidade por delimitadores '_'(underline). a primeira parte antes do primeiro underline é a placa, que devemos considerar como o novo nome do veículo.
            partes_nome = unidade_nome.split('_')
            placa = partes_nome[0].strip() if partes_nome else ''
            restante_nome = ' '.join([parte.strip() for parte in partes_nome[1:]]) if len(partes_nome) > 1 else ''
    
            #checa se 'restante_nome' possui o valor 'Scania', se sim, define 'marca' como Scania
            if 'Scania' in restante_nome:
                marca = 'Scania'
            else:
                marca = 'Volvo'

            cls = 'Veículo'
            #retorna a instância da empresa correspondente
            empresa = Empresa.objects.filter(nome=empresa_nome).first()
            if not empresa:
                self.stdout.write(self.style.ERROR(f'Empresa {empresa_nome} não encontrada no banco de dados.'))
                return

            print(f'Unidade: {placa} | ID: {unidade_id} | Restante do nome: {restante_nome} | Marca: {marca} | Classe: {cls} | Empresa: {empresa.nome}')

            # Atualiza a unidade no banco de dados
            Unidade.objects.update_or_create(
                id=unidade_id,
                defaults={
                    'nm': unidade_nome,
                    'placa': placa,
                    'marca': marca,
                    'cls': cls,
                    'descricao': restante_nome if restante_nome else placa,
                    'empresa': empresa
                }
            )
            #adiciona também os motoristas

        motoristas = Wialon.motoristas_simples2(sid)
        df_motoristas = pd.DataFrame(motoristas)
        print(f'Motoristas encontrados:' , colored(f'{len(df_motoristas)}', 'green'))
        print(f'Motoristas: {df_motoristas}')

        for motorista in df_motoristas.itertuples(index=False):
            motorista_id = motorista.id
            motorista_nome = motorista.nm
            print(f'Motorista: {motorista_nome} | ID: {motorista_id}')
            






    def process_units(self, sid):
        #funcao para executar a coleta de dados de unidades por relatorios
        #recupera as unidades do banco de dados
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        print(f'Unidades no banco de dados:' , colored(f'{len(unidades_db_ids)}', 'green'))

        processamento_df = pd.DataFrame()


        #separa as unidades pertencentes a empresa
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='CPBRASCELL')

        #pega as primmeiras 10 unidades
        unidades_db = unidades_db[:5]

        # Coleta dados de relatório para 1 dia
        processamento_df = self.retrieve_unit_data(sid, unidades_db, processamento_df, tempo_dias=1, periodo='Ontem')

        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)

        # Atualiza ou cria as viagens no model Viagem_Base
        #self.update_or_create_trip(processamento_df)


        #coleta dados de relatorio para 7 dias
        #processamento_df = self.retrieve_unit_data(sid, unidades_db, processamento_df, tempo_dias=7, periodo='Últimos 7 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)

        #procecessa os valores numéricos

        # Atualiza ou cria as viagens no model Viagem_Base
        #self.update_or_create_trip(processamento_df)


        #coleta dados de relatorio para 30 dias
        #processamento_df = self.retrieve_unit_data(sid, unidades_db, processamento_df, tempo_dias=30, periodo='Últimos 30 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)

        # Atualiza ou cria as viagens no model Viagem_Base
        self.update_or_create_trip(processamento_df)
        print(processamento_df)

    def update_or_create_trip(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    unidade_instance = Unidade.objects.get(nm=row['Grouping'])
                    
                    # Processa os valores numericos
                    quilometragem = self.processar_valor_numerico(row.get('Quilometragem', '0'))
                    consumo = self.processar_valor_numerico(row.get('Consumido por AbsFCS', '0'))
                    km_media = self.processar_valor_numerico(row.get('Quilometragem média por unidade de combustível por AbsFCS', '0'))
                    velocidade_media = self.processar_valor_numerico(row.get('Velocidade média', '0'))
                    rpm_medio = self.processar_valor_numerico(row.get('RPM médio do motor', '0'))
                    temperatura_media = self.processar_valor_numerico(row.get('Temperatura média', '0'))
                    co2 = self.processar_valor_numerico(row.get('Emissões de CO2', '0'))


                    try:
                        quilometragem_value = float(quilometragem)
                        consumo_value = float(consumo)
                        km_media_value = float(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                    except (ValueError, TypeError):
                        km_media_value = 0.00
                        velocidade_media_value = 0.00
                        rpm_medio_value = 0.00
                        temperatura_media_value = 0.00
                        co2_value = 0.00

                    
                    Viagem_Base.objects.update_or_create(
                        unidade=unidade_instance,
                        período=row['periodo'],
                        defaults={
                            'quilometragem': quilometragem_value,
                            'Consumido': consumo_value,
                            'Quilometragem_média': km_media_value,
                            'Velocidade_média': velocidade_media_value,
                            'RPM_médio': rpm_medio_value,
                            'Temperatura_média': temperatura_media_value,
                            'Emissões_CO2': co2_value,

                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Viagem atualizada ou criada para a unidade {row["Grouping"]} no período {row["periodo"]} com quilometragem {quilometragem_value}'))
                
                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue

    def retrieve_unit_data(self, sid, unidades_db, processamento_df, tempo_dias, periodo):
        for unidade in unidades_db:
            unidade_id = unidade.id
            unidade_nome = unidade.nm
            #self.stdout.write(f'Processando unidade: {unidade_nome} (ID: {unidade_id})')

            # Coleta dados de relatório para 1 dia
            relatorio = Wialon.Colheitadeira_JSON(sid, unidade_id, id_relatorio=59, tempo_dias=tempo_dias, periodo=periodo)

            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            Wialon.clean_up_result(sid)
            time.sleep(1)
        return processamento_df



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

from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade, Viagem_CAM, Caminhao
import json
import pandas as pd
import time
from termcolor import colored


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

        self.principal(WIALON_TOKEN_BRAS, "CPBRASCELL")
        #self.principal(WIALON_TOKEN_PLAC, "PLACIDO")


    def principal(self, token, empresa_nome):
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de dados para a empresa: {empresa_nome}'))


        # Inicia a sessão Wialon
        self.stdout.write(self.style.SUCCESS(f'Iniciando sessão Wialon para {empresa_nome}...'))

        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return


        #processa as unidades
        self.process_units(sid)






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



    def process_units(self, sid):
        #funcao para executar a coleta de dados de unidades por relatorios
        #recupera as unidades do banco de dados
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        print(f'Unidades no banco de dados:' , colored(f'{len(unidades_db_ids)}', 'green'))


        #separa as 10 primeiras unidades para teste
        unidades_db = unidades_db[:3]


        # Coleta dados de relatório para 7 dias
        for unidade in unidades_db:
            unidade_id = unidade.id
            unidade_nome = unidade.nm
            self.stdout.write(f'Processando unidade: {unidade_nome} (ID: {unidade_id})')

            # Coleta dados de relatório para 7 dias
            Wialon.Colheitadeira_JSON(sid, unidade_id, id_relatorio=59, tempo_dias=7, periodo='Ultimos 7 dias')

            Wialon.clean_up_result(sid)
            time.sleep(1)

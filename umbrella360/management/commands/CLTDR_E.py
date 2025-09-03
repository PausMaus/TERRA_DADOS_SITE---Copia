from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.models import Empresa, Unidade, Viagem_Base, CheckPoint, Infrações, Veiculo, ConfiguracaoSistema
import json
import pandas as pd
import time
from termcolor import colored
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from tqdm import tqdm
import decimal
from django.utils import timezone
from datetime import timedelta
import pytz


deposito = rf"umbrella360\deposito"

# frotas
frt_cpbr = 401914599
frt_plac = 401929585
frt_sfre = 401939414


WIALON_TOKEN_UMBR = "fcc5baae18cdbea20200265b6b8a4af142DD8BF34CF94701039765308B2527031174B00A"
##################################################

class Command(BaseCommand):
    help = 'Importa dados da API Wialon'
    def handle(self, *args, **kwargs):
        ##################################################
        start_time = datetime.now()
        self.stdout.write(self.style.SUCCESS(f'Iniciando comando às {start_time.strftime("%H:%M:%S")}'))
        ##################################################
        # TESTE #
        #self.TESTE_03()
        self.TESTE_04()
        ##################################################
        
        ##################################################
        # PRINCIPAL #
        #self.PRINCIPAL()
        ##############################


        
        ##################################################
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f'Comando concluído às {end_time.strftime("%H:%M:%S")}'))
        self.stdout.write(self.style.SUCCESS(f'Tempo total de execução: {execution_time}'))
    #######################################################################################


    def TESTE(self):

        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
            self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
            return
        
        
        Wialon.set_locale()
        processamento_df = pd.DataFrame()

        print(Infrações.objects.all())
        print(f'Número de infrações antes da limpeza: {Infrações.objects.count()}')
        print(CheckPoint.objects.all())
        print(f'Número de checkpoints antes da limpeza: {CheckPoint.objects.count()}')


        
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=1)
        processamento_df = pd.DataFrame()   

        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=1)
        processamento_df = pd.DataFrame()


        Wialon.wialon_logout(sid)

    def TESTE_02(self):
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return
        
        processamento_df = pd.DataFrame()
                
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=30, periodo="Últimos 30 dias")
        #
        Wialon.wialon_logout(sid)

    def TESTE_03(self):
        bandeiras = []
        self.Limpeza()  
        print("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()


        ###__UNIDADES__TODAS__###
        print(colored("Processando Unidades...",'yellow'))
        processamento_df = pd.DataFrame()
        # Coleta de dados para o relatório

        
        #self.CLTDR_01(sid, processamento_df, flag=16777218, dias=1, periodo="Ontem")
        #self.CLTDR_01(sid, processamento_df, flag=16777218, dias=7, periodo="Últimos 7 dias")
        #self.CLTDR_01(sid, processamento_df, flag=16777218, dias=20, periodo="Últimos 20 dias")
        #
        #self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_cpbr, dias=30, periodo="Últimos 30 dias")

        #
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401939410, dias=1, periodo="Últimos 30 dias")
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401939414, dias=1, periodo="Últimos 30 dias")
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401929585, dias=1, periodo="Últimos 30 dias")
        #
        processamento_df = pd.DataFrame()
        ###


        ###__CARGO__POLO__###
        # CAMINHOES
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=1, periodo="Ontem")
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=30, periodo="Últimos 30 dias")


        #motoristas 
        #self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777218, dias=1, periodo="Ontem")
        #self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777220, dias=1, periodo="Últimos 7 dias")
        #self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777224, dias=1, periodo="Últimos 30 dias")

        processamento_df = pd.DataFrame()

        ###__PLACIDO__###
        # CAMINHÕES
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=30, periodo="Últimos 30 dias")

        #Motoristas
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777218, dias=1, periodo="Ontem")
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777220, dias=1, periodo="Últimos 7 dias")
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777224, dias=1, periodo="Últimos 30 dias")

        processamento_df = pd.DataFrame()


        ###__SFRESGATE__###
        # VEICULOS
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=30, periodo="Últimos 30 dias")

        #motoristas 
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777218, dias=1, periodo="Ontem")
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777220, dias=1, periodo="Últimos 7 dias")
        #self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777224, dias=1, periodo="Últimos 30 dias")
        #processamento_df = pd.DataFrame()

        #checkpoints e infrações
        #self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()   

        #self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()

        print(bandeiras)
        Wialon.wialon_logout(sid)

    def TESTE_04(self):
        def comm(msg):
            print(colored("="*30, "yellow"))
            print(colored(f"{nome}:","green"))
            print(f"{msg}")
            print(colored("="*30, "yellow"))
        #lista as empresas registradas
        empresas = Empresa.objects.all()
        for empresa in empresas:
            print(f'Empresa: {empresa.nome}')
            # Inicia a sessão Wialon para cada empresa
            sid=Wialon.authenticate_with_wialon(empresa.token)
            print(f'Sessão Wialon iniciada para {empresa.nome}, ID de recurso: {empresa.id_recurso}')
            if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                continue

            unidades = unidades_simples_03(sid,empresa)
            if not unidades:
                self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
                return
            
            #print(f'Unidades encontradas:' , colored(f'{len(unidades)}', 'green'))
            #print(f'Unidades: {colored(f"{unidades}", "green")}')

            #coloca os dados em um dataframe
            df_unidades = pd.DataFrame(unidades)
            print(f'Unidades encontradas:' , colored(f'{len(df_unidades)}', 'green'))
            print(f'Unidades: {df_unidades}')
            df_unidades.to_excel(f'{deposito}/{empresa.nome}_unidades.xlsx', index=False)

            

            for unidade in df_unidades.itertuples(index=False):
                id=unidade.unit_id
                nome=unidade.unit_name
                marca=unidade.brand
                modelo=unidade.model
                ano=unidade.year
                cor=unidade.color
                placa=unidade.registration_plate
                cls = 'Veículo'
                unidade_id = f"{empresa.nome}_{id}"

                # Faça algo com o nome da unidade
                comm(f'Nome da unidade: {nome}, Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Cor: {cor}, Placa: {placa}')

                # Atualiza a unidade no banco de dados
                Veiculo.objects.update_or_create(
                    id=unidade_id,
                    defaults={
                        'nm': nome,
                        'placa': placa,
                        'marca': marca,
                        'cls': cls,
                        'empresa': empresa,
                        'cor': cor,
                        'modelo': modelo
                    }
                )





        #faz logout
        Wialon.wialon_logout(sid)

        sid=Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
                            #checkpoints e infrações
        processamento_df = pd.DataFrame()
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()   

        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()



    def PRINCIPAL(self):
        self.Limpeza()
        self.atualizar_01()
        self.processamento_global()

    def Limpeza(self):
        # Limpa os dados antigos
        #Unidade.objects.all().delete()
        Infrações.objects.all().delete()
        CheckPoint.objects.all().delete()
        Viagem_Base.objects.all().delete()

    def atualizar_01(self):
        #lista as empresas registradas
        empresas = Empresa.objects.all()
        for empresa in empresas:
            print(f'Empresa: {empresa.nome}')
            # Inicia a sessão Wialon para cada empresa
            sid=Wialon.authenticate_with_wialon(empresa.token)
            print(f'Sessão Wialon iniciada para {empresa.nome}, ID de recurso: {empresa.id_recurso}')
            if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                continue

            Wialon.set_locale()

            #busca relatórios
            relatórios = Wialon.buscadora_reports(sid)
            print(f'Relatórios encontrados: {colored(len(relatórios), "green")}')
            relatórios = json.dumps(relatórios, indent=4)
            print(f'Relatórios: {relatórios}')
            #-------
            #salva os relatorios em .txt no deposito
            #with open(f'{deposito}/{empresa.nome}_relatorios.txt', 'w') as f:
            #    f.write(json.dumps(relatórios, indent=4))
            #-------
            unidades = Wialon.unidades_simples(sid)
            print(f'Unidades encontradas: {colored(len(unidades), "green")}')
            #-------
            #for unidade in unidades:
            #    print(f'Unidade: {unidade}')
            #-------
            df_unidades = pd.DataFrame(unidades)
            print(f'Unidades: {df_unidades}')


            motoristas = Wialon.motoristas_simples2(sid)
            df_motoristas = pd.DataFrame(motoristas)
            print(f'Motoristas encontrados:' , colored(f'{len(df_motoristas)}', 'green'))
            print(f'Motoristas: {df_motoristas}')
            
            # Atualiza as unidades
            self.atualiza_unidades(sid, empresa.nome)
            ###

            #faz logout
            Wialon.wialon_logout(sid)

    def processamento_global(self):
        print("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        processamento_df = pd.DataFrame()

        ###__UNIDADES__TODAS__###
        print("Processando Unidades...")
        self.processador_unidades_totais(sid, processamento_df)
        print("Unidades processadas.")
        ###

        processamento_df = pd.DataFrame()

        ###__CARGO__POLO__###
        #motoristas 
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777224, dias=1, periodo="Últimos 30 dias")

        processamento_df = pd.DataFrame()

        ###__PLACIDO__###
        #Motoristas 
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777224, dias=1, periodo="Últimos 30 dias")

        processamento_df = pd.DataFrame()


        ###__SFRESGATE__###
        #motoristas 
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777224, dias=1, periodo="Últimos 30 dias")
        processamento_df = pd.DataFrame()

        #checkpoints e infrações
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()   

        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()

    def processador_unidades_totais(self, sid, processamento_df):
        print("Processando Unidades...")
        # Coleta de dados para o relatório
        
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_01(sid, processamento_df, flag=16777218, dias=30, periodo="Últimos 30 dias")
        #
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401939410, dias=1, periodo="Últimos 30 dias")
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401939414, dias=1, periodo="Últimos 30 dias")
        #self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401929585, dias=1, periodo="Últimos 30 dias")
        #
        processamento_df = pd.DataFrame()

        
#######################################################################################
    def CLTDR_01(self, sid, processamento_df, flag, dias, periodo):
        print(colored("="*30,'yellow'))
        print(colored(f'Coletando dados de unidades para ({periodo})','cyan'))

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=flag, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401946382, reportObjectSecId=0, unit_id="CLTDR_01",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #---
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)

    def CLTDR_02(self, sid, processamento_df, flag, Objeto, dias, periodo):
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=flag, reportResourceId=401756219, reportTemplateId=59, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)

    def CLTDR_03(self, sid, processamento_df, recurso, template, flag, Objeto, dias, periodo):
        #Adicionado resource, template
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)


    def CLTDR_04(self, sid, processamento_df, recurso, template, flag, Objeto, dias, periodo):
        #Adicionado resource, template
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)

            self.viagem(processamento_df)
            Wialon.clean_up_result(sid)


    def CLTDR_TESTE(self, sid, processamento_df, recurso, template, flag, Objeto, dias, periodo):
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            # salva em xlsx no deposito
            processamento_df.to_excel(f'{deposito}/relatorio_[UMBR]TESTE.xlsx', index=False)

            Wialon.clean_up_result(sid)

    def CLTDR_CP_01(self, sid, processamento_df, recurso, template, flag, Objeto, dias):
        #Adicionado resource, template
        print(f'Coletando dados de relatório [Cercas]')

        relatorio = Wialon.Colheitadeira_JSON_CP_01(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            #processamento_df.to_excel(f'{deposito}/relatorio_[UMBR]CERCAS.xlsx', index=False)
            self.update_or_create_checkpoint(processamento_df)
            Wialon.clean_up_result(sid)

    def CLTDR_MOT_01(self, sid, processamento_df, Objeto, flag, dias, periodo):
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag, reportResourceId=401756219, reportTemplateId=58, reportObjectId=Objeto, reportObjectSecId=1, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #---
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)
    
    def CLTDR_MOT_02(self, sid, processamento_df, recurso, template, Objeto, flag, dias, periodo):
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=1, unit_id="teste",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #-----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)

    def CLTDR_INFRA_01(self, sid, processamento_df, recurso, template, flag, Objeto, dias):
        #Adicionado resource, template
        print(f'Coletando dados de relatório [INFRAÇÕES]')

        relatorio = Wialon.Colheitadeira_JSON_INFRA_02(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste",  tempo_dias=dias)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            #-----
            #processamento_df.to_excel(f'{deposito}/relatorio_[UMBR]INFRA.xlsx', index=False)
            #-----
            self.update_or_create_infração(processamento_df)
            Wialon.clean_up_result(sid)




    def processamento_teste(self, empresa):
        if empresa.nome == 'CPBRACELL':
        #processa as unidades
            processamento_df = pd.DataFrame()
            self.CLTDR_02(sid, processamento_df, flag=16777218, Objeto=401756235, dias=1, periodo="Ontem")
            self.CLTDR_02(sid, processamento_df, flag=16777220, Objeto=401756235, dias=1, periodo="Últimos 7 dias")
            self.CLTDR_02(sid, processamento_df, flag=16777224, Objeto=401756235, dias=1, periodo="Últimos 30 dias")

        #processa os motoristas
            processamento_df = pd.DataFrame()
            self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777218, dias=1, periodo="Ontem")
            self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777220, dias=1, periodo="Últimos 7 dias")
            self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777224, dias=1, periodo="Últimos 30 dias")

        elif empresa.nome == 'PLACIDO':
            #processa as unidades
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777218, Objeto=401756235, dias=1, periodo="Ontem")
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777220, Objeto=401756235, dias=1, periodo="Últimos 7 dias")
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777224, Objeto=401756235, dias=1, periodo="Últimos 30 dias")
            

        elif empresa.nome == 'São Francisco Resgate':
            #processa as unidades
            processamento_df = pd.DataFrame()
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777218, Objeto=401756235, dias=1, periodo="Ontem")
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777220, Objeto=401756235, dias=1, periodo="Últimos 7 dias")
            self.CLTDR_03(sid, processamento_df, recurso=401756235, template=59, flag=16777224, Objeto=401756235, dias=1, periodo="Últimos 30 dias")





    def principal(self, token, empresa_nome):
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de dados para a empresa: {empresa_nome}'))


        # Inicia a sessão Wialon
        self.stdout.write(self.style.SUCCESS(f'Iniciando sessão Wialon para {empresa_nome}...'))

        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        self.atualiza_unidades(sid, empresa_nome)

        #busca os relatorios
        print(Wialon.buscadora_reports(sid))

        if empresa_nome == 'CPBRACELL':
            self.process_units_CP(sid)
            #self.process_motoristas_CP_2(sid)

        if empresa_nome == 'PLACIDO':
            self.process_units_PLAC(sid)

        elif empresa_nome == 'São Francisco Resgate':
            self.process_units_SF(sid)

        # Encerra a sessão Wialon
        Wialon.wialon_logout(sid)

        self.stdout.write(self.style.SUCCESS(f'Sessão Wialon encerrada para {empresa_nome}.'))


        #######################################################################################

    def localizzare(self, token):
        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        #busca os relatorios
        relatórios = Wialon.buscadora_reports(sid)
        #salva os relatorios em .txt no deposito
        with open(f'{deposito}/localizzare_relatorios.txt', 'w') as f:
            f.write(json.dumps(relatórios, indent=4))

        unidades = unidades_simples(sid)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return
        
        #coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        print(f'Unidades encontradas:' , colored(f'{len(df_unidades)}', 'green'))
        print(f'Unidades: {df_unidades}')
        #salva as unidades em um excel
        df_unidades.to_excel(f'{deposito}/localizzare_unidades.xlsx', index=False)
        #
        motoristas = Wialon.motoristas_simples2(sid)
        df_motoristas = pd.DataFrame(motoristas)
        print(f'Motoristas encontrados:' , colored(f'{len(df_motoristas)}', 'green'))
        print(f'Motoristas: {df_motoristas}')
        df_motoristas.to_excel(f'{deposito}/localizzare_motoristas.xlsx', index=False)

        #####

        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(cls__icontains='Veículo')  # Filtra por classe que contém "Veículo"

        processamento_df = pd.DataFrame()
        unidades_db = unidades_db
        unidades_db = unidades_db[:5]# Limita a 5 veículos para teste
        # Coleta dados de relatório para 1 dia
        
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=1, periodo='Ontem')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)

        processamento_df.to_excel(f'{deposito}/localizzare_veiculos.xlsx', index=False)
#######
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(cls__icontains='Motorista')  # Filtra por classe que contém "Motorista"
            unidades_db = unidades_db.filter(empresa__nome='CPBRACELL')  # Filtra por empresa CPBRACELL
        processamento_df = pd.DataFrame()
        unidades_db = unidades_db
        unidades_db = unidades_db[:5]  # Limita a 5 motoristas para teste
        # Coleta dados de relatório para 1 dia
        
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 58, processamento_df, tempo_dias=1, periodo='Ontem')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)

        processamento_df.to_excel(f'{deposito}/localizzare_motoristas.xlsx', index=False)

        motoristas = Wialon.motoristas_simples2(sid)
        df_motoristas = pd.DataFrame(motoristas)
        print(f'Motoristas encontrados:' , colored(f'{len(df_motoristas)}', 'green'))
        print(f'Motoristas: {df_motoristas}')
        #seleciona os 10 primeiros motoristas do dataframe
        df_motoristas = df_motoristas.head(10)
        for motorista in df_motoristas.itertuples(index=False):
            motorista_id = motorista.driver_id

            relatorio = Wialon.Colheitadeira_JSON_02(sid, 401756219, motorista_id, 5, tempo_dias=1, periodo="teste")
            print(relatorio)
            Wialon.clean_up_result(sid)
            relatorio = Wialon.Colheitadeira_JSON_02(sid, 401756219, motorista_id, 58, tempo_dias=1, periodo="teste")
            print(relatorio)
            Wialon.clean_up_result(sid)





        Wialon.wialon_logout(sid)

    def localizzare2(self, token):
        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()

        ###__UNIDADES__TODAS__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_ontem.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)

        ###__MOTORISTAS__CPBrascell__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_ontem.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)
        
        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)

        ###__MOTORISTAS__PLACIDO__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_ontem.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)
        
        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)


        Wialon.wialon_logout(sid)

    
    def localizzare3(self, token):
        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        processamento_df = pd.DataFrame()

        ###__UNIDADES__TODAS__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')

        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_ontem.xlsx', index=False)
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)
            print("RESULTADO:")
            print(processamento_df)

        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=59, reportObjectId=401939391, reportObjectSecId=0, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[UMBR]UNIDADES_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)

        ###__MOTORISTAS__CPBrascell__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_ontem.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)
        
        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401756219, reportTemplateId=58, reportObjectId=401756219, reportObjectSecId=1, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[CPB]MOTORISTAS_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)

        ###__MOTORISTAS__PLACIDO__###

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=1, periodo="Ontem")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_ontem.xlsx', index=False)
        Wialon.clean_up_result(sid)

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=7, periodo="Semana")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_semana.xlsx', index=False)
        Wialon.clean_up_result(sid)
        
        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag=16777218, reportResourceId=401768999, reportTemplateId=48, reportObjectId=401768999, reportObjectSecId=1, unit_id="teste",  tempo_dias=30, periodo="Mês")
        print(f'Relatório coletado: {relatorio}')
        if relatorio is not None:
            relatorio.to_excel(f'{deposito}/relatorio_[PLA]MOTORISTAS_mes.xlsx', index=False)
        Wialon.clean_up_result(sid)


        Wialon.wialon_logout(sid)

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
            if empresa.nome == 'PLACIDO':
                marca = 'DAF'
            if empresa.nome == 'São Francisco Resgate':
                marca = 'Fiat'
            unidade_id = f"{empresa_nome}_{unidade_id}"

            #+---
            print(f'Unidade: {placa} | ID: {unidade_id} | Restante do nome: {restante_nome} | Marca: {marca} | Classe: {cls} | Empresa: {empresa.nome}')
            #+---

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
            motorista_id = motorista.driver_id
            motorista_nome = motorista.driver_name
            cls = 'Motorista'
            empresa = Empresa.objects.filter(nome=empresa_nome).first()
            if not empresa:
                self.stdout.write(self.style.ERROR(f'Empresa {empresa_nome} não encontrada no banco de dados.'))
                return

            motorista_id = f"{empresa_nome}_{motorista_id}"

            print(f'Motorista: {motorista_nome} | ID: {motorista_id} | Classe: {cls} | Empresa: {empresa.nome}')

            # Atualiza o motorista no banco de dados
            Unidade.objects.update_or_create(
                id=motorista_id,
                defaults={
                    'nm': motorista_nome,
                    'cls': cls,
                    'empresa': empresa,
                }
            )





    def process_units_CP(self, sid):
        # CAMINHOES BRASCELL#######################
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='CPBRASCELL')
            unidades_db = unidades_db.filter(cls__icontains='Veículo')  # Filtra por classe que contém "Veículo"

        processamento_df = pd.DataFrame()
        unidades_db = unidades_db
        # Coleta dados de relatório para 1 dia
        
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=1, periodo='Ontem')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=7, periodo='Últimos 7 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=30, periodo='Últimos 30 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        




        # Atualiza ou cria as viagens no model Viagem_Base

        self.update_or_create_trip(processamento_df)



    def process_units_PLAC(self, sid):
        # CAMINHOES PLACIDO#######################
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='PLACIDO')
            unidades_db = unidades_db.filter(cls__icontains='Veículo')  # Filtra por classe que contém "Veículo"

        processamento_df = pd.DataFrame()

        # Coleta dados de relatório para 1 dia
        processamento_df = self.retrieve_unit_data(sid, 401768999, unidades_db, 45, processamento_df, tempo_dias=1, periodo='Ontem')
        processamento_df = self.retrieve_unit_data(sid, 401768999, unidades_db, 45, processamento_df, tempo_dias=7, periodo='Últimos 7 dias')
        processamento_df = self.retrieve_unit_data(sid, 401768999, unidades_db, 45, processamento_df, tempo_dias=30, periodo='Últimos 30 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')

        # Atualiza ou cria as viagens no model Viagem_Base
        self.update_or_create_trip(processamento_df)
        print(processamento_df)

    def process_units_SF(self, sid):
        # CAMINHOES SÃO FRANCISCO#######################
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='São Francisco Resgate')
            unidades_db = unidades_db.filter(cls__icontains='Veículo')  # Filtra por classe que contém "Veículo"

        processamento_df = pd.DataFrame()
        unidades_db = unidades_db
        # Coleta dados de relatório para 1 dia
        
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=1, periodo='Ontem')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=7, periodo='Últimos 7 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 59, processamento_df, tempo_dias=30, periodo='Últimos 30 dias')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        




        # Atualiza ou cria as viagens no model Viagem_Base

        self.update_or_create_trip(processamento_df)



    def process_motoristas_CP(self, sid):
        #MOTORISTAS BRASCELL####################################################################################
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='CPBRACELL')
            unidades_db = unidades_db.filter(cls__icontains='Motorista')  # Filtra por classe que contém "Motorista"

        processamento_df = pd.DataFrame()
        #pega as primmeiras 5 unidades
        unidades_db = unidades_db[:5]
        print(f"ids_motoristas: {unidades_db}")
        # Coleta dados de relatório para 7 dias
        processamento_df = self.retrieve_unit_data_motorista(sid, 401756219, unidades_db, 58, processamento_df, tempo_dias=7, periodo='Ultimos 7 dias')
        print(f'Relatórios coletados para {len(processamento_df)} motoristas.')
        print(processamento_df)

    def process_motoristas_CP_2(self, sid):
        # motoristas BRASCELL#######################
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='CPBRACELL')
            unidades_db = unidades_db.filter(cls__icontains='Motorista')  # Filtra por classe que contém "Motorista"

        processamento_df = pd.DataFrame()
        unidades_db = unidades_db
        # Coleta dados de relatório para 1 dia
        
        processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 58, processamento_df, tempo_dias=1, periodo='Ontem')
        print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        print(processamento_df)
        #processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 58, processamento_df, tempo_dias=7, periodo='Últimos 7 dias')
        #print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        #print(processamento_df)
        #processamento_df = self.retrieve_unit_data(sid, 401756219, unidades_db, 58, processamento_df, tempo_dias=30, periodo='Últimos 30 dias')
        #print(f'Relatórios coletados para {len(processamento_df)} unidades.')
        #print(processamento_df)
        




        # Atualiza ou cria as viagens no model Viagem_Base

        self.update_or_create_trip(processamento_df)

    def update_or_create_trip(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    unidades = Unidade.objects.filter(nm=row['Grouping'])
                    
                    if not unidades.exists():
                        self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                        continue
                    
                    if unidades.count() > 1:
                        self.stdout.write(self.style.WARNING(f'Múltiplas unidades encontradas com nome "{colored(row["Grouping"], "red")}". Usando a primeira.'))
                        # Log das unidades duplicadas para análise
                        for unidade in unidades:
                            self.stdout.write(self.style.WARNING(f'  - ID: {unidade.id}, Empresa: {unidade.empresa.nome if unidade.empresa else "N/A"}'))
                    
                    unidade_instance = unidades.first()
                    
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
                    self.stdout.write(self.style.SUCCESS(f'Viagem: {colored(row["Grouping"], "cyan")} - {colored(row["periodo"], "magenta")} - {colored(quilometragem_value, "green")}'))

                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue



    def viagem(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    unidades = Unidade.objects.filter(nm=row['Grouping'])
                    
                    if not unidades.exists():
                        self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                        continue
                    
                    if unidades.count() > 1:
                        self.stdout.write(self.style.WARNING(f'Múltiplas unidades encontradas com nome "{colored(row["Grouping"], "red")}". Usando a primeira.'))
                        # Log das unidades duplicadas para análise
                        for unidade in unidades:
                            self.stdout.write(self.style.WARNING(f'  - ID: {unidade.id}, Empresa: {unidade.empresa.nome if unidade.empresa else "N/A"}'))
                    
                    unidade_instance = unidades.first()
                    
                    # Processa os valores numericos
                    quilometragem = self.processar_valor_numerico(row.get('Quilometragem Percorrida', '0'))
                    consumo = self.processar_valor_numerico(row.get('Consumido por AbsFCS', '0'))
                    km_media = self.processar_valor_numerico(row.get('Média de Consumo de Combustivel em Movimento', '0'))
                    velocidade_media = self.processar_valor_numerico(row.get('Velocidade média', '0'))
                    rpm_medio = self.processar_valor_numerico(row.get('RPM médio do motor', '0'))
                    temperatura_media = self.processar_valor_numerico(row.get('Temperatura média', '0'))
                    co2 = self.processar_valor_numerico(row.get('Emissões de CO2', '0'))
                    odometro = self.processar_valor_numerico(row.get('Hodometro Atual', '0'))


                    try:
                        quilometragem_value = float(quilometragem)
                        consumo_value = float(consumo)
                        km_media_value = float(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                        odometro_value = float(odometro)
                    except (ValueError, TypeError):
                        km_media_value = 0.00
                        velocidade_media_value = 0.00
                        rpm_medio_value = 0.00
                        temperatura_media_value = 0.00
                        co2_value = 0.00
                        odometro_value = 0.00

                    
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
                    Unidade.objects.filter(id=unidade_instance.id).update(odometro=odometro_value)

                    self.stdout.write(self.style.SUCCESS(f'Viagem: {colored(row["Grouping"], "cyan")} - {colored(row["periodo"], "magenta")} - {colored(quilometragem_value, "green")}'))

                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue



    def update_or_create_checkpoint(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    # CORREÇÃO: Obter uma instância única em vez de QuerySet
                    unidades = Unidade.objects.filter(nm=row['Grouping'])
                    
                    if not unidades.exists():
                        self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                        continue
                    
                    if unidades.count() > 1:
                        self.stdout.write(self.style.WARNING(f'Múltiplas unidades encontradas com nome "{colored(row["Grouping"], "red")}". Usando a primeira.'))
                        # Log das unidades duplicadas para análise
                        for unidade in unidades:
                            self.stdout.write(self.style.WARNING(f'  - ID: {unidade.id}, Empresa: {unidade.empresa.nome if unidade.empresa else "N/A"}'))
                    
                    unidade_instance = unidades.first()  # Obter a instância única
                    
                    # Processa os valores de data/hora
                    hora_entrada = self.processar_datetime2(row.get('Hora de entrada'))
                    hora_saida = self.processar_datetime2(row.get('Hora de saída'))
                    duracao = self.processar_duracao(row.get('Duração em', ''))



                    # Processa a cerca eletrônica (texto)
                    cerca_eletronica = str(row.get('Cerca eletrônica', '')).strip()

                    CheckPoint.objects.update_or_create(
                        unidade=unidade_instance,  # CORREÇÃO: Usar a instância em vez do QuerySet
                        cerca=cerca_eletronica,
                        data_entrada=hora_entrada,
                        data_saida=hora_saida,
                        duracao=duracao
                    )
                    #+---
                    #self.stdout.write(self.style.SUCCESS(f'CheckPoint  {colored(row["Grouping"], "cyan")} -  - Cerca: {colored(cerca_eletronica, "green")} - Hora de entrada: {colored(hora_entrada, "blue")} - Hora de saída: {colored(hora_saida, "blue")}. - Duração: {colored(duracao, "green")}'))
                    #+---
                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao processar linha {index + 1}: {str(e)}'))
                    continue



    def update_or_create_infração(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    # CORREÇÃO: Obter uma instância única em vez de QuerySet
                    unidades = Unidade.objects.filter(nm=row['Grouping'])
                    
                    if not unidades.exists():
                        self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                        continue
                    
                    if unidades.count() > 1:
                        self.stdout.write(self.style.WARNING(f'Múltiplas unidades encontradas com nome "{colored(row["Grouping"], "red")}". Usando a primeira.'))
                        # Log das unidades duplicadas para análise
                        for unidade in unidades:
                            self.stdout.write(self.style.WARNING(f'  - ID: {unidade.id}, Empresa: {unidade.empresa.nome if unidade.empresa else "N/A"}'))
                    
                    unidade_instance = unidades.first()  # Obter a instância única
                    #remove "km/h”
                    velocidade=row.get('Velocidade média', '').replace("km/h", "").strip()
                    limite = row.get('Limite de velocidade', '').replace("km/h", "").strip()
                    data = row.get('Início', '').strip()

                    latitude = row.get('Latitude', '')
                    longitude = row.get('Longitude', '')
                    
                    maps = f"https://www.google.com/maps?q={latitude},{longitude}"

                    # Processa os valores de data/hora
                    #hora_entrada = self.processar_datetime(row.get('Hora de entrada'))
                    #hora_saida = self.processar_datetime(row.get('Hora de saída'))
                    #duracao = self.processar_duracao(row.get('Duração em', ''))

                    Infrações.objects.update_or_create(
                        unidade=unidade_instance,
                        velocidade=velocidade,
                        limite=limite,  
                        data=self.processar_datetime2(data),
                        localizacao=maps,
                    )
                    self.stdout.write(self.style.SUCCESS(f'WORKED!'))

                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao processar linha {index + 1}: {str(e)}'))
                    continue

    def processar_datetime(self, valor_datetime):
        """
        Processa valores de data/hora do Excel e aplica fuso horário GMT-03 (Brasília)
        """
        try:
            if pd.isna(valor_datetime) or valor_datetime == '' or valor_datetime is None:
                return None
            

            
            # Se já é um datetime do pandas
            if isinstance(valor_datetime, pd.Timestamp):
                dt = valor_datetime.to_pydatetime()
            elif isinstance(valor_datetime, str):
                # Se é string, tenta converter
                dt = None
                # Tenta alguns formatos comuns - colocando o formato correto primeiro
                formatos = [
                    '%d.%m.%Y %H:%M:%S',  # 17.08.2025 15:31:02 (formato correto)
                    '%Y-%m-%d %H:%M:%S',  # 2025-08-17 15:31:02
                    '%d/%m/%Y %H:%M:%S',  # 17/08/2025 15:31:02
                    '%Y-%m-%d',           # 2025-08-17
                    '%d.%m.%Y',           # 17.08.2025
                    '%d/%m/%Y',           # 17/08/2025
                ]
                
                for formato in formatos:
                    try:
                        dt = datetime.strptime(valor_datetime.strip(), formato)
                        break
                    except ValueError:
                        continue
                
                if dt is None:
                    # Se não conseguiu converter, retorna None
                    self.stdout.write(self.style.WARNING(f'Formato de data/hora não reconhecido: {valor_datetime}'))
                    return None
            else:
                return None
            
            # FORÇA BRUTA: Subtrai 3 horas diretamente
            dt_brasilia = dt - timedelta(hours=3)
            
            # Aplica o timezone de Brasília ao resultado
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            
            # Se o datetime resultante é "naive", localiza no timezone de Brasília
            if dt_brasilia.tzinfo is None:
                dt_brasilia = brasilia_tz.localize(dt_brasilia)
            else:
                # Se já tem timezone, converte para Brasília
                dt_brasilia = dt_brasilia.astimezone(brasilia_tz)
            
            return dt_brasilia
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao processar data/hora "{valor_datetime}": {e}'))
            return None
        

    
    def processar_datetime2(self, valor_datetime):
        """
        Processa valores de data/hora do Excel e aplica fuso horário GMT-03 (Brasília)
        """
        try:
            if pd.isna(valor_datetime) or valor_datetime == '' or valor_datetime is None:
                return None
            
            from django.utils import timezone
            from datetime import timedelta
            import pytz
            
            # Se já é um datetime do pandas
            if isinstance(valor_datetime, pd.Timestamp):
                dt = valor_datetime.to_pydatetime()
            elif isinstance(valor_datetime, str):
                # Se é string, tenta converter
                dt = None
                # Tenta alguns formatos comuns - colocando o formato correto primeiro
                formatos = [
                    '%d.%m.%Y %H:%M:%S',  # 17.08.2025 15:31:02 (formato correto)
                    '%Y-%m-%d %H:%M:%S',  # 2025-08-17 15:31:02
                    '%d/%m/%Y %H:%M:%S',  # 17/08/2025 15:31:02
                    '%Y-%m-%d',           # 2025-08-17
                    '%d.%m.%Y',           # 17.08.2025
                    '%d/%m/%Y',           # 17/08/2025
                ]
                
                for formato in formatos:
                    try:
                        dt = datetime.strptime(valor_datetime.strip(), formato)
                        break
                    except ValueError:
                        continue
                
                if dt is None:
                    # Se não conseguiu converter, retorna None
                    self.stdout.write(self.style.WARNING(f'Formato de data/hora não reconhecido: {valor_datetime}'))
                    return None
            else:
                return None
            
            # FORÇA BRUTA: Subtrai 3 horas diretamente
            dt_brasilia = dt - timedelta(hours=3)
            
            
            return dt_brasilia
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao processar data/hora "{valor_datetime}": {e}'))
            return None

    def processar_duracao(self, valor_duracao):
        """
        Processa valores de duração (formato "1 dias 3:20:04" ou HH:MM:SS)
        Retorna um objeto timedelta para o campo DurationField do Django
        """
        try:
            if pd.isna(valor_duracao) or valor_duracao == '' or valor_duracao is None:
                return None
            
            # Converte para string
            duracao_str = str(valor_duracao).strip()
            
            # Se está vazio após strip
            if not duracao_str:
                return None
            
            # Verifica se é o formato "X dias HH:MM:SS"
            if 'dias' in duracao_str or 'dia' in duracao_str:
                import re
                from datetime import timedelta
                
                # Regex para capturar dias e tempo
                match = re.match(r'(\d+)\s+dias?\s+(\d+):(\d+):(\d+)', duracao_str)
                if match:
                    dias = int(match.group(1))
                    horas = int(match.group(2))
                    minutos = int(match.group(3))
                    segundos = int(match.group(4))
                    
                    return timedelta(days=dias, hours=horas, minutes=minutos, seconds=segundos)
            
            # Se está no formato HH:MM:SS, converte para timedelta
            if ':' in duracao_str:
                from datetime import timedelta
                partes = duracao_str.split(':')
                if len(partes) == 3:
                    try:
                        horas = int(partes[0])
                        minutos = int(partes[1])
                        segundos = int(partes[2])
                        return timedelta(hours=horas, minutes=minutos, seconds=segundos)
                    except ValueError:
                        pass
                elif len(partes) == 2:
                    try:
                        horas = int(partes[0])
                        minutos = int(partes[1])
                        return timedelta(hours=horas, minutes=minutos)
                    except ValueError:
                        pass
            
            # Se é um número (minutos), converte para timedelta
            try:
                from datetime import timedelta
                minutos = float(duracao_str)
                return timedelta(minutes=minutos)
            except ValueError:
                pass
            
            return None
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao processar duração "{valor_duracao}": {e}'))
            return None



    def retrieve_unit_data(self, sid, resource_id, unidades_db, id_relatorio, processamento_df, tempo_dias, periodo):
        for unidade in tqdm(unidades_db, desc="Processando unidades", unit="unidade"):
            unidade_id = unidade.id

            # Coleta dados de relatório para 1 dia
            relatorio = Wialon.Colheitadeira_JSON(sid, resource_id, unidade_id, id_relatorio, tempo_dias=tempo_dias, periodo=periodo)

            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            Wialon.clean_up_result(sid)
        return processamento_df

    def retrieve_unit_data_motorista(self, sid, unidades_db, id_relatorio, processamento_df, tempo_dias, periodo):
        for unidade in tqdm(unidades_db, desc="Processando unidades", unit="unidade"):
            unidade_id = unidade.id

            # Coleta dados de relatório para 1 dia
            relatorio = Wialon.Colheitadeira_JSON_motorista(sid, unidade_id, id_relatorio, tempo_dias=tempo_dias, periodo=periodo)

            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            Wialon.clean_up_result(sid)
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

from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.models import Empresa, Unidade, Viagem_Base, CheckPoint, Infrações, Veiculo, ConfiguracaoSistema, Viagem_eco, Viagem_Detalhada, Driver
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
import sqlite3
import numbers
import threading
import time
conn = sqlite3.connect('db.sqlite3')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()






deposito = rf"C:\TERRA DADOS\laboratorium\Site\Deposito"

# frotas
#+-------------------------------------------------------------+
#| Nome da Frota       | ID da Frota  |
frt_cpbr =              401914599
frt_plac =              401929585
frt_sfre =              401939414
#+-------------------------------------------------------------+


WIALON_TOKEN_UMBR = "fcc5baae18cdbea20200265b6b8a4af142DD8BF34CF94701039765308B2527031174B00A"
##################################################

class Command(BaseCommand):
    help = 'Importa dados da API Wialon'
    def handle(self, *args, **kwargs):
        ##################################################
        # Start timing
        start_time = datetime.now()
        self.stdout.write(self.style.SUCCESS(f'Iniciando comando às {start_time.strftime("%H:%M:%S")}'))
        ###############################################
        # PRINCIPAL #
        self.Limpeza() 

        #self.CLTDR_TESTE_01(cor1="blue", cor2="green")
        #self.CLTDR_TESTE_02(cor1="blue", cor2="green")
        ##################################################
        # MENSAGENS #

        #Viagem_eco.objects.all().delete()
        #self.MENSAGENS(1,"Petitto")
        #self.MENSAGENS(1,"CPBRACELL")
        

        ##################################################
        # ESTUDO #

        ##################################################
        # CHECAGEM #
        self.Checagem_01()
        ##################################################
        # End timing and display results
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f'Comando concluído às {end_time.strftime("%H:%M:%S")}'))
        self.stdout.write(self.style.SUCCESS(f'Tempo total de execução: {execution_time}'))
        #salva o tempo de execução como uma nova linha numerada e datada em um arquivo .txt
        with open("tempo_execucao.txt", "a") as f:
            f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Tempo total de execução: {execution_time}\n')
        print("--------------------------------------------------")
    #######################################################################################
    
################################################################################################







    def atualizador_04(self,sid,id_criador,  flags=8388613):
        

        def comm(msg):
            print(colored("="*30, "yellow"))
            print(colored(f"Atualizador de Unidades V4:","green"))
            print(f"{msg}")
            print(colored("="*30, "yellow"))

        def driver_code_to_avl(codigo_motorista: int) -> int:
            # converte para hex e garante 8 caracteres
            hex_code = f'{codigo_motorista}'
            # cria uma string de 16 bytes com o código no meio
            # exemplo: prefixo + hex_code + sufixo
            # aqui usamos um padrão que gera o mesmo resultado
            reversed_bytes = '000000' + hex_code + '000000'
            # inverte os bytes novamente
            bytes_list = [reversed_bytes[i:i+2] for i in range(0, len(reversed_bytes), 2)]
            original_hex = ''.join(bytes_list[::-1])
            # converte para decimal
            return int(original_hex, 16)

                
                
        empresa = Empresa.objects.get(id_criador=id_criador)

        vcl_processados = 0
        vcl_excludentes = 0
        mtr_processados = 0
        mtr_excludentes = 0


        unidades = Wialon.unidades_simples_05(sid,  flags=flags)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return

        #coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        #+---
        #comm(f'Unidades encontradas: {len(df_unidades)}')
        #comm(f'Unidades: {df_unidades}')
        #+---

        for unidade in df_unidades.itertuples(index=False):
            id=unidade.unit_id
            nome=unidade.unit_name
            marca=unidade.brand
            modelo=unidade.model
            ano=unidade.year
            cor=unidade.color
            placa=unidade.registration_plate
            cls = 'Veículo'
            id_criador_unidade = unidade.id_criador
            if id_criador_unidade == id_criador:

                #+---
                #print(f'A unidade {nome} pertence à empresa {empresa.nome}')
                #print(colored(f'Empresa encontrada: {empresa.nome}, ID Criador: {empresa.id_criador}', 'red'))
                #+---
                #+---   
                #comm(f'Nome da unidade: {nome}, Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Cor: {cor}, Placa: {placa}')
                #+---
                
                # Atualiza a unidade no banco de dados
                Veiculo.objects.update_or_create(
                    id=f"{empresa.nome}_{id}",
                    defaults={
                        'nm': nome,
                        'placa': placa,
                        'marca': marca,
                        'cls': cls,
                        'empresa': empresa,
                        'cor': cor,
                        'modelo': modelo,
                        'id_wialon': id,
                        
                    }
                )
                vcl_processados += 1
                #+---
                #comm(f'Veículo {nome} atualizado/criado com ID {unidade_id}.')
                #+---

            else:
                vcl_excludentes += 1
                #+---
                #comm(f'A unidade {nome} não pertence à empresa CARGO POLO. ID Criador: {id_criador_unidade}')
                #+---

        #adiciona também os motoristas

        motoristas = Wialon.motoristas_simples_03(sid, flags=261)
        df_motoristas = pd.DataFrame(motoristas)

        #+---
        #comm(f'Motoristas encontrados: {len(df_motoristas)}')
        #comm(f'Motoristas: {df_motoristas}')
        #+---

        

        for motorista in df_motoristas.itertuples(index=False):
            if motorista.creator_id == id_criador:
                #+---
                #comm(f'O motorista {motorista.driver_name} pertence à empresa CARGO POLO.')
                #+---
                Driver.objects.update_or_create(
                    id=f"{empresa.nome}_{motorista.driver_id}",
                    defaults={
                        'nm': motorista.driver_name,
                        'cls': 'Motorista',
                        'empresa': empresa,
                        'id_wialon': f"{motorista.driver_name}_{motorista.driver_id}",
                        'codigo': motorista.driver_code if motorista.driver_code.isnumeric() else 0,
                        #'avl_driver': driver_code_to_avl(motorista.driver_code) if motorista.driver_code.isnumeric() else 0,
                    }
                )
                mtr_processados += 1
                #+---
                #comm(f'Motorista {motorista.driver_name} atualizado/criado com ID {empresa.nome}_{motorista.driver_id}.')
                #+---
                

            else:
                mtr_excludentes += 1
                #+---
                #comm(f'O motorista {motorista.driver_name} não pertence à empresa CARGO POLO. ID Criador: {motorista.creator_id}')
                #+---
                
            

        comm(f'{colored("Resumo:", "magenta")}\n'
            f'Veículos processados: {colored(vcl_processados, "green")}\n'
            f'Veículos excluídos: {colored(vcl_excludentes, "red")}\n'
            f'Motoristas processados: {colored(mtr_processados, "green")}\n'
            f'Motoristas excluídos: {colored(mtr_excludentes, "red")}\n'
            f'Motoristas encontrados: {len(df_motoristas)}\n'
            f'{df_motoristas.head()}'
        )




    def CLTDR_TESTE_02(self, cor1, cor2, tool="CLTDR_UMBRELLA"):
        def comm(msg):
            print(colored("="*30, cor1))
            print(colored(tool, cor2))
            print(f"{msg}")
            print(colored("="*30, cor1))
        comm("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        #busca os relatorios
        usuários = Wialon.buscadora_reports(sid)
        comm(usuários)

        ###__ATUALIZADOR_UNIDADES__###
        self.ATUALIZADOR_01(sid)

        ###__CLTDR_empresas__###
        self.CLTDR_empresas(sid, cor1="blue" , cor2="white", tool= "CLTDR_empresas")

        Wialon.wialon_logout(sid)

    def CLTDR_empresas(self, sid, cor1, cor2, tool):
        def comm(msg):
            print(colored("="*30, cor1))
            print(colored(tool, cor2))
            print(f"{msg}")
            print(colored("="*30, cor1))
        ###__CARGO__POLO__###
        comm("Processando CARGO POLO...")
        self.CARGO_POLO(sid, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr,)
        comm("CARGO POLO processado.")

        ###__PLACIDO__###
        comm("Processando PLACIDO...")
        self.PLACIDO(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac)
        comm("PLACIDO processado.")

        ###__SFRESGATE__###
        comm("Processando SFRESGATE...")
        self.SFRESGATE(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre)
        comm("SFRESGATE processado.")

        ###__PETITTO__###
        comm("Processando PETITTO...")
        self.PETITTO(sid, recurso=401756219, template=59, flag=16777218, Objeto=401904974)
        comm("PETITTO processado.")

        ###__checkpoints e infrações__###
        self.CH_INFRA(sid)



    def CLTDR_TESTE_01(self, cor1, cor2, tool="CLTDR_UMBRELLA"):
        def comm(msg):
            print(colored("="*30, cor1))
            print(colored(tool, cor2))
            print(f"{msg}")
            print(colored("="*30, cor1))
        comm("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        #busca os relatorios
        usuários = Wialon.buscadora_reports(sid)
        comm(usuários)

        ###__ATUALIZADOR_UNIDADES__###
        self.ATUALIZADOR_01(sid)

        ###__CARGO__POLO__###
        comm("Processando CARGO POLO...")
        self.CARGO_POLO(sid, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr,)
        comm("CARGO POLO processado.")

        ###__PLACIDO__###
        comm("Processando PLACIDO...")
        self.PLACIDO(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac)
        comm("PLACIDO processado.")

        ###__SFRESGATE__###
        comm("Processando SFRESGATE...")
        self.SFRESGATE(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre)
        comm("SFRESGATE processado.")

        ###__PETITTO__###
        comm("Processando PETITTO...")
        self.PETITTO(sid, recurso=401756219, template=59, flag=16777218, Objeto=401904974)
        comm("PETITTO processado.")

        ###__checkpoints e infrações__###
        self.CH_INFRA(sid)
        

        Wialon.wialon_logout(sid)





#checa se o banco de dados for completamente atualizado
    def Checagem_01(self):
        #imprime todos os dados

        unidades = Unidade.objects.all()
        infrações = Infrações.objects.all()
        checkpoints = CheckPoint.objects.all()
        viagens_base = Viagem_Base.objects.all()
        viagens_detalhadas = Viagem_Detalhada.objects.all()
        viagens_eco = Viagem_eco.objects.all()

        print(f'Unidades: {unidades.count()}')
        print(f'Infrações: {infrações.count()}')
        print(f'CheckPoints: {checkpoints.count()}')
        print(f'Viagens Base: {viagens_base.count()}')
        print(f'Viagens Detalhadas: {viagens_detalhadas.count()}')
        print(f'Viagens Econômicas: {viagens_eco.count()}')
        print("--------------------------------------------------")

        #self.Checagem_Detalhada(unidades, infrações, checkpoints, viagens_base, viagens_detalhadas, viagens_eco)

    def Checagem_Detalhada(self, unidades, infrações, checkpoints, viagens_base, viagens_detalhadas, viagens_eco):
        print("Unidades:")
        for unidade in unidades:
            print(f' - {unidade}')  
        print("--------------------------------------------------")
        print("Infrações:")
        for infração in infrações:
            print(f' - {infração}')
        print("--------------------------------------------------")
        print("CheckPoints:")
        for checkpoint in checkpoints:
            print(f' - {checkpoint}')
        print("--------------------------------------------------")
        print("Viagens Base:")
        for viagem in viagens_base:
            print(f' - {viagem}')
        print("--------------------------------------------------")
        print("Viagens Detalhadas:")
        for viagem in viagens_detalhadas:
            print(f' - {viagem}')
        print("--------------------------------------------------")
        print("Viagens Econômicas:")
        for viagem in viagens_eco:
            print(f' - {viagem}')
        print("--------------------------------------------------")
    ############################################################################################

    def CLTDR_UMBRELLA_02(self, cor1, cor2, tool="CLTDR_UMBRELLA"):
        def comm(msg):
            print(colored("="*30, cor1))
            print(colored(tool, cor2))
            print(f"{msg}")
            print(colored("="*30, cor1))
        comm("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        #busca os relatorios
        usuários = Wialon.buscadora_reports(sid)
        print(usuários)


        ###__CARGO__POLO__###
        comm("Processando CARGO POLO...")
        self.CARGO_POLO(sid, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr)
        comm("CARGO POLO processado.")
        ###__PLACIDO__###
        comm("Processando PLACIDO...")
        self.PLACIDO(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac)
        comm("PLACIDO processado.")
        ###__SFRESGATE__###
        comm("Processando SFRESGATE...")
        self.SFRESGATE(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre)
        comm("SFRESGATE processado.")

        ###__checkpoints e infrações__###
        processamento_df = pd.DataFrame()
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()
        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()

        print("Usuários encontrados:", colored(f'{len(usuários)}', 'green'))
        print("Usuários:", usuários)
    
        Wialon.wialon_logout(sid)

    def CLTDR_UMBRELLA_03(self, cor1, cor2, tool="CLTDR_UMBRELLA"):
        def comm(msg):
            print(colored("="*30, cor1))
            print(colored(tool, cor2))
            print(f"{msg}")
            print(colored("="*30, cor1))
        comm("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        Wialon.set_locale()
        #busca os relatorios
        usuários = Wialon.buscadora_reports(sid)
        comm(usuários)

        ###__ATUALIZADOR_UNIDADES__###
        self.ATUALIZADOR_01(sid)



        ###__CARGO__POLO__###
        comm("Processando CARGO POLO...")
        self.CARGO_POLO(sid, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr,)
        comm("CARGO POLO processado.")

        ###__PLACIDO__###
        comm("Processando PLACIDO...")
        self.PLACIDO(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac)
        comm("PLACIDO processado.")

        ###__SFRESGATE__###
        comm("Processando SFRESGATE...")
        self.SFRESGATE(sid, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre)
        comm("SFRESGATE processado.")

        ###__PETITTO__###
        comm("Processando PETITTO...")
        self.PETITTO(sid, recurso=401756219, template=59, flag=16777218, Objeto=401904974)
        comm("PETITTO processado.")

        ###__checkpoints e infrações__###
        self.CH_INFRA(sid)
        

        

        comm(f'{colored("Resumo:", "magenta")}\n'
            f'Usuários encontrados: {colored(len(usuários), "green")}\n'
            f'Usuários: {usuários}'
        )

        Wialon.wialon_logout(sid)

    def ATUALIZADOR_01(self, sid):
        self.atualizador_04(sid, id_criador=401756218)
        self.atualizador_04(sid, id_criador=401768998)
        self.atualizador_04(sid, id_criador=401872802)
        self.atualizador_04(sid, id_criador=401824174)



    def CH_INFRA(self, sid):
        processamento_df = pd.DataFrame()
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()
        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()





    ############################################################################################

    def CARGO_POLO(self, sid,  recurso, template, flag, Objeto,  empresa='CPBRACELL'):
        #
        self.prsr_vcl(sid, recurso, template, flag, Objeto)
        #
        self.prsr_mtr(sid, flag)
        #
        self.TESTE_01(sid, flag)


    def teste(self, sid, recurso, template, flag, Objeto):
        processamento_df = pd.DataFrame()
        self.CLTDR_05(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=1, periodo="Ontem")
        self.CLTDR_05(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=2, periodo="Anteontem")
        self.CLTDR_05(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=3, periodo="Dois Dias atrás")

    def prsr_mtr(self, sid, flag):
        processamento_df = pd.DataFrame()
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=flag, dias=1, periodo="Ontem")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=flag, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=flag, dias=30, periodo="Últimos 30 dias")



    def prsr_vcl(self, sid, recurso, template, flag, Objeto):
        processamento_df = pd.DataFrame()
        self.CLTDR_04(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=1, periodo="Ontem")
        self.CLTDR_04(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_04(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=30, periodo="Últimos 30 dias")


    def TESTE_01(self, sid, flag):
        processamento_df = pd.DataFrame()
        # pega dos ultimos 30 dias usando um loop for
        #dias = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
        # dias de testes
        dias = range(1,15)
        for dia in dias:
            self.CLTDR_MOT_01_teste(sid, processamento_df, Objeto=401756219, flag=16777216, dias=dia, periodo=str(dia))


### ############################################################################################

    def PLACIDO(self, sid, recurso, template, flag, Objeto):
        processamento_df = pd.DataFrame()
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=30, periodo="Últimos 30 dias")
        #
        processamento_df = pd.DataFrame()
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=flag, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=flag, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=flag, dias=30, periodo="Últimos 30 dias")

### ############################################################################################

    def SFRESGATE(self, sid, recurso, template, flag, Objeto):
        processamento_df = pd.DataFrame()
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=30, periodo="Últimos 30 dias")
        #
        processamento_df = pd.DataFrame()
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=flag, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=flag, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=flag, dias=30, periodo="Últimos 30 dias")



### ############################################################################################

    def PETITTO(self, sid,  recurso, template, flag, Objeto):

        processamento_df = pd.DataFrame()
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=recurso, template=template, flag=flag, Objeto=Objeto, dias=30, periodo="Últimos 30 dias")
        #
        processamento_df = pd.DataFrame()
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401756219, template=48, Objeto=401824175, flag=flag, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401756219, template=48, Objeto=401824175, flag=flag, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401756219, template=48, Objeto=401824175, flag=flag, dias=30, periodo="Últimos 30 dias")


#### ############################################################################################
   


    def Limpeza(self):
        # Limpa os dados antigos
        Unidade.objects.all().delete()
        Infrações.objects.all().delete()
        CheckPoint.objects.all().delete()
        Viagem_Base.objects.all().delete()
        Viagem_eco.objects.all().delete()
        Viagem_Detalhada.objects.all().delete()
        Driver.objects.all().delete()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("VACUUM;")


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
        #Modificado de update or create trip para viagem
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

    def CLTDR_05(self, sid, processamento_df, recurso, template, flag, Objeto,  periodo, interval_from, interval_to):
        #Modificado de update or create trip para viagem
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_04(sid, flag=flag, reportResourceId=recurso, reportTemplateId=template, reportObjectId=Objeto, reportObjectSecId=0, unit_id="teste", interval_from=interval_from, interval_to=interval_to, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #----
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)

            #self.viagem(processamento_df)
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

        relatorio = Wialon.Colheitadeira_JSON_03(sid, flag, reportResourceId=401756219, reportTemplateId=58, reportObjectId=Objeto, reportObjectSecId=2, unit_id="CLTDR_MOT_01",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            print(f'Relatório coletado: {relatorio}')
            #---
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)

            print(processamento_df)
            self.update_or_create_trip(processamento_df)
            Wialon.clean_up_result(sid)

    def CLTDR_MOT_01_teste(self, sid, processamento_df, Objeto, flag, dias, periodo):
        print(f'Coletando dados de relatório para ({periodo})')

        relatorio = Wialon.Colheitadeira_JSON_03_EX(sid, flag, reportResourceId=401756219, reportTemplateId=58, reportObjectId=Objeto, reportObjectSecId=2, unit_id="CLTDR_MOT_01",  tempo_dias=dias, periodo=periodo)

        if relatorio is not None:
            #----
            #print(f'Relatório coletado: {relatorio}')
            #---
            
            processamento_df = pd.concat([processamento_df, relatorio], ignore_index=True)
            #printa o dataframe completo
            print(processamento_df)
            #+---
            # salva como excel
            #processamento_df.to_excel(f'{deposito}/CLTDR_MOT_01_teste.xlsx', index=False)
            #+---
            
            self.update_or_create_trip_02(processamento_df)
            Wialon.clean_up_result(sid)
    
    def CLTDR_MOT_02(self, sid, processamento_df, recurso, template, Objeto, flag, dias, periodo):
        #adicionado recurso e template
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







########################################################################################


########################################################################################



    #######################################################################################

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
                        km_media_value = Decimal(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                    except (ValueError, TypeError):
                        quilometragem_value = 0.00
                        consumo_value = 0.00
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



    def update_or_create_trip_02(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    
                    unidades = Unidade.objects.filter(nm=row['Motorista'])
                    
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
                    timestamp_inicial = row.get('timestamp_from', None)
                    timestamp_final = row.get('timestamp_to', None)
                    veiculo = row.get('Unidade', None)
                    periodo = row.get('periodo', None)


                    try:
                        quilometragem_value = float(quilometragem)
                        consumo_value = float(consumo)
                        km_media_value = Decimal(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                    except (ValueError, TypeError):
                        quilometragem_value = 0.00
                        consumo_value = 0.00
                        km_media_value = 0.00
                        velocidade_media_value = 0.00
                        rpm_medio_value = 0.00
                        temperatura_media_value = 0.00
                        co2_value = 0.00

                    
                    Viagem_Detalhada.objects.update_or_create(
                        unidade=unidade_instance,
                        quilometragem = quilometragem_value,

                    

                        
                        defaults={
                            'quilometragem': quilometragem_value,
                            'Consumido': consumo_value,
                            'Quilometragem_média': km_media_value,
                            'Velocidade_média': velocidade_media_value,
                            'RPM_médio': rpm_medio_value,
                            'Temperatura_média': temperatura_media_value,
                            'Emissões_CO2': co2_value,
                            'timestamp_inicial': timestamp_inicial,
                            'timestamp_final': timestamp_final,
                            'veiculo': veiculo,
                            #'período': periodo,

                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Viagem: {colored(row["Motorista"], "cyan")} - {colored(row["periodo"], "magenta")} - {colored(row["Unidade"], "light_cyan")}- {colored(quilometragem_value, "green")} '))

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
                        km_media_value = Decimal(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                        odometro_value = float(odometro)
                    except (ValueError, TypeError):
                        quilometragem_value = 0.00
                        consumo_value = 0.00
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



    def processar_mensagens_wialon(self, messages_data):
        """
        Processa os dados de mensagens do Wialon e retorna um DataFrame pandas
        """

        
        if not messages_data:
            return pd.DataFrame()
        
        processed_data = []
        
        for message in messages_data:
            # Dados básicos da mensagem
            base_data = {
                'timestamp': message.get('t'),
                'datetime': datetime.fromtimestamp(message.get('t', 0)) if message.get('t') else None,
                'flags': message.get('f'),
                'type': message.get('tp'),
                'index': message.get('i'),
                'driver_id': message.get('dr'),
                'location_type': message.get('lc'),
                'received_time': message.get('rt'),
            }
            
            # Dados de posição
            if message.get('pos'):
                pos = message.get('pos', {})
                position_data = {
                    'latitude': pos.get('y'),
                    'longitude': pos.get('x'),
                    'course': pos.get('c'),
                    'altitude': pos.get('z'),
                    'speed': pos.get('s'),
                    'satellites': pos.get('sc'),
                }
            
            else:
                position_data = {
                    'latitude': None,
                    'longitude': None,
                    'course': None,
                    'altitude': None,
                    'speed': None,
                    'satellites': None,
                }
            # Dados de parâmetros (sensores e CAN)
            params = message.get('p', {})
            
            # Dados CAN do motor
            can_data = {
                'can_rpm': params.get('can_rpm'),
                'can_speed': params.get('can_wbspeed'),
                'can_fuel_rate': params.get('can_fuel_rate'),
                'can_distance': params.get('can_distance'),
                'can_fuel_used': params.get('can_fuel_used'),
                'can_coolant_temp': params.get('can_coolant_temp'),
                'can_acc_pedal': params.get('can_acc_pedal'),
                'can_breaks': params.get('can_breaks'),
                'can_eng_plcs': params.get('can_eng_plcs'),
                'can_hfrc': params.get('can_hfrc'),
            }
            
            # Dados de I/O
            io_data = {
                'hdop': params.get('hdop'),
                'power': params.get('power'),
                'battery': params.get('battery'),
                'odometer': params.get('odometer'),
                'gsm_signal': params.get('gsm_signal'),
                'gsm_operator': params.get('gsm_operator'),
                'movement_sens': params.get('movement_sens'),
                'current_profile': params.get('current_profile'),
                'avl_driver': params.get('avl_driver'),
            }
            
            # Sensores digitais específicos
            digital_inputs = {
                f'io_{key}': value for key, value in params.items() 
                if key.startswith('io_') and not key in ['io_caused']
            }
            
            # Combina todos os dados
            row_data = {
                **base_data,
                **position_data,
                **can_data,
                **io_data,
                **digital_inputs,
                'io_caused': params.get('io_caused'),
            }
            
            processed_data.append(row_data)
        
        df = pd.DataFrame(processed_data)
        
        # Adiciona colunas calculadas úteis
        if not df.empty:
            # Converte coordenadas para links do Google Maps
            df['google_maps'] = df.apply(
                lambda row: f"https://www.google.com/maps?q={row['latitude']},{row['longitude']}" 
                if pd.notna(row['latitude']) and pd.notna(row['longitude']) else None, 
                axis=1
            )
            
            # Converte RPM e velocidade CAN para valores mais legíveis
            if 'can_rpm' in df.columns:
                df['can_rpm_readable'] = df['can_rpm'] / 8  # Ajuste conforme necessário
        
            if 'can_speed' in df.columns:
                df['can_speed_kmh'] = df['can_speed'] / 256  # Ajuste conforme necessário
                
            # Converte odômetro para km
            if 'odometer' in df.columns:
                df['odometer_km'] = df['odometer'] / 1000
    
        return df


    def MENSAGENS(self, tempo, empresa):
        
        def avl_to_driver_code(avl_driver: int) -> int:
            """Converte código AVL para código do motorista"""
            try:
                if not avl_driver or avl_driver == 0:
                    return 0
                
                hex_str = hex(avl_driver)[2:]
                if len(hex_str) % 2 != 0:
                    hex_str = '0' + hex_str
                reversed_bytes = ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
                if len(reversed_bytes) >= 14:
                    substr = reversed_bytes[6:14]
                    return int(substr, 16)
                else:
                    return 0
            except (ValueError, TypeError, IndexError):
                return 0

        def classificar_viagem(rpm: float, velocidade: float) -> dict:
            """
            Classifica a viagem baseada em RPM e velocidade
            Retorna um dicionário com as classificações booleanas
            """
            classificacao = {
                'ocioso': False,
                'faixa_azul': False,
                'faixa_verde': False,
                'faixa_amarela': False,
                'faixa_vermelha': False
            }
            
            # Verifica se está ocioso (parado com motor ligado)
            if velocidade == 0 and rpm > 0:
                classificacao['ocioso'] = True
                return classificacao
            
            # Classifica por faixa de RPM (apenas se estiver em movimento)
            if velocidade > 0:
                if 350 <= rpm <= 799:
                    classificacao['faixa_azul'] = True
                elif 800 <= rpm <= 1300:
                    classificacao['faixa_verde'] = True
                elif 1301 <= rpm <= 2300:
                    classificacao['faixa_amarela'] = True
                elif rpm > 2301:
                    classificacao['faixa_vermelha'] = True
            
            return classificacao
        
        counter = 0

        #lista_cpbracell = Veiculo.objects.filter(empresa__nome="CPBRACELL").values_list('id_wialon', flat=True)
        #lista_petitto = Veiculo.objects.filter(empresa__nome="Petitto").values_list('id_wialon', flat=True)
        #lista_sfresgate = Veiculo.objects.filter(empresa__nome="São Francisco Resgate").values_list('id_wialon', flat=True)
        #lista_unidades = list(lista_sfresgate) + list(lista_petitto) + list(lista_cpbracell)
        #lista_unidades = list(lista_petitto) + list(lista_cpbracell)

        lista_unidades = Veiculo.objects.filter(empresa__nome=empresa).values_list('id_wialon',flat=True)

        n_unidades = len(lista_unidades)
        print(f"lista_unidades: {n_unidades} unidades.")
        print(lista_unidades)


        current_time = int(time.time())
        timeFrom = current_time - (tempo * 24 * 3600)
        timeTo = current_time
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
            self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
            return
        
        keep_alive_active = True
        
        def keep_session_alive():
            """Thread function para manter a sessão ativa"""
            while keep_alive_active:
                try:
                    time.sleep(180)
                    
                    if not keep_alive_active:
                        break
                    
                    payload = {
                        "svc": "avl_evts",
                        "sid": sid
                    }
                    
                    response = requests.post(Wialon.API_URL, data=payload, timeout=30)
                    response.raise_for_status()
                    
                    print(f"🔄 {colored('Keep-alive enviado', 'blue')} - {colored(datetime.now().strftime('%H:%M:%S'), 'cyan')}")
                    
                except requests.RequestException as e:
                    print(f"⚠️ Erro no keep-alive: {e}")
                except Exception as e:
                    print(f"⚠️ Erro inesperado no keep-alive: {e}")
        
        keep_alive_thread = threading.Thread(target=keep_session_alive, daemon=True)
        keep_alive_thread.start()
        
        try:
            for unidade_id in lista_unidades:
                unidade_nome = Veiculo.objects.filter(id_wialon=unidade_id).first().nm
                print(f"\nProcessando unidade ID: {colored(unidade_id, 'cyan')} - Nome: {colored(unidade_nome, 'yellow')}")

                # Remover layer anterior
                payload = {
                    "svc": "render/remove_layer",
                    "params": json.dumps({"layerName": "messages"}),
                    "sid": sid
                }
                try:
                    response = requests.post(Wialon.API_URL, data=payload)
                    response.raise_for_status()
                    result = response.json()
                    print("Response 01:", result)
                except requests.RequestException as e:
                    print("Error:", e)
                    continue

                # Update custom property
                payload = {
                    "svc": "item/update_custom_property",
                    "params": json.dumps({
                        "itemId": unidade_id,
                        "name": "lastmsgl",
                        "value": f'{{"u":{unidade_id},"t":"data","s":0}}'
                    }),
                    "sid": sid
                }
                try:
                    response = requests.post(Wialon.API_URL, data=payload)
                    response.raise_for_status()
                    result = response.json()
                    print("Response 02:", result)
                except requests.RequestException as e:
                    print("Error:", e)
                    continue

                # Create messages layer
                payload = {
                    "svc": "render/create_messages_layer",
                    "params": json.dumps({
                        "layerName": "messages",
                        "itemId": unidade_id,
                        "timeFrom": timeFrom,
                        "timeTo": timeTo,
                        "tripDetector": 0,
                        "flags": 0,
                        "trackWidth": 4,
                        "trackColor": "speed",
                        "annotations": 0,
                        "points": 1,
                        "pointColor": "cc0000ff",
                        "arrows": 1
                    }),
                    "sid": sid
                }
                try:
                    response = requests.post(Wialon.API_URL, data=payload)
                    response.raise_for_status()
                    result = response.json()
                    print("Response 03:", result)
                    contagem_mensagens = result.get('units', [])[0].get('msgs', {}).get('count', 0) if result.get('units') else 0
                    print(f"Contagem de mensagens para a unidade {unidade_id}:", colored(contagem_mensagens, 'green'))
                except requests.RequestException as e:
                    print("Error:", e)
                    continue

                # Get messages
                payload = {
                    "svc": "render/get_messages",
                    "params": json.dumps({
                        "indexFrom": 0,
                        "indexTo": contagem_mensagens,
                        "layerName": "messages",
                        "unitId": unidade_id
                    }),
                    "sid": sid
                }
                try:
                    response = requests.post(Wialon.API_URL, data=payload)
                    response.raise_for_status()
                    result = response.json()


                    if result and isinstance(result, list):
                        df_messages = self.processar_mensagens_wialon(result)

                        unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                        if unidade_obj and not df_messages.empty:
                            viagens_criar = []
                            
                            for _, row in df_messages.iterrows():
                                try:
                                    rpm_valor = float(row.get('can_rpm', 0)) if pd.notna(row.get('can_rpm')) else 0
                                    velocidade_valor = float(row.get('speed', 0)) if pd.notna(row.get('speed')) else 0
                                    altitude_valor = float(row.get('altitude', 0)) if pd.notna(row.get('altitude')) else 0
                                    energia_valor = int(row.get('power', 0)) if pd.notna(row.get('power')) else 0
                                    timestamp_valor = int(row.get('timestamp', 0)) if pd.notna(row.get('timestamp')) else 0
                                    avl_driver_valor = int(row.get('avl_driver', 0)) if pd.notna(row.get('avl_driver')) else 0
                                    rpm_tratado = float(row.get('can_rpm_readable', 0)) if pd.notna(row.get('can_rpm_readable')) else 0
                                    # Classificar a viagem
                                    classificacao = classificar_viagem(rpm_tratado, velocidade_valor)
                                    
                                    # Converter avl_driver para driver_code
                                    driver_code_valor = avl_to_driver_code(avl_driver_valor)
                                    
                                    # Buscar motorista pelo driver_code
                                    nome_motorista_obj = None
                                    if driver_code_valor and driver_code_valor != 0:
                                        try:
                                            nome_motorista_obj = Driver.objects.filter(
                                                codigo=driver_code_valor,
                                                empresa=unidade_obj.empresa
                                            ).first()
                                        except Driver.DoesNotExist:
                                            pass
                                    
                                    viagem = Viagem_eco(
                                        unidade=unidade_obj,
                                        timestamp=timestamp_valor,
                                        rpm=rpm_valor,
                                        velocidade=velocidade_valor,
                                        altitude=altitude_valor,
                                        energia=energia_valor,
                                        avl_driver=avl_driver_valor,
                                        driver_code=driver_code_valor,
                                        nome_motorista=nome_motorista_obj,
                                        # Aplicar classificações
                                        ocioso=classificacao['ocioso'],
                                        faixa_azul=classificacao['faixa_azul'],
                                        faixa_verde=classificacao['faixa_verde'],
                                        faixa_amarela=classificacao['faixa_amarela'],
                                        faixa_vermelha=classificacao['faixa_vermelha']
                                    )
                                    viagens_criar.append(viagem)
                                    
                                except Exception as e:
                                    print(f"Erro ao processar mensagem: {e}")
                                    continue
                            
                            # Criar todas as viagens de uma vez
                            if viagens_criar:
                                Viagem_eco.objects.bulk_create(viagens_criar, ignore_conflicts=True)
                                print(f"✅ {colored(f'{len(viagens_criar)} viagens ecológicas criadas para {unidade_nome}', 'green')}")
                                
                                # Estatísticas de classificação
                                total_viagens = len(viagens_criar)
                                ocioso_count = sum(1 for v in viagens_criar if v.ocioso)
                                azul_count = sum(1 for v in viagens_criar if v.faixa_azul)
                                verde_count = sum(1 for v in viagens_criar if v.faixa_verde)
                                amarela_count = sum(1 for v in viagens_criar if v.faixa_amarela)
                                vermelha_count = sum(1 for v in viagens_criar if v.faixa_vermelha)
                                
                                print(f"\n📊 Estatísticas de classificação:")
                                print(f"   🔵 Ocioso: {colored(ocioso_count, 'cyan')} ({colored(f'{ocioso_count/total_viagens*100:.1f}%', 'cyan')})")
                                print(f"   🔵 Faixa Azul: {colored(azul_count, 'blue')} ({colored(f'{azul_count/total_viagens*100:.1f}%', 'blue')})")
                                print(f"   🟢 Faixa Verde: {colored(verde_count, 'green')} ({colored(f'{verde_count/total_viagens*100:.1f}%', 'green')})")
                                print(f"   🟡 Faixa Amarela: {colored(amarela_count, 'yellow')} ({colored(f'{amarela_count/total_viagens*100:.1f}%', 'yellow')})")
                                print(f"   🔴 Faixa Vermelha: {colored(vermelha_count, 'red')} ({colored(f'{vermelha_count/total_viagens*100:.1f}%', 'red')})")

                        print(f"\nDataFrame criado com {len(df_messages)} mensagens:")
                        print(df_messages.head())
                        

                        print(f"\nEstatísticas das mensagens:")
                        print(f"Período: {df_messages['datetime'].min()} até {df_messages['datetime'].max()}")
                        print(f"Velocidade média: {df_messages['speed'].mean():.2f} km/h")
                        print(f"RPM médio: {df_messages['can_rpm_readable'].mean():.0f}" if 'can_rpm_readable' in df_messages.columns else "RPM não disponível")
                        print(f"Consumo médio de combustível: {df_messages['can_fuel_rate'].mean():.2f} l/h" if 'can_fuel_rate' in df_messages.columns else "Consumo não disponível")
                        print(f"Temperatura média do motor: {df_messages['can_coolant_temp'].mean():.2f} °C" if 'can_coolant_temp' in df_messages.columns else "Temperatura não disponível")
                        print(f"Distância percorrida (odômetro): {df_messages['odometer_km'].iloc[-1] - df_messages['odometer_km'].iloc[0]:.2f} km" if 'odometer_km' in df_messages.columns else "Odômetro não disponível")
                        print(f"Tempo médio entre mensagens: {((df_messages['timestamp'].iloc[-1] - df_messages['timestamp'].iloc[0]) / len(df_messages)):.2f} segundos")
                        
                        counter += 1
                        print("Unidades processadas com sucesso até agora:", colored(counter, 'yellow'), "/", colored(n_unidades, 'green'))
                    else:
                        print("Nenhuma mensagem para processar")

                except requests.RequestException as e:
                    print("Error:", e)
                    continue
                except Exception as e:
                    print(f"Erro ao processar unidade {unidade_id}: {e}")
                    continue

            print("Total de unidades processadas com sucesso:", colored(counter, 'blue'), "/", colored(n_unidades, 'green'))

        finally:
            keep_alive_active = False
            if keep_alive_thread.is_alive():
                keep_alive_thread.join(timeout=5)
            
            print(f"🔄 {colored('Keep-alive finalizado', 'blue')}")
            
            Wialon.wialon_logout(sid)



###-----------------------------------------------------------------------------------------------------------------#####
# INVESTIGAÇÃO #
        #######################################################################################

    ############################################################################################
    ###+---------------------------------------------------------------------------------------------+
    # DEMOLIÇÃO #



    # DEMOLIÇÃO #
    ###+---------------------------------------------------------------------------------------------+
    ############################################################################################
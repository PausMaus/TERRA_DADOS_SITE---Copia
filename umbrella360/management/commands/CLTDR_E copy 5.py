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
        #self.Limpeza() 

        #self.CLTDR_TESTE_01(cor1="blue", cor2="green")
        #self.CLTDR_TESTE_02(cor1="blue", cor2="green")
        ##################################################
        # MENSAGENS #
        
        self.MENSAGENS_04(1)

        ##################################################
        # ESTUDO #



        #self.ESTUDO_01()
        #self.ESTUDO_02()
        #self.ESTUDO_03()
        ##################################################
        # CHECAGEM #
        #self.Checagem_01()
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




    def driver_code_to_avl(self, codigo_motorista: int) -> int:
        # converte para hex e garante 8 caracteres
        hex_code = f'{codigo_motorista:08x}'
        # cria uma string de 16 bytes com o código no meio
        # exemplo: prefixo + hex_code + sufixo
        # aqui usamos um padrão que gera o mesmo resultado
        reversed_bytes = '000000' + hex_code + '000000'
        # inverte os bytes novamente
        bytes_list = [reversed_bytes[i:i+2] for i in range(0, len(reversed_bytes), 2)]
        original_hex = ''.join(bytes_list[::-1])
        # converte para decimal
        return int(original_hex, 16)










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
        #self.CLTDR_empresas(self, sid, "orange" , "white", tool= "CLTDR_empresas")

        Wialon.wialon_logout(sid)

    def CLTDR_empresas(self, sid, cor1, cor2, tool="CLTDR_UMBRELLA"):
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
        dias = range(1,10)
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
                            'período': periodo,

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

    def TESTE_MENSAGENS(self, tempo):
        counter = 0
        # procura apenas unidade com nome que inclua "PRO"
        #lista_unidades = Veiculo.objects.filter(empresa__nome="CPBRACELL", nm__icontains="PRO").values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas
        lista_unidades = Veiculo.objects.filter(empresa__nome="Petitto").values_list('id_wialon', flat=True)[:2]  # IDs das unidades a serem processadas

        n_unidades = len(lista_unidades)
        print(f"lista_unidades: {n_unidades} unidades.")
        print(lista_unidades)


        current_time = int(time.time())
        timeFrom = current_time - (tempo * 24 * 3600)  
        timeTo = current_time  # Agora
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
            self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
            return
        
        #################################################
        for unidade_id in lista_unidades:
            unidade_nome = Veiculo.objects.filter(id_wialon=unidade_id).first().nm
            print(f"\nProcessando unidade ID: {colored(unidade_id, 'cyan')} - Nome: {colored(unidade_nome, 'yellow')}")

            payload = {
                "svc": "render/remove_layer",
                "params": json.dumps({
                    "layerName":"messages"
                }),
                "sid": sid
            }
            try:
                response = requests.post(Wialon.API_URL, data=payload)
                response.raise_for_status()
                result = response.json()
                print("Response 01:", result)
            except requests.RequestException as e:
                print("Error:", e)
                return

                ##################################################
            
            payload = {
                "svc": "item/update_custom_property",
                "params": json.dumps({
                    #"itemId":unidade_id,"name":"lastmsgl","value":"{\"u\":401970473,\"t\":\"data\",\"s\":0}" 
                    "itemId": unidade_id, "name": "lastmsgl", "value": f'{{"u":{unidade_id},"t":"data","s":0}}'

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
                return

            ##################################################

            payload = {
                "svc": "render/create_messages_layer",
                "params": json.dumps({
                    "layerName":"messages","itemId":unidade_id,"timeFrom":timeFrom,"timeTo":timeTo,"tripDetector":0,"flags":0,"trackWidth":4,"trackColor":"speed","annotations":0,"points":1,"pointColor":"cc0000ff","arrows":1
                }),
                "sid": sid
            }
            try:
                response = requests.post(Wialon.API_URL, data=payload)
                response.raise_for_status()
                result = response.json()
                print("Response 03:", result)
                #exemplo de resultado:
                #{'name': 'messages', 'bounds': [-24.1431566, -49.45541, -23.84126, -49.31901], 'units': [{'id': 401970473, 'msgs': {'count': 14499, 'first': {'time': 1757034264, 'lat': -24.1347770691, 'lon': -49.4387168884}, 'last': {'time': 1757819133, 'lat': -23.8940887451, 'lon': -49.3677978516}}, 'mileage': 3467888.96775, 'max_speed': 81}]}}
                #recuperar a contagem de mensagens
                contagem_mensagens = result.get('units', [])[0].get('msgs', {}).get('count', 0) if result.get('units') else 0
                print(f"Contagem de mensagens para a unidade {unidade_id}:", colored(contagem_mensagens, 'green'))
            except requests.RequestException as e:
                print("Error:", e)
                return

            ###################################################
            # Sua última requisição que retorna as mensagens
            payload = {
                "svc": "render/get_messages",
                "params": json.dumps({
                    "indexFrom":0,"indexTo":contagem_mensagens,"layerName":"messages","unitId":unidade_id
                }),
                "sid": sid
            }
            try:
                response = requests.post(Wialon.API_URL, data=payload)
                response.raise_for_status()
                result = response.json()
                #print("Response 04:", result)
                
                # Processa as mensagens e cria o DataFrame
                if result and isinstance(result, list):
                    df_messages = self.processar_mensagens_wialon(result)

                    #atualiza o model Viagem_eco de acordo com a unidade_id = unidade_id_wialon
                    unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                    if unidade_obj:
                        for index, row in df_messages.iterrows():
                            unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                            timestamp = str(row['timestamp'])
                            can_rpm_readable = float(row['can_rpm_readable']) if 'can_rpm_readable' in row and pd.notna(row['can_rpm_readable']) else 0.0
                            speed = float(row['speed']) if 'speed' in row and pd.notna(row['speed']) else 0.0
                            altitude = float(row['altitude']) if 'altitude' in row and pd.notna(row['altitude']) else 0.0
                            
                            # Atualiza ou cria a viagem correspondente
                            Viagem_eco.objects.update_or_create(
                                unidade_id=unidade_obj.id,
                                defaults={
                                    'timestamp': timestamp,
                                    'rpm': can_rpm_readable,
                                    'speed': speed,
                                    'altitude': altitude,
                                }
                            )
                    



                    print(f"\nDataFrame criado com {len(df_messages)} mensagens:")
                    print(df_messages.head())
                    
                    # Salva em Excel para análise
                    df_messages.to_excel(f'{deposito}/{unidade_nome}_{unidade_id}.xlsx', index=False)
                    print(f"DataFrame salvo em {deposito}/{unidade_nome}_{unidade_id}.xlsx")

                    # Mostra algumas estatísticas
                    print(f"\nEstatísticas das mensagens:")
                    print(f"Período: {df_messages['datetime'].min()} até {df_messages['datetime'].max()}")
                    print(f"Velocidade média: {df_messages['speed'].mean():.2f} km/h")
                    print(f"RPM médio: {df_messages['can_rpm'].mean():.0f}" if 'can_rpm' in df_messages.columns else "RPM não disponível")
                    # 
                    print(f"Consumo médio de combustível: {df_messages['can_fuel_rate'].mean():.2f} l/h" if 'can_fuel_rate' in df_messages.columns else "Consumo não disponível")
                    print(f"Temperatura média do motor: {df_messages['can_coolant_temp'].mean():.2f} °C" if 'can_coolant_temp' in df_messages.columns else "Temperatura não disponível")
                    print(f"Distância percorrida (odômetro): {df_messages['odometer_km'].iloc[-1] - df_messages['odometer_km'].iloc[0]:.2f} km" if 'odometer_km' in df_messages.columns else "Odômetro não disponível")
                    #tempo médio entre mensagens
                    print(f"Tempo médio entre mensagens: {((df_messages['timestamp'].iloc[-1] - df_messages['timestamp'].iloc[0]) / len(df_messages)):.2f} segundos")
                    #print(f"Distância CAN: {df_messages['can_distance'].iloc[-1] - df_messages['can_distance'].iloc[0]} metros" if 'can_distance' in df_messages.columns else "Distância não disponível")
                    
                    counter += 1
                    print("Unidades processadas com sucesso até agora:", colored(counter, 'yellow'), "/", colored(n_unidades, 'green'))
                else:
                    print("Nenhuma mensagem para processar")


            except requests.RequestException as e:
                print("Error:", e)
                return df_messages
        print("Total de unidades processadas com sucesso:", colored(counter, 'blue'), "/", colored(n_unidades, 'green'))
        
        #média entre mensagens
        print(f"Tempo médio entre mensagens: {((df_messages['timestamp'].iloc[-1] - df_messages['timestamp'].iloc[0]) / len(df_messages)):.2f} segundos")




        Wialon.wialon_logout(sid)



    def TESTE_MENSAGENS_02(self, tempo):
        counter = 0
        # procura apenas unidade com nome que inclua "PRO"
        #lista_unidades = Veiculo.objects.filter(empresa__nome="CPBRACELL", nm__icontains="PRO").values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas
        lista_unidades = Veiculo.objects.filter(empresa__nome="Petitto").values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas
        #lista todos os veículos
        #lista_unidades = Veiculo.objects.all().values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas

        n_unidades = len(lista_unidades)
        print(f"lista_unidades: {n_unidades} unidades.")
        print(lista_unidades)

        current_time = int(time.time())
        timeFrom = current_time - (tempo * 24 * 3600)  
        timeTo = current_time  # Agora
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
            self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
            return
        
        #################################################
        for unidade_id in lista_unidades:


            unidade_nome = Veiculo.objects.filter(id_wialon=unidade_id).first().nm
            print(f"\nProcessando unidade ID: {colored(unidade_id, 'cyan')} - Nome: {colored(unidade_nome, 'yellow')}")

            payload = {
                "svc": "render/remove_layer",
                "params": json.dumps({
                    "layerName":"messages"
                }),
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

            ##################################################
            
            payload = {
                "svc": "item/update_custom_property",
                "params": json.dumps({
                    "itemId": unidade_id, "name": "lastmsgl", "value": f'{{"u":{unidade_id},"t":"data","s":0}}'
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

            ##################################################

            payload = {
                "svc": "render/create_messages_layer",
                "params": json.dumps({
                    "layerName":"messages","itemId":unidade_id,"timeFrom":timeFrom,"timeTo":timeTo,"tripDetector":0,"flags":0,"trackWidth":4,"trackColor":"speed","annotations":0,"points":1,"pointColor":"cc0000ff","arrows":1
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

            ###################################################
            # Requisição que retorna as mensagens
            payload = {
                "svc": "render/get_messages",
                "params": json.dumps({
                    "indexFrom":0,"indexTo":contagem_mensagens,"layerName":"messages","unitId":unidade_id
                }),
                "sid": sid
            }
            try:
                response = requests.post(Wialon.API_URL, data=payload)
                response.raise_for_status()
                result = response.json()

                #print("Response 04:", result)
                # salva como json
                with open(f'{deposito}/messages_{unidade_nome}_{unidade_id}.json', 'w') as f:
                    json.dump(result, f, indent=4)

                
                # Processa as mensagens e cria o DataFrame
                if result and isinstance(result, list):
                    df_messages = self.processar_mensagens_wialon(result)

                    # CORREÇÃO: Atualiza o model Viagem_eco com TODOS os registros
                    unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                    if unidade_obj and not df_messages.empty:
                        registros_criados = 0
                        registros_atualizados = 0
                        
                        for index, row in df_messages.iterrows():
                            timestamp = str(row['timestamp'])
                            can_rpm_readable = float(row['can_rpm_readable']) if 'can_rpm_readable' in row and pd.notna(row['can_rpm_readable']) else 0.0
                            

                            # Atualiza ou cria usando timestamp como chave única também
                            viagem_eco, created = Viagem_eco.objects.update_or_create(
                                unidade_id=unidade_obj.id,
                                timestamp=timestamp,  # IMPORTANTE: Incluir timestamp na busca
                                defaults={
                                    'rpm': can_rpm_readable,
                                    'velocidade': float(row['speed']) if 'speed' in row and pd.notna(row['speed']) else 0.0,
                                    'altitude': float(row['altitude']) if 'altitude' in row and pd.notna(row['altitude']) else 0.0,
                                }
                            )
                            
                            if created:
                                registros_criados += 1
                            else:
                                registros_atualizados += 1
                        
                        print(f"✅ Unidade {unidade_nome}: {colored(registros_criados, 'green')} novos registros, {colored(registros_atualizados, 'yellow')} atualizados")

                    print(f"\nDataFrame criado com {len(df_messages)} mensagens:")
                    print(df_messages.head())
                    
                    # Salva em Excel para análise
                    df_messages.to_excel(f'{deposito}/{unidade_nome}_{unidade_id}.xlsx', index=False)
                    print(f"DataFrame salvo em {deposito}/{unidade_nome}_{unidade_id}.xlsx")

                    # Mostra algumas estatísticas
                    print(f"\nEstatísticas das mensagens:")
                    print(f"Período: {df_messages['datetime'].min()} até {df_messages['datetime'].max()}")
                    print(f"Velocidade média: {df_messages['speed'].mean():.2f} km/h")
                    print(f"RPM médio: {df_messages['can_rpm'].mean():.0f}" if 'can_rpm' in df_messages.columns else "RPM não disponível")
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

        Wialon.wialon_logout(sid)

    def MENSAGENS_04(self, tempo):
        
        def avl_to_driver_code(avl_driver: int) -> int:
            """Converte código AVL para código do motorista"""
            try:
                if not avl_driver or avl_driver == 0:
                    return 0
                
                hex_str = hex(avl_driver)[2:] # remove '0x'
                # garante que tenha número par de caracteres
                if len(hex_str) % 2 != 0:
                    hex_str = '0' + hex_str
                    # inverte os bytes
                reversed_bytes = ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
                # extrai da posição 6 os próximos 8 caracteres
                if len(reversed_bytes) >= 14:
                    substr = reversed_bytes[6:14]
                     # converte para decimal
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

        lista_cpbracell = Veiculo.objects.filter(empresa__nome="CPBRACELL").values_list('id_wialon', flat=True)
        lista_petitto = Veiculo.objects.filter(empresa__nome="Petitto").values_list('id_wialon', flat=True)
        lista_sfresgate = Veiculo.objects.filter(empresa__nome="São Francisco Resgate").values_list('id_wialon', flat=True)

        lista_unidades = list(lista_sfresgate) + list(lista_petitto) + list(lista_cpbracell)
        #lista_unidades = Veiculo.objects.filter(empresa__nome="CPBRACELL", nm__icontains="PRO").values_list('id_wialon', flat=True)[:10]

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
                    # Aguarda 3 minutos (180 segundos)
                    time.sleep(180)
                    
                    if not keep_alive_active:
                        break
                    
                    # Faz requisição para manter a sessão
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
        
        # Inicia thread do keep-alive
        keep_alive_thread = threading.Thread(target=keep_session_alive, daemon=True)
        keep_alive_thread.start()
        
        try:
            #################################################
            for unidade_id in lista_unidades:
                unidade_nome = Veiculo.objects.filter(id_wialon=unidade_id).first().nm
                print(f"\nProcessando unidade ID: {colored(unidade_id, 'cyan')} - Nome: {colored(unidade_nome, 'yellow')}")

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

                ##################################################
                
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

                ##################################################

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

                    with open(f'{deposito}/messages_{unidade_nome}_{unidade_id}.json', 'w') as f:
                        json.dump(result, f, indent=4)

                    if result and isinstance(result, list):
                        df_messages = self.processar_mensagens_wialon(result)

                        # Atualiza o model Viagem_eco
                        unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                        
                        if unidade_obj and not df_messages.empty:
                            registros_criados = 0
                            registros_atualizados = 0
                            
                            # 🔥 CRIAR UM DICIONÁRIO DE CACHE PARA DRIVERS
                            # Isso evita múltiplas consultas ao banco de dados
                            drivers_cache = {}
                            
                            for index, row in df_messages.iterrows():
                                timestamp = str(row['timestamp'])
                                
                                # Converter avl_driver usando a função
                                avl_driver_raw = row.get('avl_driver', 0)
                                
                                try:
                                    avl_driver_value = float(avl_driver_raw) if pd.notna(avl_driver_raw) else 0.0
                                    avl_driver_int = int(avl_driver_value)
                                    driver_code = avl_to_driver_code(avl_driver_int)
                                except (ValueError, TypeError):
                                    avl_driver_value = 0.0
                                    driver_code = 0
                                
                                # 🔥 BUSCAR O DRIVER PELO CÓDIGO (COM CACHE)
                                driver_instance = None
                                
                                if driver_code and driver_code != 0:
                                    # Verifica se já está no cache
                                    if driver_code in drivers_cache:
                                        driver_instance = drivers_cache[driver_code]
                                    else:
                                        # Busca no banco de dados
                                        try:
                                            # Busca o Driver que pertence à mesma empresa da unidade
                                            driver_instance = Driver.objects.filter(
                                                codigo=driver_code,
                                                empresa=unidade_obj.empresa
                                            ).first()
                                            
                                            # Adiciona ao cache (mesmo que seja None)
                                            drivers_cache[driver_code] = driver_instance
                                            
                                            if driver_instance:
                                                print(f"✅ Driver encontrado: {driver_instance.nm} (código: {driver_code})")
                                            else:
                                                print(f"⚠️ Driver não encontrado para código: {driver_code}")
                                                
                                        except Driver.DoesNotExist:
                                            print(f"❌ Driver com código {driver_code} não existe")
                                            drivers_cache[driver_code] = None
                                
                                # Atualiza ou cria usando timestamp como chave única
                                viagem_eco, created = Viagem_eco.objects.update_or_create(
                                    unidade_id=unidade_obj.id,
                                    timestamp=timestamp,
                                    defaults={
                                        'rpm': float(row['can_rpm']) if 'can_rpm' in row and pd.notna(row['can_rpm']) else 0.0,
                                        'velocidade': float(row['speed']) if 'speed' in row and pd.notna(row['speed']) else 0.0,
                                        'altitude': float(row['altitude']) if 'altitude' in row and pd.notna(row['altitude']) else 0.0,
                                        'energia': float(row['power']) if 'power' in row and pd.notna(row['power']) else 0.0,
                                        'avl_driver': avl_driver_value,  # Valor original
                                        'driver_code': driver_code,  # Valor convertido
                                        'nome_motorista': driver_instance,  # 🔥 RELACIONAMENTO COM DRIVER
                                    }
                                )
                                
                                if created:
                                    registros_criados += 1
                                else:
                                    registros_atualizados += 1
                            
                            print(f"📊 Viagem_eco atualizada: {registros_criados} criados, {registros_atualizados} atualizados")
                            print(f"👥 Drivers únicos encontrados: {len([d for d in drivers_cache.values() if d is not None])}")

                            
                            print(f"✅ Unidade {unidade_nome}: {colored(registros_criados, 'green')} novos registros, {colored(registros_atualizados, 'yellow')} atualizados")

                        print(f"\nDataFrame criado com {len(df_messages)} mensagens:")
                        print(df_messages.head())
                        
                        # Salva em Excel para análise
                        #+---
                        #df_messages.to_excel(f'{deposito}/{unidade_nome}_{unidade_id}.xlsx', index=False)
                        #print(f"DataFrame salvo em {deposito}/{unidade_nome}_{unidade_id}.xlsx")
                        #+---
                        
                        # Mostra algumas estatísticas
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
            # Para o keep-alive e aguarda a thread finalizar
            keep_alive_active = False
            if keep_alive_thread.is_alive():
                keep_alive_thread.join(timeout=5)
            
            print(f"🔄 {colored('Keep-alive finalizado', 'blue')}")
            
            Wialon.wialon_logout(sid)




    def ESTUDO_01(self):
        """
        Análise estatística completa dos dados de Viagem_eco
        - Detecção de outliers
        - Análise de padrões
        - Estatísticas descritivas
        - Correlações entre variáveis
        - Análise temporal
        """
        print(colored("="*50, 'cyan'))
        print(colored("INICIANDO ESTUDO ESTATÍSTICO COMPLETO", 'yellow'))
        print(colored("="*50, 'cyan'))
        
        # Importações necessárias
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.ensemble import IsolationForest
        import warnings
        warnings.filterwarnings('ignore')
        
        # Configurar matplotlib para não mostrar gráficos
        plt.ioff()
        
        try:
            # ============= COLETA DE DADOS =============
            print(f"📊 {colored('Coletando dados do banco...', 'blue')}")
            
            # Buscar todos os dados de Viagem_eco
            viagens_eco = Viagem_eco.objects.all().select_related('unidade')
            
            if not viagens_eco.exists():
                print(f"❌ {colored('Nenhum dado encontrado na tabela Viagem_eco', 'red')}")
                return
            
            # Converter para DataFrame
            data_list = []
            for viagem in viagens_eco:
                try:
                    # Converter timestamp unix para datetime
                    timestamp_int = int(viagem.timestamp)
                    dt = datetime.fromtimestamp(timestamp_int)
                    
                    # Filtrar apenas dados com RPM válidos (acima de 300)
                    if viagem.rpm and float(viagem.rpm) >= 300:
                        data_list.append({
                            'timestamp': timestamp_int,
                            'datetime': dt,
                            'unidade_id': viagem.unidade.id,
                            'unidade_nome': viagem.unidade.nm,
                            'empresa': viagem.unidade.empresa.nome if viagem.unidade.empresa else 'N/A',
                            'rpm': float(viagem.rpm),
                            'velocidade': float(viagem.velocidade) if viagem.velocidade else 0.0,
                            'altitude': float(viagem.altitude) if viagem.altitude else 0.0,
                            'hora': dt.hour,
                            'dia_semana': dt.weekday(),
                            'mes': dt.month,
                            'ano': dt.year,
                        })
                except (ValueError, TypeError, OSError):
                    continue
            
            if not data_list:
                print(f"❌ {colored('Nenhum dado válido encontrado', 'red')}")
                return
            
            df = pd.DataFrame(data_list)
            print(f"✅ {colored(f'Dados coletados: {len(df)} registros de {df.unidade_id.nunique()} unidades', 'green')}")
            
            # ============= ANÁLISE DESCRITIVA BÁSICA =============
            print(f"\n📈 {colored('Gerando estatísticas descritivas...', 'blue')}")
            
            stats_desc = df[['rpm', 'velocidade', 'altitude']].describe()
            
            # Função para calcular MAD (Mean Absolute Deviation) manualmente
            def calculate_mad(series):
                """Calcula o desvio absoluto mediano"""
                median = series.median()
                return (series - median).abs().median()
            
            # Adicionar estatísticas extras
            stats_extras = pd.DataFrame({
                'rpm': [
                    df['rpm'].var(),
                    df['rpm'].skew(),
                    df['rpm'].kurtosis(),
                    calculate_mad(df['rpm'])  # CORREÇÃO: Usar função personalizada
                ],
                'velocidade': [
                    df['velocidade'].var(),
                    df['velocidade'].skew(),
                    df['velocidade'].kurtosis(),
                    calculate_mad(df['velocidade'])  # CORREÇÃO: Usar função personalizada
                ],
                'altitude': [
                    df['altitude'].var(),
                    df['altitude'].skew(),
                    df['altitude'].kurtosis(),
                    calculate_mad(df['altitude'])  # CORREÇÃO: Usar função personalizada
                ]
            }, index=['variancia', 'assimetria', 'curtose', 'desvio_abs_mediano'])
            
            stats_completas = pd.concat([stats_desc, stats_extras])
            
            # Salvar estatísticas descritivas
            stats_completas.to_excel(f'{deposito}/estudo_01_estatisticas_descritivas.xlsx')
            print(f"💾 Estatísticas descritivas salvas em: estudo_01_estatisticas_descritivas.xlsx")
            
            # ============= DETECÇÃO DE OUTLIERS =============
            print(f"\n🔍 {colored('Detectando outliers...', 'blue')}")
            
            # Método 1: Z-Score
            z_scores = np.abs(stats.zscore(df[['rpm', 'velocidade', 'altitude']]))
            outliers_zscore = df[(z_scores > 3).any(axis=1)].copy()
            
            # Método 2: IQR (Interquartile Range)
            outliers_iqr = pd.DataFrame()
            for coluna in ['rpm', 'velocidade', 'altitude']:
                Q1 = df[coluna].quantile(0.25)
                Q3 = df[coluna].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_col = df[(df[coluna] < lower_bound) | (df[coluna] > upper_bound)]
                outliers_iqr = pd.concat([outliers_iqr, outliers_col]).drop_duplicates()
            
            # Método 3: Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers_iso = iso_forest.fit_predict(df[['rpm', 'velocidade', 'altitude']])
            outliers_isolation = df[outliers_iso == -1].copy()
            
            # Combinar todos os outliers
            all_outliers = pd.concat([outliers_zscore, outliers_iqr, outliers_isolation]).drop_duplicates()
            all_outliers['metodo_deteccao'] = 'Múltiplos'
            
            print(f"🎯 Outliers detectados:")
            print(f"   - Z-Score (>3): {len(outliers_zscore)} registros")
            print(f"   - IQR: {len(outliers_iqr)} registros")
            print(f"   - Isolation Forest: {len(outliers_isolation)} registros")
            print(f"   - Total únicos: {len(all_outliers)} registros")
            
            # Salvar outliers
            all_outliers.to_excel(f'{deposito}/estudo_01_outliers_detectados.xlsx', index=False)
            print(f"💾 Outliers salvos em: estudo_01_outliers_detectados.xlsx")
            
            # ============= ANÁLISE POR UNIDADE =============
            print(f"\n🚛 {colored('Analisando padrões por unidade...', 'blue')}")
            
            stats_por_unidade = df.groupby(['unidade_nome', 'empresa']).agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
            }).round(2)
            
            # Achatar colunas multi-nível
            stats_por_unidade.columns = ['_'.join(col).strip() for col in stats_por_unidade.columns]
            stats_por_unidade = stats_por_unidade.reset_index()
            
            # Adicionar classificações
            stats_por_unidade['rpm_categoria'] = pd.cut(
                stats_por_unidade['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Baixo', 'Econômico', 'Normal', 'Alto']
            )
            
            stats_por_unidade['velocidade_categoria'] = pd.cut(
                stats_por_unidade['velocidade_mean'], 
                bins=[0, 40, 60, 80, float('inf')], 
                labels=['Baixa', 'Moderada', 'Alta', 'Muito Alta']
            )
            
            # Salvar análise por unidade
            stats_por_unidade.to_excel(f'{deposito}/estudo_01_analise_por_unidade.xlsx', index=False)
            print(f"💾 Análise por unidade salva em: estudo_01_analise_por_unidade.xlsx")
            
            # ============= ANÁLISE TEMPORAL =============
            print(f"\n⏰ {colored('Analisando padrões temporais...', 'blue')}")
            
            # Por hora do dia
            analise_hora = df.groupby('hora').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_hora.columns = ['_'.join(col).strip() for col in analise_hora.columns]
            analise_hora = analise_hora.reset_index()
            
            # Por dia da semana
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            analise_dia_semana = df.groupby('dia_semana').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_dia_semana.columns = ['_'.join(col).strip() for col in analise_dia_semana.columns]
            analise_dia_semana = analise_dia_semana.reset_index()
            analise_dia_semana['dia_nome'] = analise_dia_semana['dia_semana'].map(lambda x: dias_semana[x])
            
            # Por mês
            analise_mes = df.groupby('mes').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_mes.columns = ['_'.join(col).strip() for col in analise_mes.columns]
            analise_mes = analise_mes.reset_index()
            
            # Salvar análises temporais
            with pd.ExcelWriter(f'{deposito}/estudo_01_analise_temporal.xlsx') as writer:
                analise_hora.to_excel(writer, sheet_name='Por_Hora', index=False)
                analise_dia_semana.to_excel(writer, sheet_name='Por_Dia_Semana', index=False)
                analise_mes.to_excel(writer, sheet_name='Por_Mes', index=False)
            
            print(f"💾 Análise temporal salva em: estudo_01_analise_temporal.xlsx")
            
            # ============= ANÁLISE DE CORRELAÇÕES =============
            print(f"\n🔗 {colored('Analisando correlações...', 'blue')}")
            
            # Matriz de correlação
            correlation_matrix = df[['rpm', 'velocidade', 'altitude', 'hora', 'dia_semana']].corr()
            
            # Salvar matriz de correlação
            correlation_matrix.to_excel(f'{deposito}/estudo_01_matriz_correlacao.xlsx')
            print(f"💾 Matriz de correlação salva em: estudo_01_matriz_correlacao.xlsx")
            
            # ============= CLUSTERING ANÁLISE =============
            print(f"\n🎯 {colored('Realizando análise de clusters...', 'blue')}")
            
            # Preparar dados para clustering
            features_clustering = df[['rpm', 'velocidade', 'altitude']].copy()
            
            # Normalizar dados
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features_clustering)
            
            # K-Means com diferentes números de clusters
            inertias = []
            K_range = range(2, 11)
            
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(features_normalized)
                inertias.append(kmeans.inertia_)
            
            # Escolher k=5 para análise detalhada
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_normalized)
            
            # Adicionar clusters ao DataFrame
            df_clusters = df.copy()
            df_clusters['cluster'] = clusters
            
            # Analisar características de cada cluster
            cluster_analysis = df_clusters.groupby('cluster').agg({
                'rpm': ['mean', 'std', 'min', 'max', 'count'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            cluster_analysis.columns = ['_'.join(col).strip() for col in cluster_analysis.columns]
            cluster_analysis = cluster_analysis.reset_index()
            
            # Adicionar interpretação dos clusters
            def interpretar_cluster(row):
                rpm_mean = row['rpm_mean']
                vel_mean = row['velocidade_mean']
                
                if rpm_mean < 800:
                    rpm_cat = "Marcha Lenta"
                elif rpm_mean < 1300:
                    rpm_cat = "Econômico"
                elif rpm_mean < 2000:
                    rpm_cat = "Normal"
                else:
                    rpm_cat = "Alto"
                
                if vel_mean < 20:
                    vel_cat = "Parado/Lento"
                elif vel_mean < 50:
                    vel_cat = "Urbano"
                elif vel_mean < 80:
                    vel_cat = "Rodoviário"
                else:
                    vel_cat = "Alto"
                
                return f"{rpm_cat} + {vel_cat}"
            
            cluster_analysis['interpretacao'] = cluster_analysis.apply(interpretar_cluster, axis=1)
            
            # Salvar análise de clusters
            cluster_analysis.to_excel(f'{deposito}/estudo_01_analise_clusters.xlsx', index=False)
            print(f"💾 Análise de clusters salva em: estudo_01_analise_clusters.xlsx")
            
            # ============= DETECÇÃO DE PADRÕES ESPECÍFICOS =============
            print(f"\n🔍 {colored('Detectando padrões específicos...', 'blue')}")
            
            padroes_especificos = {}
            
            # 1. Padrão de marcha lenta excessiva
            marcha_lenta = df[df['rpm'] < 500]
            padroes_especificos['marcha_lenta_excessiva'] = {
                'total_registros': len(marcha_lenta),
                'unidades_afetadas': marcha_lenta['unidade_nome'].nunique(),
                'percentual_total': round(len(marcha_lenta) / len(df) * 100, 2)
            }
            
            # 2. Padrão de RPM muito alto (zona vermelha)
            rpm_alto = df[df['rpm'] > 2300]
            padroes_especificos['rpm_zona_vermelha'] = {
                'total_registros': len(rpm_alto),
                'unidades_afetadas': rpm_alto['unidade_nome'].nunique(),
                'percentual_total': round(len(rpm_alto) / len(df) * 100, 2)
            }
            
            # 3. Padrão de velocidade alta com RPM baixo (possível descida)
            vel_alta_rpm_baixo = df[(df['velocidade'] > 60) & (df['rpm'] < 1000)]
            padroes_especificos['velocidade_alta_rpm_baixo'] = {
                'total_registros': len(vel_alta_rpm_baixo),
                'unidades_afetadas': vel_alta_rpm_baixo['unidade_nome'].nunique(),
                'percentual_total': round(len(vel_alta_rpm_baixo) / len(df) * 100, 2)
            }
            
            # 4. Padrão noturno (22h às 6h)
            periodo_noturno = df[(df['hora'] >= 22) | (df['hora'] <= 6)]
            padroes_especificos['atividade_noturna'] = {
                'total_registros': len(periodo_noturno),
                'unidades_afetadas': periodo_noturno['unidade_nome'].nunique(),
                'percentual_total': round(len(periodo_noturno) / len(df) * 100, 2)
            }
            
            # 5. Eficiência por faixa de RPM
            df['faixa_rpm'] = pd.cut(
                df['rpm'], 
                bins=[0, 799, 1300, 2300, float('inf')], 
                labels=['Azul (350-799)', 'Verde (800-1300)', 'Amarela (1301-2300)', 'Vermelha (2301+)']
            )
            
            distribuicao_rpm = df['faixa_rpm'].value_counts().to_dict()
            padroes_especificos['distribuicao_faixas_rpm'] = distribuicao_rpm
            
            # Converter para DataFrame e salvar
            padroes_df = pd.DataFrame([padroes_especificos]).T
            padroes_df.to_excel(f'{deposito}/estudo_01_padroes_especificos.xlsx')
            print(f"💾 Padrões específicos salvos em: estudo_01_padroes_especificos.xlsx")
            
            # ============= GERAR GRÁFICOS =============
            print(f"\n📊 {colored('Gerando gráficos de análise...', 'blue')}")
            
            # Configurar estilo dos gráficos
            plt.style.use('default')
            sns.set_palette("husl")
            
            # 1. Distribuições das variáveis principais
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Distribuições das Variáveis Principais', fontsize=16, fontweight='bold')
            
            # RPM
            axes[0, 0].hist(df['rpm'], bins=50, alpha=0.7, color='blue')
            axes[0, 0].set_title('Distribuição RPM')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Frequência')
            axes[0, 0].axvline(df['rpm'].mean(), color='red', linestyle='--', label=f'Média: {df["rpm"].mean():.0f}')
            axes[0, 0].legend()
            
            # Velocidade
            axes[0, 1].hist(df['velocidade'], bins=50, alpha=0.7, color='green')
            axes[0, 1].set_title('Distribuição Velocidade')
            axes[0, 1].set_xlabel('Velocidade (km/h)')
            axes[0, 1].set_ylabel('Frequência')
            axes[0, 1].axvline(df['velocidade'].mean(), color='red', linestyle='--', label=f'Média: {df["velocidade"].mean():.1f}')
            axes[0, 1].legend()
            
            # Altitude
            axes[1, 0].hist(df['altitude'], bins=50, alpha=0.7, color='orange')
            axes[1, 0].set_title('Distribuição Altitude')
            axes[1, 0].set_xlabel('Altitude (m)')
            axes[1, 0].set_ylabel('Frequência')
            axes[1, 0].axvline(df['altitude'].mean(), color='red', linestyle='--', label=f'Média: {df["altitude"].mean():.1f}')
            axes[1, 0].legend()
            
            # Distribuição por faixa de RPM
            faixa_counts = df['faixa_rpm'].value_counts()
            axes[1, 1].pie(faixa_counts.values, labels=faixa_counts.index, autopct='%1.1f%%')
            axes[1, 1].set_title('Distribuição por Faixa de RPM')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_distribuicoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Análise temporal
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise Temporal dos Dados', fontsize=16, fontweight='bold')
            
            # RPM por hora
            hourly_rpm = df.groupby('hora')['rpm'].mean()
            axes[0, 0].plot(hourly_rpm.index, hourly_rpm.values, marker='o', linewidth=2)
            axes[0, 0].set_title('RPM Médio por Hora do Dia')
            axes[0, 0].set_xlabel('Hora')
            axes[0, 0].set_ylabel('RPM Médio')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Velocidade por hora
            hourly_vel = df.groupby('hora')['velocidade'].mean()
            axes[0, 1].plot(hourly_vel.index, hourly_vel.values, marker='s', color='green', linewidth=2)
            axes[0, 1].set_title('Velocidade Média por Hora do Dia')
            axes[0, 1].set_xlabel('Hora')
            axes[0, 1].set_ylabel('Velocidade Média (km/h)')
            axes[0, 1].grid(True, alpha=0.3)
            
            # RPM por dia da semana
            daily_rpm = df.groupby('dia_semana')['rpm'].mean()
            dias_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            axes[1, 0].bar(range(7), daily_rpm.values, color='purple', alpha=0.7)
            axes[1, 0].set_title('RPM Médio por Dia da Semana')
            axes[1, 0].set_xlabel('Dia da Semana')
            axes[1, 0].set_ylabel('RPM Médio')
            axes[1, 0].set_xticks(range(7))
            axes[1, 0].set_xticklabels(dias_nome)
            
            # Atividade por mês
            monthly_count = df.groupby('mes').size()
            axes[1, 1].bar(monthly_count.index, monthly_count.values, color='red', alpha=0.7)
            axes[1, 1].set_title('Atividade por Mês')
            axes[1, 1].set_xlabel('Mês')
            axes[1, 1].set_ylabel('Número de Registros')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_analise_temporal.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. Scatter plots e correlações
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise de Correlações', fontsize=16, fontweight='bold')
            
            # RPM vs Velocidade
            axes[0, 0].scatter(df['rpm'], df['velocidade'], alpha=0.1, s=1)
            axes[0, 0].set_title('RPM vs Velocidade')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Velocidade (km/h)')
            
            # RPM vs Altitude
            axes[0, 1].scatter(df['rpm'], df['altitude'], alpha=0.1, s=1, color='green')
            axes[0, 1].set_title('RPM vs Altitude')
            axes[0, 1].set_xlabel('RPM')
            axes[0, 1].set_ylabel('Altitude (m)')
            
            # Velocidade vs Altitude
            axes[1, 0].scatter(df['velocidade'], df['altitude'], alpha=0.1, s=1, color='red')
            axes[1, 0].set_title('Velocidade vs Altitude')
            axes[1, 0].set_xlabel('Velocidade (km/h)')
            axes[1, 0].set_ylabel('Altitude (m)')
            
            # Heatmap de correlação
            corr_data = df[['rpm', 'velocidade', 'altitude', 'hora']].corr()
            im = axes[1, 1].imshow(corr_data, cmap='coolwarm', aspect='auto')
            axes[1, 1].set_title('Matriz de Correlação')
            axes[1, 1].set_xticks(range(len(corr_data.columns)))
            axes[1, 1].set_yticks(range(len(corr_data.columns)))
            axes[1, 1].set_xticklabels(corr_data.columns)
            axes[1, 1].set_yticklabels(corr_data.columns)
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_correlacoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 Gráficos salvos em:")
            print(f"   - estudo_01_distribuicoes.png")
            print(f"   - estudo_01_analise_temporal.png")
            print(f"   - estudo_01_correlacoes.png")
            
            # ============= RELATÓRIO RESUMO =============
            print(f"\n📋 {colored('Gerando relatório resumo...', 'blue')}")
            
            resumo = {
                'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_registros': len(df),
                'total_unidades': df['unidade_id'].nunique(),
                'total_empresas': df['empresa'].nunique(),
                'periodo_dados': f"{df['datetime'].min()} até {df['datetime'].max()}",
                'rpm_medio_geral': round(df['rpm'].mean(), 2),
                'rpm_desvio_padrao': round(df['rpm'].std(), 2),
                'velocidade_media_geral': round(df['velocidade'].mean(), 2),
                'altitude_media_geral': round(df['altitude'].mean(), 2),
                'outliers_detectados': len(all_outliers),
                'percentual_outliers': round(len(all_outliers) / len(df) * 100, 2),
                'distribuicao_faixas_rpm': dict(df['faixa_rpm'].value_counts()),
                'padroes_identificados': len(padroes_especificos),
            }
            
            # Salvar resumo
            resumo_df = pd.DataFrame([resumo]).T
            resumo_df.columns = ['Valor']
            resumo_df.to_excel(f'{deposito}/estudo_01_resumo_executivo.xlsx')
            
            # ============= RESULTADO FINAL =============
            print(colored("="*50, 'cyan'))
            print(colored("ESTUDO ESTATÍSTICO CONCLUÍDO COM SUCESSO!", 'green'))
            print(colored("="*50, 'cyan'))
            
            print(f"📊 {colored('RESUMO DOS RESULTADOS:', 'yellow')}")
            print(f"   • Total de registros analisados: {colored(f'{len(df):,}', 'green')}")
            print(f"   • Unidades analisadas: {colored(df['unidade_id'].nunique(), 'green')}")
            print(f"   • Empresas envolvidas: {colored(df['empresa'].nunique(), 'green')}")
            print(f"   • Outliers detectados: {colored(f'{len(all_outliers):,}', 'red')} ({colored(f'{len(all_outliers)/len(df)*100:.1f}%', 'red')})")
            print(f"   • RPM médio da frota: {colored(f'{df.rpm.mean():.0f}', 'blue')} RPM")
            print(f"   • Velocidade média: {colored(f'{df.velocidade.mean():.1f}', 'blue')} km/h")
            
            print(f"\n📁 {colored('ARQUIVOS GERADOS:', 'yellow')}")
            print(f"   • estudo_01_estatisticas_descritivas.xlsx")
            print(f"   • estudo_01_outliers_detectados.xlsx")
            print(f"   • estudo_01_analise_por_unidade.xlsx")
            print(f"   • estudo_01_analise_temporal.xlsx")
            print(f"   • estudo_01_matriz_correlacao.xlsx")
            print(f"   • estudo_01_analise_clusters.xlsx")
            print(f"   • estudo_01_padroes_especificos.xlsx")
            print(f"   • estudo_01_resumo_executivo.xlsx")
            print(f"   • estudo_01_distribuicoes.png")
            print(f"   • estudo_01_analise_temporal.png")
            print(f"   • estudo_01_correlacoes.png")
            
            print(f"\n🎯 {colored('PRINCIPAIS INSIGHTS:', 'yellow')}")
            print(f"   • Faixa de RPM mais comum: {colored(df['faixa_rpm'].mode().iloc[0], 'green')}")
            print(f"   • Horário de maior atividade: {colored(f'{hourly_rpm.idxmax()}h', 'green')}")
            print(f"   • Correlação RPM-Velocidade: {colored(f'{df.rpm.corr(df.velocidade):.3f}', 'blue')}")
            
            return True
            
        except Exception as e:
            print(f"❌ {colored(f'Erro durante a análise: {str(e)}', 'red')}")
            import traceback
            traceback.print_exc()
            return False

    def ESTUDO_02(self):
        """
        Análise estatística completa dos dados de Viagem_eco
        - Detecção de outliers
        - Análise de padrões
        - Estatísticas descritivas
        - Correlações entre variáveis
        - Análise temporal
        - Análise por marca e modelo
        """
        print(colored("="*50, 'cyan'))
        print(colored("INICIANDO ESTUDO ESTATÍSTICO COMPLETO", 'yellow'))
        print(colored("="*50, 'cyan'))
        
        # Importações necessárias
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.ensemble import IsolationForest
        import warnings
        warnings.filterwarnings('ignore')
        
        # Configurar matplotlib para não mostrar gráficos
        plt.ioff()
        
        try:
            # ============= COLETA DE DADOS =============
            print(f"📊 {colored('Coletando dados do banco...', 'blue')}")
            
            # Buscar todos os dados de Viagem_eco com informações dos veículos
            viagens_eco = Viagem_eco.objects.all().select_related('unidade__empresa')
            
            if not viagens_eco.exists():
                print(f"❌ {colored('Nenhum dado encontrado na tabela Viagem_eco', 'red')}")
                return
            
            # Converter para DataFrame
            data_list = []
            for viagem in viagens_eco:
                try:
                    # Converter timestamp unix para datetime
                    timestamp_int = int(viagem.timestamp)
                    dt = datetime.fromtimestamp(timestamp_int)
                    
                    # Filtrar apenas dados com RPM válidos (acima de 300)
                    if viagem.rpm and float(viagem.rpm) >= 300:
                        data_list.append({
                            'timestamp': timestamp_int,
                            'datetime': dt,
                            'unidade_id': viagem.unidade.id,
                            'unidade_nome': viagem.unidade.nm,
                            'empresa': viagem.unidade.empresa.nome if viagem.unidade.empresa else 'N/A',
                            'marca': viagem.unidade.marca if hasattr(viagem.unidade, 'marca') and viagem.unidade.marca else 'N/I',
                            'modelo': viagem.unidade.modelo if hasattr(viagem.unidade, 'modelo') and viagem.unidade.modelo else 'N/I',
                            'cor': viagem.unidade.cor if hasattr(viagem.unidade, 'cor') and viagem.unidade.cor else 'N/I',
                            'placa': viagem.unidade.placa if hasattr(viagem.unidade, 'placa') and viagem.unidade.placa else 'N/I',
                            'rpm': float(viagem.rpm),
                            'velocidade': float(viagem.velocidade) if viagem.velocidade else 0.0,
                            'altitude': float(viagem.altitude) if viagem.altitude else 0.0,
                            'hora': dt.hour,
                            'dia_semana': dt.weekday(),
                            'mes': dt.month,
                            'ano': dt.year,
                        })
                except (ValueError, TypeError, OSError):
                    continue
            
            if not data_list:
                print(f"❌ {colored('Nenhum dado válido encontrado', 'red')}")
                return
            
            df = pd.DataFrame(data_list)
            print(f"✅ {colored(f'Dados coletados: {len(df)} registros de {df.unidade_id.nunique()} unidades', 'green')}")
            print(f"📋 {colored(f'Marcas encontradas: {df.marca.nunique()} ({list(df.marca.unique())})', 'blue')}")
            print(f"🚗 {colored(f'Modelos encontrados: {df.modelo.nunique()}', 'blue')}")
            
            # ============= ANÁLISE DESCRITIVA BÁSICA =============
            print(f"\n📈 {colored('Gerando estatísticas descritivas...', 'blue')}")
            
            stats_desc = df[['rpm', 'velocidade', 'altitude']].describe()
            
            # Função para calcular MAD (Mean Absolute Deviation) manualmente
            def calculate_mad(series):
                """Calcula o desvio absoluto mediano"""
                median = series.median()
                return (series - median).abs().median()
            
            # Adicionar estatísticas extras
            stats_extras = pd.DataFrame({
                'rpm': [
                    df['rpm'].var(),
                    df['rpm'].skew(),
                    df['rpm'].kurtosis(),
                    calculate_mad(df['rpm'])
                ],
                'velocidade': [
                    df['velocidade'].var(),
                    df['velocidade'].skew(),
                    df['velocidade'].kurtosis(),
                    calculate_mad(df['velocidade'])
                ],
                'altitude': [
                    df['altitude'].var(),
                    df['altitude'].skew(),
                    df['altitude'].kurtosis(),
                    calculate_mad(df['altitude'])
                ]
            }, index=['variancia', 'assimetria', 'curtose', 'desvio_abs_mediano'])
            
            stats_completas = pd.concat([stats_desc, stats_extras])
            
            # Salvar estatísticas descritivas
            stats_completas.to_excel(f'{deposito}/estudo_01_estatisticas_descritivas.xlsx')
            print(f"💾 Estatísticas descritivas salvas em: estudo_01_estatisticas_descritivas.xlsx")
            
            # ============= DETECÇÃO DE OUTLIERS =============
            print(f"\n🔍 {colored('Detectando outliers...', 'blue')}")
            
            # Método 1: Z-Score
            z_scores = np.abs(stats.zscore(df[['rpm', 'velocidade', 'altitude']]))
            outliers_zscore = df[(z_scores > 3).any(axis=1)].copy()
            
            # Método 2: IQR (Interquartile Range)
            outliers_iqr = pd.DataFrame()
            for coluna in ['rpm', 'velocidade', 'altitude']:
                Q1 = df[coluna].quantile(0.25)
                Q3 = df[coluna].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_col = df[(df[coluna] < lower_bound) | (df[coluna] > upper_bound)]
                outliers_iqr = pd.concat([outliers_iqr, outliers_col]).drop_duplicates()
            
            # Método 3: Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers_iso = iso_forest.fit_predict(df[['rpm', 'velocidade', 'altitude']])
            outliers_isolation = df[outliers_iso == -1].copy()
            
            # Combinar todos os outliers
            all_outliers = pd.concat([outliers_zscore, outliers_iqr, outliers_isolation]).drop_duplicates()
            all_outliers['metodo_deteccao'] = 'Múltiplos'
            
            print(f"🎯 Outliers detectados:")
            print(f"   - Z-Score (>3): {len(outliers_zscore)} registros")
            print(f"   - IQR: {len(outliers_iqr)} registros")
            print(f"   - Isolation Forest: {len(outliers_isolation)} registros")
            print(f"   - Total únicos: {len(all_outliers)} registros")
            
            # Salvar outliers
            all_outliers.to_excel(f'{deposito}/estudo_01_outliers_detectados.xlsx', index=False)
            print(f"💾 Outliers salvos em: estudo_01_outliers_detectados.xlsx")
            
            # ============= ANÁLISE POR UNIDADE =============
            print(f"\n🚛 {colored('Analisando padrões por unidade...', 'blue')}")
            
            stats_por_unidade = df.groupby(['unidade_nome', 'empresa', 'marca', 'modelo', 'placa']).agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
            }).round(2)
            
            # Achatar colunas multi-nível
            stats_por_unidade.columns = ['_'.join(col).strip() for col in stats_por_unidade.columns]
            stats_por_unidade = stats_por_unidade.reset_index()
            
            # Adicionar classificações
            stats_por_unidade['rpm_categoria'] = pd.cut(
                stats_por_unidade['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Baixo', 'Econômico', 'Normal', 'Alto']
            )
            
            stats_por_unidade['velocidade_categoria'] = pd.cut(
                stats_por_unidade['velocidade_mean'], 
                bins=[0, 40, 60, 80, float('inf')], 
                labels=['Baixa', 'Moderada', 'Alta', 'Muito Alta']
            )
            
            # Salvar análise por unidade
            stats_por_unidade.to_excel(f'{deposito}/estudo_01_analise_por_unidade.xlsx', index=False)
            print(f"💾 Análise por unidade salva em: estudo_01_analise_por_unidade.xlsx")
            
            # ============= ANÁLISE POR MARCA =============
            print(f"\n🏭 {colored('Analisando padrões por marca...', 'blue')}")
            
            stats_por_marca = df.groupby('marca').agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            stats_por_marca.columns = ['_'.join(col).strip() for col in stats_por_marca.columns]
            stats_por_marca = stats_por_marca.reset_index()
            
            # Adicionar classificação de eficiência por marca
            stats_por_marca['eficiencia_rpm'] = pd.cut(
                stats_por_marca['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Muito Eficiente', 'Eficiente', 'Normal', 'Ineficiente']
            )
            
            # Calcular ranking de eficiência
            stats_por_marca['ranking_eficiencia'] = stats_por_marca['rpm_mean'].rank(ascending=True)
            
            # Salvar análise por marca
            stats_por_marca.to_excel(f'{deposito}/estudo_01_analise_por_marca.xlsx', index=False)
            print(f"💾 Análise por marca salva em: estudo_01_analise_por_marca.xlsx")
            
            # ============= ANÁLISE POR MODELO =============
            print(f"\n🚗 {colored('Analisando padrões por modelo...', 'blue')}")
            
            stats_por_modelo = df.groupby(['marca', 'modelo']).agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            stats_por_modelo.columns = ['_'.join(col).strip() for col in stats_por_modelo.columns]
            stats_por_modelo = stats_por_modelo.reset_index()
            
            # Adicionar classificação de performance
            stats_por_modelo['performance_rpm'] = pd.cut(
                stats_por_modelo['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Excelente', 'Boa', 'Regular', 'Ruim']
            )
            
            stats_por_modelo['performance_velocidade'] = pd.cut(
                stats_por_modelo['velocidade_mean'], 
                bins=[0, 40, 60, 80, float('inf')], 
                labels=['Urbano', 'Misto', 'Rodoviário', 'Alto']
            )
            
            # Salvar análise por modelo
            stats_por_modelo.to_excel(f'{deposito}/estudo_01_analise_por_modelo.xlsx', index=False)
            print(f"💾 Análise por modelo salva em: estudo_01_analise_por_modelo.xlsx")
            
            # ============= COMPARATIVO ENTRE MARCAS =============
            print(f"\n⚖️ {colored('Gerando comparativo entre marcas...', 'blue')}")
            
            comparativo_marcas = {}
            
            for marca in df['marca'].unique():
                if marca != 'N/I':  # Ignora registros sem marca
                    dados_marca = df[df['marca'] == marca]
                    
                    comparativo_marcas[marca] = {
                        'total_registros': len(dados_marca),
                        'total_unidades': dados_marca['unidade_id'].nunique(),
                        'rpm_medio': dados_marca['rpm'].mean(),
                        'rpm_desvio': dados_marca['rpm'].std(),
                        'velocidade_media': dados_marca['velocidade'].mean(),
                        'altitude_media': dados_marca['altitude'].mean(),
                        'percentual_zona_verde': len(dados_marca[(dados_marca['rpm'] >= 800) & (dados_marca['rpm'] <= 1300)]) / len(dados_marca) * 100,
                        'percentual_zona_vermelha': len(dados_marca[dados_marca['rpm'] > 2300]) / len(dados_marca) * 100,
                        'empresas': list(dados_marca['empresa'].unique())
                    }
            
            # Converter para DataFrame
            comparativo_df = pd.DataFrame(comparativo_marcas).T
            comparativo_df = comparativo_df.round(2)
            comparativo_df = comparativo_df.sort_values('rpm_medio')  # Ordenar por eficiência
            
            # Salvar comparativo
            comparativo_df.to_excel(f'{deposito}/estudo_01_comparativo_marcas.xlsx')
            print(f"💾 Comparativo entre marcas salvo em: estudo_01_comparativo_marcas.xlsx")
            
            # ============= ANÁLISE TEMPORAL =============
            print(f"\n⏰ {colored('Analisando padrões temporais...', 'blue')}")
            
            # Por hora do dia
            analise_hora = df.groupby('hora').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_hora.columns = ['_'.join(col).strip() for col in analise_hora.columns]
            analise_hora = analise_hora.reset_index()
            
            # Por dia da semana
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            analise_dia_semana = df.groupby('dia_semana').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_dia_semana.columns = ['_'.join(col).strip() for col in analise_dia_semana.columns]
            analise_dia_semana = analise_dia_semana.reset_index()
            analise_dia_semana['dia_nome'] = analise_dia_semana['dia_semana'].map(lambda x: dias_semana[x])
            
            # Por mês
            analise_mes = df.groupby('mes').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_mes.columns = ['_'.join(col).strip() for col in analise_mes.columns]
            analise_mes = analise_mes.reset_index()
            
            # Análise temporal por marca
            analise_temporal_marca = df.groupby(['marca', 'hora']).agg({
                'rpm': 'mean',
                'velocidade': 'mean'
            }).round(2).reset_index()
            
            # Salvar análises temporais
            with pd.ExcelWriter(f'{deposito}/estudo_01_analise_temporal.xlsx') as writer:
                analise_hora.to_excel(writer, sheet_name='Por_Hora', index=False)
                analise_dia_semana.to_excel(writer, sheet_name='Por_Dia_Semana', index=False)
                analise_mes.to_excel(writer, sheet_name='Por_Mes', index=False)
                analise_temporal_marca.to_excel(writer, sheet_name='Marca_por_Hora', index=False)
            
            print(f"💾 Análise temporal salva em: estudo_01_analise_temporal.xlsx")
            
            # ============= ANÁLISE DE CORRELAÇÕES =============
            print(f"\n🔗 {colored('Analisando correlações...', 'blue')}")
            
            # Matriz de correlação geral
            correlation_matrix = df[['rpm', 'velocidade', 'altitude', 'hora', 'dia_semana']].corr()
            
            # Correlações por marca (se houver dados suficientes)
            correlacoes_por_marca = {}
            for marca in df['marca'].unique():
                if marca != 'N/I':
                    dados_marca = df[df['marca'] == marca]
                    if len(dados_marca) > 50:  # Só calcula se houver dados suficientes
                        correlacoes_por_marca[marca] = dados_marca[['rpm', 'velocidade', 'altitude']].corr()
            
            # Salvar correlações
            with pd.ExcelWriter(f'{deposito}/estudo_01_matriz_correlacao.xlsx') as writer:
                correlation_matrix.to_excel(writer, sheet_name='Geral')
                for marca, corr_matrix in correlacoes_por_marca.items():
                    corr_matrix.to_excel(writer, sheet_name=f'Marca_{marca}')
            
            print(f"💾 Matriz de correlação salva em: estudo_01_matriz_correlacao.xlsx")
            
            # ============= CLUSTERING ANÁLISE =============
            print(f"\n🎯 {colored('Realizando análise de clusters...', 'blue')}")
            
            # Preparar dados para clustering
            features_clustering = df[['rpm', 'velocidade', 'altitude']].copy()
            
            # Normalizar dados
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features_clustering)
            
            # K-Means com k=5
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_normalized)
            
            # Adicionar clusters ao DataFrame
            df_clusters = df.copy()
            df_clusters['cluster'] = clusters
            
            # Analisar características de cada cluster
            cluster_analysis = df_clusters.groupby('cluster').agg({
                'rpm': ['mean', 'std', 'min', 'max', 'count'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            cluster_analysis.columns = ['_'.join(col).strip() for col in cluster_analysis.columns]
            cluster_analysis = cluster_analysis.reset_index()
            
            # Análise de clusters por marca
            cluster_por_marca = df_clusters.groupby(['marca', 'cluster']).size().reset_index(name='count')
            cluster_por_marca_pivot = cluster_por_marca.pivot(index='marca', columns='cluster', values='count').fillna(0)
            
            # Adicionar interpretação dos clusters
            def interpretar_cluster(row):
                rpm_mean = row['rpm_mean']
                vel_mean = row['velocidade_mean']
                
                if rpm_mean < 800:
                    rpm_cat = "Marcha Lenta"
                elif rpm_mean < 1300:
                    rpm_cat = "Econômico"
                elif rpm_mean < 2000:
                    rpm_cat = "Normal"
                else:
                    rpm_cat = "Alto"
                
                if vel_mean < 20:
                    vel_cat = "Parado/Lento"
                elif vel_mean < 50:
                    vel_cat = "Urbano"
                elif vel_mean < 80:
                    vel_cat = "Rodoviário"
                else:
                    vel_cat = "Alto"
                
                return f"{rpm_cat} + {vel_cat}"
            
            cluster_analysis['interpretacao'] = cluster_analysis.apply(interpretar_cluster, axis=1)
            
            # Salvar análise de clusters
            with pd.ExcelWriter(f'{deposito}/estudo_01_analise_clusters.xlsx') as writer:
                cluster_analysis.to_excel(writer, sheet_name='Clusters_Geral', index=False)
                cluster_por_marca_pivot.to_excel(writer, sheet_name='Clusters_por_Marca')
            
            print(f"💾 Análise de clusters salva em: estudo_01_analise_clusters.xlsx")
            
            # ============= DETECÇÃO DE PADRÕES ESPECÍFICOS =============
            print(f"\n🔍 {colored('Detectando padrões específicos...', 'blue')}")
            
            padroes_especificos = {}
            
            # 1. Padrão de marcha lenta excessiva
            marcha_lenta = df[df['rpm'] < 500]
            padroes_especificos['marcha_lenta_excessiva'] = {
                'total_registros': len(marcha_lenta),
                'unidades_afetadas': marcha_lenta['unidade_nome'].nunique(),
                'percentual_total': round(len(marcha_lenta) / len(df) * 100, 2),
                'por_marca': dict(marcha_lenta['marca'].value_counts())
            }
            
            # 2. Padrão de RPM muito alto (zona vermelha)
            rpm_alto = df[df['rpm'] > 2300]
            padroes_especificos['rpm_zona_vermelha'] = {
                'total_registros': len(rpm_alto),
                'unidades_afetadas': rpm_alto['unidade_nome'].nunique(),
                'percentual_total': round(len(rpm_alto) / len(df) * 100, 2),
                'por_marca': dict(rpm_alto['marca'].value_counts())
            }
            
            # 3. Padrão de velocidade alta com RPM baixo
            vel_alta_rpm_baixo = df[(df['velocidade'] > 60) & (df['rpm'] < 1000)]
            padroes_especificos['velocidade_alta_rpm_baixo'] = {
                'total_registros': len(vel_alta_rpm_baixo),
                'unidades_afetadas': vel_alta_rpm_baixo['unidade_nome'].nunique(),
                'percentual_total': round(len(vel_alta_rpm_baixo) / len(df) * 100, 2),
                'por_marca': dict(vel_alta_rpm_baixo['marca'].value_counts())
            }
            
            # 4. Padrão noturno (22h às 6h)
            periodo_noturno = df[(df['hora'] >= 22) | (df['hora'] <= 6)]
            padroes_especificos['atividade_noturna'] = {
                'total_registros': len(periodo_noturno),
                'unidades_afetadas': periodo_noturno['unidade_nome'].nunique(),
                'percentual_total': round(len(periodo_noturno) / len(df) * 100, 2),
                'por_marca': dict(periodo_noturno['marca'].value_counts())
            }
            
            # 5. Eficiência por faixa de RPM
            df['faixa_rpm'] = pd.cut(
                df['rpm'], 
                bins=[0, 799, 1300, 2300, float('inf')], 
                labels=['Azul (350-799)', 'Verde (800-1300)', 'Amarela (1301-2300)', 'Vermelha (2301+)']
            )
            
            distribuicao_rpm = df['faixa_rpm'].value_counts().to_dict()
            distribuicao_rpm_por_marca = df.groupby(['marca', 'faixa_rpm']).size().unstack(fill_value=0)
            
            padroes_especificos['distribuicao_faixas_rpm'] = distribuicao_rpm
            
            # Salvar padrões específicos
            with pd.ExcelWriter(f'{deposito}/estudo_01_padroes_especificos.xlsx') as writer:
                # Sheet com resumo dos padrões
                padroes_resumo = pd.DataFrame([padroes_especificos]).T
                padroes_resumo.to_excel(writer, sheet_name='Resumo_Padroes')
                
                # Sheet com distribuição RPM por marca
                distribuicao_rpm_por_marca.to_excel(writer, sheet_name='RPM_por_Marca')
            
            print(f"💾 Padrões específicos salvos em: estudo_01_padroes_especificos.xlsx")
            
            # ============= GERAR GRÁFICOS =============
            print(f"\n📊 {colored('Gerando gráficos de análise...', 'blue')}")
            
            # Configurar estilo dos gráficos
            plt.style.use('default')
            sns.set_palette("husl")
            
            # 1. Distribuições das variáveis principais
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Distribuições das Variáveis Principais', fontsize=16, fontweight='bold')
            
            # RPM
            axes[0, 0].hist(df['rpm'], bins=50, alpha=0.7, color='blue')
            axes[0, 0].set_title('Distribuição RPM')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Frequência')
            axes[0, 0].axvline(df['rpm'].mean(), color='red', linestyle='--', label=f'Média: {df["rpm"].mean():.0f}')
            axes[0, 0].legend()
            
            # Velocidade
            axes[0, 1].hist(df['velocidade'], bins=50, alpha=0.7, color='green')
            axes[0, 1].set_title('Distribuição Velocidade')
            axes[0, 1].set_xlabel('Velocidade (km/h)')
            axes[0, 1].set_ylabel('Frequência')
            axes[0, 1].axvline(df['velocidade'].mean(), color='red', linestyle='--', label=f'Média: {df["velocidade"].mean():.1f}')
            axes[0, 1].legend()
            
            # Altitude
            axes[1, 0].hist(df['altitude'], bins=50, alpha=0.7, color='orange')
            axes[1, 0].set_title('Distribuição Altitude')
            axes[1, 0].set_xlabel('Altitude (m)')
            axes[1, 0].set_ylabel('Frequência')
            axes[1, 0].axvline(df['altitude'].mean(), color='red', linestyle='--', label=f'Média: {df["altitude"].mean():.1f}')
            axes[1, 0].legend()
            
            # Distribuição por faixa de RPM
            faixa_counts = df['faixa_rpm'].value_counts()
            axes[1, 1].pie(faixa_counts.values, labels=faixa_counts.index, autopct='%1.1f%%')
            axes[1, 1].set_title('Distribuição por Faixa de RPM')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_distribuicoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Análise por marca
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise por Marca', fontsize=16, fontweight='bold')
            
            # RPM médio por marca
            marca_rpm = df.groupby('marca')['rpm'].mean().sort_values()
            axes[0, 0].bar(range(len(marca_rpm)), marca_rpm.values, color='skyblue')
            axes[0, 0].set_title('RPM Médio por Marca')
            axes[0, 0].set_xlabel('Marca')
            axes[0, 0].set_ylabel('RPM Médio')
            axes[0, 0].set_xticks(range(len(marca_rpm)))
            axes[0, 0].set_xticklabels(marca_rpm.index, rotation=45)
            
            # Velocidade média por marca
            marca_vel = df.groupby('marca')['velocidade'].mean().sort_values()
            axes[0, 1].bar(range(len(marca_vel)), marca_vel.values, color='lightgreen')
            axes[0, 1].set_title('Velocidade Média por Marca')
            axes[0, 1].set_xlabel('Marca')
            axes[0, 1].set_ylabel('Velocidade Média (km/h)')
            axes[0, 1].set_xticks(range(len(marca_vel)))
            axes[0, 1].set_xticklabels(marca_vel.index, rotation=45)
            
            # Distribuição de registros por marca
            marca_count = df['marca'].value_counts()
            axes[1, 0].pie(marca_count.values, labels=marca_count.index, autopct='%1.1f%%')
            axes[1, 0].set_title('Distribuição de Registros por Marca')
            
            # Boxplot RPM por marca
            marcas_com_dados = [marca for marca in df['marca'].unique() if len(df[df['marca'] == marca]) > 100]
            if len(marcas_com_dados) > 1:
                dados_boxplot = [df[df['marca'] == marca]['rpm'] for marca in marcas_com_dados]
                axes[1, 1].boxplot(dados_boxplot, labels=marcas_com_dados)
                axes[1, 1].set_title('Distribuição RPM por Marca')
                axes[1, 1].set_xlabel('Marca')
                axes[1, 1].set_ylabel('RPM')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_analise_marcas.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. Análise temporal
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise Temporal dos Dados', fontsize=16, fontweight='bold')
            
            # RPM por hora
            hourly_rpm = df.groupby('hora')['rpm'].mean()
            axes[0, 0].plot(hourly_rpm.index, hourly_rpm.values, marker='o', linewidth=2)
            axes[0, 0].set_title('RPM Médio por Hora do Dia')
            axes[0, 0].set_xlabel('Hora')
            axes[0, 0].set_ylabel('RPM Médio')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Velocidade por hora
            hourly_vel = df.groupby('hora')['velocidade'].mean()
            axes[0, 1].plot(hourly_vel.index, hourly_vel.values, marker='s', color='green', linewidth=2)
            axes[0, 1].set_title('Velocidade Média por Hora do Dia')
            axes[0, 1].set_xlabel('Hora')
            axes[0, 1].set_ylabel('Velocidade Média (km/h)')
            axes[0, 1].grid(True, alpha=0.3)
            
            # RPM por dia da semana
            daily_rpm = df.groupby('dia_semana')['rpm'].mean()
            dias_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            axes[1, 0].bar(range(7), daily_rpm.values, color='purple', alpha=0.7)
            axes[1, 0].set_title('RPM Médio por Dia da Semana')
            axes[1, 0].set_xlabel('Dia da Semana')
            axes[1, 0].set_ylabel('RPM Médio')
            axes[1, 0].set_xticks(range(7))
            axes[1, 0].set_xticklabels(dias_nome)
            
            # Atividade por mês
            monthly_count = df.groupby('mes').size()
            axes[1, 1].bar(monthly_count.index, monthly_count.values, color='red', alpha=0.7)
            axes[1, 1].set_title('Atividade por Mês')
            axes[1, 1].set_xlabel('Mês')
            axes[1, 1].set_ylabel('Número de Registros')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_analise_temporal.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 4. Scatter plots e correlações
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise de Correlações', fontsize=16, fontweight='bold')
            
            # RPM vs Velocidade
            axes[0, 0].scatter(df['rpm'], df['velocidade'], alpha=0.1, s=1)
            axes[0, 0].set_title('RPM vs Velocidade')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Velocidade (km/h)')
            
            # RPM vs Altitude
            axes[0, 1].scatter(df['rpm'], df['altitude'], alpha=0.1, s=1, color='green')
            axes[0, 1].set_title('RPM vs Altitude')
            axes[0, 1].set_xlabel('RPM')
            axes[0, 1].set_ylabel('Altitude (m)')
            
            # Velocidade vs Altitude
            axes[1, 0].scatter(df['velocidade'], df['altitude'], alpha=0.1, s=1, color='red')
            axes[1, 0].set_title('Velocidade vs Altitude')
            axes[1, 0].set_xlabel('Velocidade (km/h)')
            axes[1, 0].set_ylabel('Altitude (m)')
            
            # Heatmap de correlação
            corr_data = df[['rpm', 'velocidade', 'altitude', 'hora']].corr()
            im = axes[1, 1].imshow(corr_data, cmap='coolwarm', aspect='auto')
            axes[1, 1].set_title('Matriz de Correlação')
            axes[1, 1].set_xticks(range(len(corr_data.columns)))
            axes[1, 1].set_yticks(range(len(corr_data.columns)))
            axes[1, 1].set_xticklabels(corr_data.columns)
            axes[1, 1].set_yticklabels(corr_data.columns)
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_01_correlacoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 Gráficos salvos em:")
            print(f"   - estudo_01_distribuicoes.png")
            print(f"   - estudo_01_analise_marcas.png")
            print(f"   - estudo_01_analise_temporal.png")
            print(f"   - estudo_01_correlacoes.png")
            
            # ============= RELATÓRIO RESUMO =============
            print(f"\n📋 {colored('Gerando relatório resumo...', 'blue')}")
            
            resumo = {
                'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_registros': len(df),
                'total_unidades': df['unidade_id'].nunique(),
                'total_empresas': df['empresa'].nunique(),
                'total_marcas': df['marca'].nunique(),
                'total_modelos': df['modelo'].nunique(),
                'periodo_dados': f"{df['datetime'].min()} até {df['datetime'].max()}",
                'rpm_medio_geral': round(df['rpm'].mean(), 2),
                'rpm_desvio_padrao': round(df['rpm'].std(), 2),
                'velocidade_media_geral': round(df['velocidade'].mean(), 2),
                'altitude_media_geral': round(df['altitude'].mean(), 2),
                'outliers_detectados': len(all_outliers),
                'percentual_outliers': round(len(all_outliers) / len(df) * 100, 2),
                'distribuicao_faixas_rpm': dict(df['faixa_rpm'].value_counts()),
                'marca_mais_eficiente': marca_rpm.index[0] if len(marca_rpm) > 0 else 'N/A',
                'marca_menos_eficiente': marca_rpm.index[-1] if len(marca_rpm) > 0 else 'N/A',
                'padroes_identificados': len(padroes_especificos),
            }
            
            # Salvar resumo
            resumo_df = pd.DataFrame([resumo]).T
            resumo_df.columns = ['Valor']
            resumo_df.to_excel(f'{deposito}/estudo_01_resumo_executivo.xlsx')
            
            # ============= RESULTADO FINAL =============
            print(colored("="*50, 'cyan'))
            print(colored("ESTUDO ESTATÍSTICO CONCLUÍDO COM SUCESSO!", 'green'))
            print(colored("="*50, 'cyan'))
            
            print(f"📊 {colored('RESUMO DOS RESULTADOS:', 'yellow')}")
            print(f"   • Total de registros analisados: {colored(f'{len(df):,}', 'green')}")
            print(f"   • Unidades analisadas: {colored(df['unidade_id'].nunique(), 'green')}")
            print(f"   • Empresas envolvidas: {colored(df['empresa'].nunique(), 'green')}")
            print(f"   • Marcas analisadas: {colored(df['marca'].nunique(), 'blue')}")
            print(f"   • Modelos analisados: {colored(df['modelo'].nunique(), 'blue')}")
            print(f"   • Outliers detectados: {colored(f'{len(all_outliers):,}', 'red')} ({colored(f'{len(all_outliers)/len(df)*100:.1f}%', 'red')})")
            print(f"   • RPM médio da frota: {colored(f'{df.rpm.mean():.0f}', 'blue')} RPM")
            print(f"   • Velocidade média: {colored(f'{df.velocidade.mean():.1f}', 'blue')} km/h")
            
            print(f"\n🏭 {colored('ANÁLISE POR MARCA:', 'yellow')}")
            if len(marca_rpm) > 0:
                print(f"   • Marca mais eficiente: {colored(marca_rpm.index[0], 'green')} ({colored(f'{marca_rpm.iloc[0]:.0f}', 'green')} RPM)")
                print(f"   • Marca menos eficiente: {colored(marca_rpm.index[-1], 'red')} ({colored(f'{marca_rpm.iloc[-1]:.0f}', 'red')} RPM)")
            
            print(f"\n📁 {colored('ARQUIVOS GERADOS:', 'yellow')}")
            print(f"   • estudo_01_estatisticas_descritivas.xlsx")
            print(f"   • estudo_01_outliers_detectados.xlsx") 
            print(f"   • estudo_01_analise_por_unidade.xlsx")
            print(f"   • estudo_01_analise_por_marca.xlsx")
            print(f"   • estudo_01_analise_por_modelo.xlsx")
            print(f"   • estudo_01_comparativo_marcas.xlsx")
            print(f"   • estudo_01_analise_temporal.xlsx")
            print(f"   • estudo_01_matriz_correlacao.xlsx")
            print(f"   • estudo_01_analise_clusters.xlsx")
            print(f"   • estudo_01_padroes_especificos.xlsx")
            print(f"   • estudo_01_resumo_executivo.xlsx")
            print(f"   • estudo_01_distribuicoes.png")
            print(f"   • estudo_01_analise_marcas.png")
            print(f"   • estudo_01_analise_temporal.png")
            print(f"   • estudo_01_correlacoes.png")
            
            print(f"\n🎯 {colored('PRINCIPAIS INSIGHTS:', 'yellow')}")
            print(f"   • Faixa de RPM mais comum: {colored(df['faixa_rpm'].mode().iloc[0], 'green')}")
            print(f"   • Horário de maior atividade: {colored(f'{hourly_rpm.idxmax()}h', 'green')}")
            print(f"   • Correlação RPM-Velocidade: {colored(f'{df.rpm.corr(df.velocidade):.3f}', 'blue')}")
            if len(marca_rpm) > 1:
                print(f"   • Diferença de eficiência entre marcas: {colored(f'{marca_rpm.iloc[-1] - marca_rpm.iloc[0]:.0f}', 'yellow')} RPM")
            
            return True
            
        except Exception as e:
            print(f"❌ {colored(f'Erro durante a análise: {str(e)}', 'red')}")
            import traceback
            traceback.print_exc()
            return False


    def ESTUDO_03(self):
        """
        Análise estatística completa dos dados de Viagem_eco
        - Detecção de outliers
        - Análise de padrões
        - Estatísticas descritivas
        - Correlações entre variáveis
        - Análise temporal
        - Análise por marca e modelo
        - NOVO: Análises de dispersão RPM detalhadas
        """
        print(colored("="*50, 'cyan'))
        print(colored("INICIANDO ESTUDO ESTATÍSTICO COMPLETO V2", 'yellow'))
        print(colored("="*50, 'cyan'))
        
        # Importações necessárias
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.ensemble import IsolationForest
        import warnings
        warnings.filterwarnings('ignore')
        
        # Configurar matplotlib para não mostrar gráficos
        plt.ioff()
        
        try:
            # ============= COLETA DE DADOS =============
            print(f"📊 {colored('Coletando dados do banco...', 'blue')}")
            
            # Buscar todos os dados de Viagem_eco com informações dos veículos
            viagens_eco = Viagem_eco.objects.all().select_related('unidade__empresa')
            
            if not viagens_eco.exists():
                print(f"❌ {colored('Nenhum dado encontrado na tabela Viagem_eco', 'red')}")
                return
            
            # Converter para DataFrame
            data_list = []
            for viagem in viagens_eco:
                try:
                    # Converter timestamp unix para datetime
                    timestamp_int = int(viagem.timestamp)
                    dt = datetime.fromtimestamp(timestamp_int)
                    
                    # Filtrar apenas dados com RPM válidos (acima de 300)
                    if viagem.rpm and float(viagem.rpm) >= 300:
                        data_list.append({
                            'timestamp': timestamp_int,
                            'datetime': dt,
                            'unidade_id': viagem.unidade.id,
                            'unidade_nome': viagem.unidade.nm,
                            'empresa': viagem.unidade.empresa.nome if viagem.unidade.empresa else 'N/A',
                            'marca': viagem.unidade.marca if hasattr(viagem.unidade, 'marca') and viagem.unidade.marca else 'N/I',
                            'modelo': viagem.unidade.modelo if hasattr(viagem.unidade, 'modelo') and viagem.unidade.modelo else 'N/I',
                            'cor': viagem.unidade.cor if hasattr(viagem.unidade, 'cor') and viagem.unidade.cor else 'N/I',
                            'placa': viagem.unidade.placa if hasattr(viagem.unidade, 'placa') and viagem.unidade.placa else 'N/I',
                            'rpm': float(viagem.rpm),
                            'velocidade': float(viagem.velocidade) if viagem.velocidade else 0.0,
                            'altitude': float(viagem.altitude) if viagem.altitude else 0.0,
                            'hora': dt.hour,
                            'dia_semana': dt.weekday(),
                            'mes': dt.month,
                            'ano': dt.year,
                        })
                except (ValueError, TypeError, OSError):
                    continue
            
            if not data_list:
                print(f"❌ {colored('Nenhum dado válido encontrado', 'red')}")
                return
            
            df = pd.DataFrame(data_list)
            print(f"✅ {colored(f'Dados coletados: {len(df)} registros de {df.unidade_id.nunique()} unidades', 'green')}")
            print(f"📋 {colored(f'Marcas encontradas: {df.marca.nunique()} ({list(df.marca.unique())})', 'blue')}")
            print(f"🚗 {colored(f'Modelos encontrados: {df.modelo.nunique()}', 'blue')}")
            
            # ============= ANÁLISE DESCRITIVA BÁSICA =============
            print(f"\n📈 {colored('Gerando estatísticas descritivas...', 'blue')}")
            
            stats_desc = df[['rpm', 'velocidade', 'altitude']].describe()
            
            # Função para calcular MAD (Mean Absolute Deviation) manualmente
            def calculate_mad(series):
                """Calcula o desvio absoluto mediano"""
                median = series.median()
                return (series - median).abs().median()
            
            # Adicionar estatísticas extras
            stats_extras = pd.DataFrame({
                'rpm': [
                    df['rpm'].var(),
                    df['rpm'].skew(),
                    df['rpm'].kurtosis(),
                    calculate_mad(df['rpm'])
                ],
                'velocidade': [
                    df['velocidade'].var(),
                    df['velocidade'].skew(),
                    df['velocidade'].kurtosis(),
                    calculate_mad(df['velocidade'])
                ],
                'altitude': [
                    df['altitude'].var(),
                    df['altitude'].skew(),
                    df['altitude'].kurtosis(),
                    calculate_mad(df['altitude'])
                ]
            }, index=['variancia', 'assimetria', 'curtose', 'desvio_abs_mediano'])
            
            stats_completas = pd.concat([stats_desc, stats_extras])
            
            # Salvar estatísticas descritivas
            stats_completas.to_excel(f'{deposito}/estudo_02_estatisticas_descritivas.xlsx')
            print(f"💾 Estatísticas descritivas salvas em: estudo_02_estatisticas_descritivas.xlsx")
            
            # ============= DETECÇÃO DE OUTLIERS =============
            print(f"\n🔍 {colored('Detectando outliers...', 'blue')}")
            
            # Método 1: Z-Score
            z_scores = np.abs(stats.zscore(df[['rpm', 'velocidade', 'altitude']]))
            outliers_zscore = df[(z_scores > 3).any(axis=1)].copy()
            
            # Método 2: IQR (Interquartile Range)
            outliers_iqr = pd.DataFrame()
            for coluna in ['rpm', 'velocidade', 'altitude']:
                Q1 = df[coluna].quantile(0.25)
                Q3 = df[coluna].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_col = df[(df[coluna] < lower_bound) | (df[coluna] > upper_bound)]
                outliers_iqr = pd.concat([outliers_iqr, outliers_col]).drop_duplicates()
            
            # Método 3: Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers_iso = iso_forest.fit_predict(df[['rpm', 'velocidade', 'altitude']])
            outliers_isolation = df[outliers_iso == -1].copy()
            
            # Combinar todos os outliers
            all_outliers = pd.concat([outliers_zscore, outliers_iqr, outliers_isolation]).drop_duplicates()
            all_outliers['metodo_deteccao'] = 'Múltiplos'
            
            print(f"🎯 Outliers detectados:")
            print(f"   - Z-Score (>3): {len(outliers_zscore)} registros")
            print(f"   - IQR: {len(outliers_iqr)} registros")
            print(f"   - Isolation Forest: {len(outliers_isolation)} registros")
            print(f"   - Total únicos: {len(all_outliers)} registros")
            
            # Salvar outliers
            all_outliers.to_excel(f'{deposito}/estudo_02_outliers_detectados.xlsx', index=False)
            print(f"💾 Outliers salvos em: estudo_02_outliers_detectados.xlsx")
            
            # ============= ANÁLISE POR UNIDADE =============
            print(f"\n🚛 {colored('Analisando padrões por unidade...', 'blue')}")
            
            stats_por_unidade = df.groupby(['unidade_nome', 'empresa', 'marca', 'modelo', 'placa']).agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
            }).round(2)
            
            # Achatar colunas multi-nível
            stats_por_unidade.columns = ['_'.join(col).strip() for col in stats_por_unidade.columns]
            stats_por_unidade = stats_por_unidade.reset_index()
            
            # Adicionar classificações
            stats_por_unidade['rpm_categoria'] = pd.cut(
                stats_por_unidade['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Baixo', 'Econômico', 'Normal', 'Alto']
            )
            
            stats_por_unidade['velocidade_categoria'] = pd.cut(
                stats_por_unidade['velocidade_mean'], 
                bins=[0, 40, 60, 80, float('inf')], 
                labels=['Baixa', 'Moderada', 'Alta', 'Muito Alta']
            )
            
            # Salvar análise por unidade
            stats_por_unidade.to_excel(f'{deposito}/estudo_02_analise_por_unidade.xlsx', index=False)
            print(f"💾 Análise por unidade salva em: estudo_02_analise_por_unidade.xlsx")
            
            # ============= ANÁLISE POR MARCA =============
            print(f"\n🏭 {colored('Analisando padrões por marca...', 'blue')}")
            
            stats_por_marca = df.groupby('marca').agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            stats_por_marca.columns = ['_'.join(col).strip() for col in stats_por_marca.columns]
            stats_por_marca = stats_por_marca.reset_index()
            
            # Adicionar classificação de eficiência por marca
            stats_por_marca['eficiencia_rpm'] = pd.cut(
                stats_por_marca['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Muito Eficiente', 'Eficiente', 'Normal', 'Ineficiente']
            )
            
            # Calcular ranking de eficiência
            stats_por_marca['ranking_eficiencia'] = stats_por_marca['rpm_mean'].rank(ascending=True)
            
            # Salvar análise por marca
            stats_por_marca.to_excel(f'{deposito}/estudo_02_analise_por_marca.xlsx', index=False)
            print(f"💾 Análise por marca salva em: estudo_02_analise_por_marca.xlsx")
            
            # ============= ANÁLISE POR MODELO =============
            print(f"\n🚗 {colored('Analisando padrões por modelo...', 'blue')}")
            
            stats_por_modelo = df.groupby(['marca', 'modelo']).agg({
                'rpm': ['count', 'mean', 'std', 'min', 'max'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            stats_por_modelo.columns = ['_'.join(col).strip() for col in stats_por_modelo.columns]
            stats_por_modelo = stats_por_modelo.reset_index()
            
            # Adicionar classificação de performance
            stats_por_modelo['performance_rpm'] = pd.cut(
                stats_por_modelo['rpm_mean'], 
                bins=[0, 800, 1300, 2000, float('inf')], 
                labels=['Excelente', 'Boa', 'Regular', 'Ruim']
            )
            
            stats_por_modelo['performance_velocidade'] = pd.cut(
                stats_por_modelo['velocidade_mean'], 
                bins=[0, 40, 60, 80, float('inf')], 
                labels=['Urbano', 'Misto', 'Rodoviário', 'Alto']
            )
            
            # Salvar análise por modelo
            stats_por_modelo.to_excel(f'{deposito}/estudo_02_analise_por_modelo.xlsx', index=False)
            print(f"💾 Análise por modelo salva em: estudo_02_analise_por_modelo.xlsx")
            
            # ============= ANÁLISE DE DISPERSÃO RPM AVANÇADA =============
            print(f"\n📊 {colored('Analisando dispersão RPM por marca e modelo...', 'blue')}")
            
            # Análise de desvio por marca
            desvios_por_marca = {}
            
            for marca in df['marca'].unique():
                if marca != 'N/I':
                    dados_marca = df[df['marca'] == marca]
                    
                    if len(dados_marca) > 50:  # Só analisa marcas com dados suficientes
                        rpm_mean = dados_marca['rpm'].mean()
                        rpm_std = dados_marca['rpm'].std()
                        
                        # Identificar unidades fora do padrão da marca (> 2 desvios padrão)
                        unidades_fora_padrao = []
                        
                        for unidade in dados_marca['unidade_nome'].unique():
                            dados_unidade = dados_marca[dados_marca['unidade_nome'] == unidade]
                            rpm_unidade = dados_unidade['rpm'].mean()
                            
                            # Calcular z-score em relação à marca
                            z_score = abs(rpm_unidade - rpm_mean) / rpm_std if rpm_std > 0 else 0
                            
                            if z_score > 2:  # Fora do padrão
                                unidades_fora_padrao.append({
                                    'unidade': unidade,
                                    'rpm_unidade': rpm_unidade,
                                    'z_score': z_score,
                                    'desvio_absoluto': rpm_unidade - rpm_mean,
                                    'status': 'Acima' if rpm_unidade > rpm_mean else 'Abaixo'
                                })
                        
                        desvios_por_marca[marca] = {
                            'rpm_medio_marca': rpm_mean,
                            'rpm_desvio_marca': rpm_std,
                            'total_unidades': dados_marca['unidade_nome'].nunique(),
                            'unidades_fora_padrao': len(unidades_fora_padrao),
                            'percentual_fora_padrao': (len(unidades_fora_padrao) / dados_marca['unidade_nome'].nunique()) * 100,
                            'detalhes_unidades': unidades_fora_padrao
                        }
            
            # Salvar análise de desvios
            desvios_detalhados = []
            for marca, dados in desvios_por_marca.items():
                for unidade in dados['detalhes_unidades']:
                    desvios_detalhados.append({
                        'marca': marca,
                        'unidade': unidade['unidade'],
                        'rpm_unidade': unidade['rpm_unidade'],
                        'rpm_medio_marca': dados['rpm_medio_marca'],
                        'desvio_absoluto': unidade['desvio_absoluto'],
                        'z_score': unidade['z_score'],
                        'status': unidade['status']
                    })
            
            df_desvios = pd.DataFrame(desvios_detalhados)
            df_desvios.to_excel(f'{deposito}/estudo_02_unidades_fora_padrao.xlsx', index=False)
            print(f"💾 Análise de unidades fora do padrão salva em: estudo_02_unidades_fora_padrao.xlsx")
            
            # Análise de dispersão por modelo dentro da marca
            dispersao_modelo = []
            
            for marca in df['marca'].unique():
                if marca != 'N/I':
                    dados_marca = df[df['marca'] == marca]
                    modelos_marca = dados_marca['modelo'].unique()
                    
                    if len(modelos_marca) > 1:  # Só analisa se há múltiplos modelos
                        for modelo in modelos_marca:
                            dados_modelo = dados_marca[dados_marca['modelo'] == modelo]
                            
                            if len(dados_modelo) > 20:  # Dados suficientes
                                dispersao_modelo.append({
                                    'marca': marca,
                                    'modelo': modelo,
                                    'rpm_medio': dados_modelo['rpm'].mean(),
                                    'rpm_desvio': dados_modelo['rpm'].std(),
                                    'rpm_min': dados_modelo['rpm'].min(),
                                    'rpm_max': dados_modelo['rpm'].max(),
                                    'coef_variacao': (dados_modelo['rpm'].std() / dados_modelo['rpm'].mean()) * 100,
                                    'total_registros': len(dados_modelo),
                                    'total_unidades': dados_modelo['unidade_nome'].nunique()
                                })
            
            df_dispersao = pd.DataFrame(dispersao_modelo)
            df_dispersao = df_dispersao.sort_values(['marca', 'coef_variacao'])
            df_dispersao.to_excel(f'{deposito}/estudo_02_dispersao_por_modelo.xlsx', index=False)
            print(f"💾 Análise de dispersão por modelo salva em: estudo_02_dispersao_por_modelo.xlsx")
            
            # ============= COMPARATIVO ENTRE MARCAS =============
            print(f"\n⚖️ {colored('Gerando comparativo entre marcas...', 'blue')}")
            
            comparativo_marcas = {}
            
            for marca in df['marca'].unique():
                if marca != 'N/I':  # Ignora registros sem marca
                    dados_marca = df[df['marca'] == marca]
                    
                    comparativo_marcas[marca] = {
                        'total_registros': len(dados_marca),
                        'total_unidades': dados_marca['unidade_id'].nunique(),
                        'rpm_medio': dados_marca['rpm'].mean(),
                        'rpm_desvio': dados_marca['rpm'].std(),
                        'velocidade_media': dados_marca['velocidade'].mean(),
                        'altitude_media': dados_marca['altitude'].mean(),
                        'percentual_zona_verde': len(dados_marca[(dados_marca['rpm'] >= 800) & (dados_marca['rpm'] <= 1300)]) / len(dados_marca) * 100,
                        'percentual_zona_vermelha': len(dados_marca[dados_marca['rpm'] > 2300]) / len(dados_marca) * 100,
                        'coef_variacao_rpm': (dados_marca['rpm'].std() / dados_marca['rpm'].mean()) * 100,
                        'empresas': list(dados_marca['empresa'].unique())
                    }
            
            # Converter para DataFrame
            comparativo_df = pd.DataFrame(comparativo_marcas).T
            comparativo_df = comparativo_df.round(2)
            comparativo_df = comparativo_df.sort_values('rpm_medio')  # Ordenar por eficiência
            
            # Salvar comparativo
            comparativo_df.to_excel(f'{deposito}/estudo_02_comparativo_marcas.xlsx')
            print(f"💾 Comparativo entre marcas salvo em: estudo_02_comparativo_marcas.xlsx")
            
            # ============= ANÁLISE TEMPORAL =============
            print(f"\n⏰ {colored('Analisando padrões temporais...', 'blue')}")
            
            # Por hora do dia
            analise_hora = df.groupby('hora').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_hora.columns = ['_'.join(col).strip() for col in analise_hora.columns]
            analise_hora = analise_hora.reset_index()
            
            # Por dia da semana
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            analise_dia_semana = df.groupby('dia_semana').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_dia_semana.columns = ['_'.join(col).strip() for col in analise_dia_semana.columns]
            analise_dia_semana = analise_dia_semana.reset_index()
            analise_dia_semana['dia_nome'] = analise_dia_semana['dia_semana'].map(lambda x: dias_semana[x])
            
            # Por mês
            analise_mes = df.groupby('mes').agg({
                'rpm': ['mean', 'std', 'count'],
                'velocidade': ['mean', 'std'],
                'altitude': ['mean', 'std']
            }).round(2)
            analise_mes.columns = ['_'.join(col).strip() for col in analise_mes.columns]
            analise_mes = analise_mes.reset_index()
            
            # Análise temporal por marca
            analise_temporal_marca = df.groupby(['marca', 'hora']).agg({
                'rpm': 'mean',
                'velocidade': 'mean'
            }).round(2).reset_index()
            
            # Salvar análises temporais
            with pd.ExcelWriter(f'{deposito}/estudo_02_analise_temporal.xlsx') as writer:
                analise_hora.to_excel(writer, sheet_name='Por_Hora', index=False)
                analise_dia_semana.to_excel(writer, sheet_name='Por_Dia_Semana', index=False)
                analise_mes.to_excel(writer, sheet_name='Por_Mes', index=False)
                analise_temporal_marca.to_excel(writer, sheet_name='Marca_por_Hora', index=False)
            
            print(f"💾 Análise temporal salva em: estudo_02_analise_temporal.xlsx")
            
            # ============= ANÁLISE DE CORRELAÇÕES =============
            print(f"\n🔗 {colored('Analisando correlações...', 'blue')}")
            
            # Matriz de correlação geral
            correlation_matrix = df[['rpm', 'velocidade', 'altitude', 'hora', 'dia_semana']].corr()
            
            # Correlações por marca (se houver dados suficientes)
            correlacoes_por_marca = {}
            for marca in df['marca'].unique():
                if marca != 'N/I':
                    dados_marca = df[df['marca'] == marca]
                    if len(dados_marca) > 50:  # Só calcula se houver dados suficientes
                        correlacoes_por_marca[marca] = dados_marca[['rpm', 'velocidade', 'altitude']].corr()
            
            # Salvar correlações
            with pd.ExcelWriter(f'{deposito}/estudo_02_matriz_correlacao.xlsx') as writer:
                correlation_matrix.to_excel(writer, sheet_name='Geral')
                for marca, corr_matrix in correlacoes_por_marca.items():
                    corr_matrix.to_excel(writer, sheet_name=f'Marca_{marca}')
            
            print(f"💾 Matriz de correlação salva em: estudo_02_matriz_correlacao.xlsx")
            
            # ============= CLUSTERING ANÁLISE =============
            print(f"\n🎯 {colored('Realizando análise de clusters...', 'blue')}")
            
            # Preparar dados para clustering
            features_clustering = df[['rpm', 'velocidade', 'altitude']].copy()
            
            # Normalizar dados
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features_clustering)
            
            # K-Means com k=5
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_normalized)
            
            # Adicionar clusters ao DataFrame
            df_clusters = df.copy()
            df_clusters['cluster'] = clusters
            
            # Analisar características de cada cluster
            cluster_analysis = df_clusters.groupby('cluster').agg({
                'rpm': ['mean', 'std', 'min', 'max', 'count'],
                'velocidade': ['mean', 'std', 'min', 'max'],
                'altitude': ['mean', 'std', 'min', 'max'],
                'unidade_id': 'nunique'
            }).round(2)
            
            cluster_analysis.columns = ['_'.join(col).strip() for col in cluster_analysis.columns]
            cluster_analysis = cluster_analysis.reset_index()
            
            # Análise de clusters por marca
            cluster_por_marca = df_clusters.groupby(['marca', 'cluster']).size().reset_index(name='count')
            cluster_por_marca_pivot = cluster_por_marca.pivot(index='marca', columns='cluster', values='count').fillna(0)
            
            # Adicionar interpretação dos clusters
            def interpretar_cluster(row):
                rpm_mean = row['rpm_mean']
                vel_mean = row['velocidade_mean']
                
                if rpm_mean < 800:
                    rpm_cat = "Marcha Lenta"
                elif rpm_mean < 1300:
                    rpm_cat = "Econômico"
                elif rpm_mean < 2000:
                    rpm_cat = "Normal"
                else:
                    rpm_cat = "Alto"
                
                if vel_mean < 20:
                    vel_cat = "Parado/Lento"
                elif vel_mean < 50:
                    vel_cat = "Urbano"
                elif vel_mean < 80:
                    vel_cat = "Rodoviário"
                else:
                    vel_cat = "Alto"
                
                return f"{rpm_cat} + {vel_cat}"
            
            cluster_analysis['interpretacao'] = cluster_analysis.apply(interpretar_cluster, axis=1)
            
            # Salvar análise de clusters
            with pd.ExcelWriter(f'{deposito}/estudo_02_analise_clusters.xlsx') as writer:
                cluster_analysis.to_excel(writer, sheet_name='Clusters_Geral', index=False)
                cluster_por_marca_pivot.to_excel(writer, sheet_name='Clusters_por_Marca')
            
            print(f"💾 Análise de clusters salva em: estudo_02_analise_clusters.xlsx")
            
            # ============= DETECÇÃO DE PADRÕES ESPECÍFICOS =============
            print(f"\n🔍 {colored('Detectando padrões específicos...', 'blue')}")
            
            padroes_especificos = {}
            
            # 1. Padrão de marcha lenta excessiva
            marcha_lenta = df[df['rpm'] < 500]
            padroes_especificos['marcha_lenta_excessiva'] = {
                'total_registros': len(marcha_lenta),
                'unidades_afetadas': marcha_lenta['unidade_nome'].nunique(),
                'percentual_total': round(len(marcha_lenta) / len(df) * 100, 2),
                'por_marca': dict(marcha_lenta['marca'].value_counts())
            }
            
            # 2. Padrão de RPM muito alto (zona vermelha)
            rpm_alto = df[df['rpm'] > 2300]
            padroes_especificos['rpm_zona_vermelha'] = {
                'total_registros': len(rpm_alto),
                'unidades_afetadas': rpm_alto['unidade_nome'].nunique(),
                'percentual_total': round(len(rpm_alto) / len(df) * 100, 2),
                'por_marca': dict(rpm_alto['marca'].value_counts())
            }
            
            # 3. Padrão de velocidade alta com RPM baixo
            vel_alta_rpm_baixo = df[(df['velocidade'] > 60) & (df['rpm'] < 1000)]
            padroes_especificos['velocidade_alta_rpm_baixo'] = {
                'total_registros': len(vel_alta_rpm_baixo),
                'unidades_afetadas': vel_alta_rpm_baixo['unidade_nome'].nunique(),
                'percentual_total': round(len(vel_alta_rpm_baixo) / len(df) * 100, 2),
                'por_marca': dict(vel_alta_rpm_baixo['marca'].value_counts())
            }
            
            # 4. Padrão noturno (22h às 6h)
            periodo_noturno = df[(df['hora'] >= 22) | (df['hora'] <= 6)]
            padroes_especificos['atividade_noturna'] = {
                'total_registros': len(periodo_noturno),
                'unidades_afetadas': periodo_noturno['unidade_nome'].nunique(),
                'percentual_total': round(len(periodo_noturno) / len(df) * 100, 2),
                'por_marca': dict(periodo_noturno['marca'].value_counts())
            }
            
            # 5. Eficiência por faixa de RPM
            df['faixa_rpm'] = pd.cut(
                df['rpm'], 
                bins=[0, 799, 1300, 2300, float('inf')], 
                labels=['Azul (350-799)', 'Verde (800-1300)', 'Amarela (1301-2300)', 'Vermelha (2301+)']
            )
            
            distribuicao_rpm = df['faixa_rpm'].value_counts().to_dict()
            distribuicao_rpm_por_marca = df.groupby(['marca', 'faixa_rpm']).size().unstack(fill_value=0)
            
            padroes_especificos['distribuicao_faixas_rpm'] = distribuicao_rpm
            
            # Salvar padrões específicos
            with pd.ExcelWriter(f'{deposito}/estudo_02_padroes_especificos.xlsx') as writer:
                # Sheet com resumo dos padrões
                padroes_resumo = pd.DataFrame([padroes_especificos]).T
                padroes_resumo.to_excel(writer, sheet_name='Resumo_Padroes')
                
                # Sheet com distribuição RPM por marca
                distribuicao_rpm_por_marca.to_excel(writer, sheet_name='RPM_por_Marca')
            
            print(f"💾 Padrões específicos salvos em: estudo_02_padroes_especificos.xlsx")
            
            # ============= GERAR GRÁFICOS =============
            print(f"\n📊 {colored('Gerando gráficos de análise...', 'blue')}")
            
            # Configurar estilo dos gráficos
            plt.style.use('default')
            sns.set_palette("husl")
            
            # 1. Distribuições das variáveis principais
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Distribuições das Variáveis Principais', fontsize=16, fontweight='bold')
            
            # RPM
            axes[0, 0].hist(df['rpm'], bins=50, alpha=0.7, color='blue')
            axes[0, 0].set_title('Distribuição RPM')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Frequência')
            axes[0, 0].axvline(df['rpm'].mean(), color='red', linestyle='--', label=f'Média: {df["rpm"].mean():.0f}')
            axes[0, 0].legend()
            
            # Velocidade
            axes[0, 1].hist(df['velocidade'], bins=50, alpha=0.7, color='green')
            axes[0, 1].set_title('Distribuição Velocidade')
            axes[0, 1].set_xlabel('Velocidade (km/h)')
            axes[0, 1].set_ylabel('Frequência')
            axes[0, 1].axvline(df['velocidade'].mean(), color='red', linestyle='--', label=f'Média: {df["velocidade"].mean():.1f}')
            axes[0, 1].legend()
            
            # Altitude
            axes[1, 0].hist(df['altitude'], bins=50, alpha=0.7, color='orange')
            axes[1, 0].set_title('Distribuição Altitude')
            axes[1, 0].set_xlabel('Altitude (m)')
            axes[1, 0].set_ylabel('Frequência')
            axes[1, 0].axvline(df['altitude'].mean(), color='red', linestyle='--', label=f'Média: {df["altitude"].mean():.1f}')
            axes[1, 0].legend()
            
            # Distribuição por faixa de RPM
            faixa_counts = df['faixa_rpm'].value_counts()
            axes[1, 1].pie(faixa_counts.values, labels=faixa_counts.index, autopct='%1.1f%%')
            axes[1, 1].set_title('Distribuição por Faixa de RPM')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_02_distribuicoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # ============= GRÁFICOS DE DISPERSÃO RPM AVANÇADOS =============
            print(f"\n📈 {colored('Gerando gráficos de dispersão RPM avançados...', 'blue')}")
            
            # 2. Gráfico de dispersão RPM por marca (com identificação de outliers)
            marcas_validas = [marca for marca in df['marca'].unique() if marca != 'N/I']
            
            if len(marcas_validas) > 1:
                # Gráfico 1: Dispersão RPM por marca com boxplots
                fig, axes = plt.subplots(2, 2, figsize=(20, 16))
                fig.suptitle('Análise de Dispersão RPM por Marca', fontsize=16, fontweight='bold')
                
                # Subplot 1: Boxplot RPM por marca
                dados_boxplot = [df[df['marca'] == marca]['rpm'] for marca in marcas_validas if len(df[df['marca'] == marca]) > 100]
                marcas_boxplot = [marca for marca in marcas_validas if len(df[df['marca'] == marca]) > 100]
                
                if dados_boxplot:
                    axes[0, 0].boxplot(dados_boxplot, labels=marcas_boxplot, patch_artist=True)
                    axes[0, 0].set_title('Distribuição RPM por Marca (Boxplot)')
                    axes[0, 0].set_xlabel('Marca')
                    axes[0, 0].set_ylabel('RPM')
                    axes[0, 0].tick_params(axis='x', rotation=45)
                    axes[0, 0].grid(True, alpha=0.3)
                    
                    # Adicionar linhas de referência
                    axes[0, 0].axhline(800, color='green', linestyle='--', alpha=0.7, label='Zona Verde (800)')
                    axes[0, 0].axhline(1300, color='green', linestyle='--', alpha=0.7, label='Zona Verde (1300)')
                    axes[0, 0].axhline(2300, color='red', linestyle='--', alpha=0.7, label='Zona Vermelha (2300)')
                    axes[0, 0].legend()
                
                # Subplot 2: Violin plot para mostrar distribuição completa
                df_plot = df[df['marca'].isin(marcas_boxplot)]
                import seaborn as sns
                sns.violinplot(data=df_plot, x='marca', y='rpm', ax=axes[0, 1])
                axes[0, 1].set_title('Distribuição RPM por Marca (Violin Plot)')
                axes[0, 1].set_xlabel('Marca')
                axes[0, 1].set_ylabel('RPM')
                axes[0, 1].tick_params(axis='x', rotation=45)
                
                # Subplot 3: Scatter plot RPM vs Velocidade colorido por marca
                cores_marca = plt.cm.Set1(np.linspace(0, 1, len(marcas_validas)))
                for i, marca in enumerate(marcas_validas):
                    dados_marca = df[df['marca'] == marca]
                    axes[1, 0].scatter(dados_marca['rpm'], dados_marca['velocidade'], 
                                    alpha=0.3, s=1, label=marca, c=[cores_marca[i]])
                
                axes[1, 0].set_title('RPM vs Velocidade por Marca')
                axes[1, 0].set_xlabel('RPM')
                axes[1, 0].set_ylabel('Velocidade (km/h)')
                axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                axes[1, 0].grid(True, alpha=0.3)
                
                # Subplot 4: Média RPM por marca com barras de erro
                marca_stats = []
                for marca in marcas_validas:
                    dados_marca = df[df['marca'] == marca]
                    if len(dados_marca) > 50:
                        marca_stats.append({
                            'marca': marca,
                            'rpm_mean': dados_marca['rpm'].mean(),
                            'rpm_std': dados_marca['rpm'].std()
                        })
                
                if marca_stats:
                    df_stats = pd.DataFrame(marca_stats).sort_values('rpm_mean')
                    axes[1, 1].bar(df_stats['marca'], df_stats['rpm_mean'], 
                                yerr=df_stats['rpm_std'], capsize=5, alpha=0.7)
                    axes[1, 1].set_title('RPM Médio por Marca (com Desvio Padrão)')
                    axes[1, 1].set_xlabel('Marca')
                    axes[1, 1].set_ylabel('RPM Médio')
                    axes[1, 1].tick_params(axis='x', rotation=45)
                    axes[1, 1].grid(True, alpha=0.3)
                    
                    # Adicionar linhas de referência
                    axes[1, 1].axhline(1050, color='green', linestyle='-', alpha=0.7, label='Zona Verde Média')
                    axes[1, 1].legend()
                
                plt.tight_layout()
                plt.savefig(f'{deposito}/estudo_02_dispersao_rpm_marcas.png', dpi=300, bbox_inches='tight')
                plt.close()
            
            # 3. Gráfico de unidades fora do padrão por marca
            if desvios_detalhados:
                fig, axes = plt.subplots(2, 2, figsize=(20, 16))
                fig.suptitle('Análise de Unidades Fora do Padrão por Marca', fontsize=16, fontweight='bold')
                
                # Subplot 1: Número de unidades fora do padrão por marca
                marca_desvios = {}
                for marca, dados in desvios_por_marca.items():
                    marca_desvios[marca] = dados['unidades_fora_padrao']
                
                marcas = list(marca_desvios.keys())
                valores = list(marca_desvios.values())
                
                axes[0, 0].bar(marcas, valores, color='red', alpha=0.7)
                axes[0, 0].set_title('Unidades Fora do Padrão por Marca')
                axes[0, 0].set_xlabel('Marca')
                axes[0, 0].set_ylabel('Número de Unidades Fora do Padrão')
                axes[0, 0].tick_params(axis='x', rotation=45)
                
                # Subplot 2: Percentual de unidades fora do padrão
                percentuais = [desvios_por_marca[marca]['percentual_fora_padrao'] for marca in marcas]
                axes[0, 1].bar(marcas, percentuais, color='orange', alpha=0.7)
                axes[0, 1].set_title('Percentual de Unidades Fora do Padrão')
                axes[0, 1].set_xlabel('Marca')
                axes[0, 1].set_ylabel('Percentual (%)')
                axes[0, 1].tick_params(axis='x', rotation=45)
                
                # Subplot 3: Scatter plot dos desvios
                if desvios_detalhados:
                    df_desvios_plot = pd.DataFrame(desvios_detalhados)
                    cores = ['red' if status == 'Acima' else 'blue' for status in df_desvios_plot['status']]
                    
                    axes[1, 0].scatter(df_desvios_plot['rpm_medio_marca'], df_desvios_plot['rpm_unidade'], 
                                    c=cores, alpha=0.6, s=50)
                    axes[1, 0].plot([400, 2500], [400, 2500], 'k--', alpha=0.5, label='Linha de Igualdade')
                    axes[1, 0].set_title('RPM Unidade vs RPM Médio da Marca')
                    axes[1, 0].set_xlabel('RPM Médio da Marca')
                    axes[1, 0].set_ylabel('RPM da Unidade')
                    axes[1, 0].legend()
                    axes[1, 0].grid(True, alpha=0.3)
                
                # Subplot 4: Histograma dos Z-scores
                if desvios_detalhados:
                    z_scores = [item['z_score'] for item in desvios_detalhados]
                    axes[1, 1].hist(z_scores, bins=20, alpha=0.7, color='purple')
                    axes[1, 1].axvline(2, color='red', linestyle='--', label='Limite Z-Score = 2')
                    axes[1, 1].set_title('Distribuição dos Z-Scores das Unidades Fora do Padrão')
                    axes[1, 1].set_xlabel('Z-Score')
                    axes[1, 1].set_ylabel('Frequência')
                    axes[1, 1].legend()
                    axes[1, 1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig(f'{deposito}/estudo_02_unidades_fora_padrao_graficos.png', dpi=300, bbox_inches='tight')
                plt.close()
            
            # 4. Análise temporal de dispersão
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise Temporal dos Dados', fontsize=16, fontweight='bold')
            
            # RPM por hora
            hourly_rpm = df.groupby('hora')['rpm'].mean()
            axes[0, 0].plot(hourly_rpm.index, hourly_rpm.values, marker='o', linewidth=2)
            axes[0, 0].set_title('RPM Médio por Hora do Dia')
            axes[0, 0].set_xlabel('Hora')
            axes[0, 0].set_ylabel('RPM Médio')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Velocidade por hora
            hourly_vel = df.groupby('hora')['velocidade'].mean()
            axes[0, 1].plot(hourly_vel.index, hourly_vel.values, marker='s', color='green', linewidth=2)
            axes[0, 1].set_title('Velocidade Média por Hora do Dia')
            axes[0, 1].set_xlabel('Hora')
            axes[0, 1].set_ylabel('Velocidade Média (km/h)')
            axes[0, 1].grid(True, alpha=0.3)
            
            # RPM por dia da semana
            daily_rpm = df.groupby('dia_semana')['rpm'].mean()
            dias_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            axes[1, 0].bar(range(7), daily_rpm.values, color='purple', alpha=0.7)
            axes[1, 0].set_title('RPM Médio por Dia da Semana')
            axes[1, 0].set_xlabel('Dia da Semana')
            axes[1, 0].set_ylabel('RPM Médio')
            axes[1, 0].set_xticks(range(7))
            axes[1, 0].set_xticklabels(dias_nome)
            
            # Atividade por mês
            monthly_count = df.groupby('mes').size()
            axes[1, 1].bar(monthly_count.index, monthly_count.values, color='red', alpha=0.7)
            axes[1, 1].set_title('Atividade por Mês')
            axes[1, 1].set_xlabel('Mês')
            axes[1, 1].set_ylabel('Número de Registros')
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_02_analise_temporal.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 5. Scatter plots e correlações
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise de Correlações', fontsize=16, fontweight='bold')
            
            # RPM vs Velocidade
            axes[0, 0].scatter(df['rpm'], df['velocidade'], alpha=0.1, s=1)
            axes[0, 0].set_title('RPM vs Velocidade')
            axes[0, 0].set_xlabel('RPM')
            axes[0, 0].set_ylabel('Velocidade (km/h)')
            
            # RPM vs Altitude
            axes[0, 1].scatter(df['rpm'], df['altitude'], alpha=0.1, s=1, color='green')
            axes[0, 1].set_title('RPM vs Altitude')
            axes[0, 1].set_xlabel('RPM')
            axes[0, 1].set_ylabel('Altitude (m)')
            
            # Velocidade vs Altitude
            axes[1, 0].scatter(df['velocidade'], df['altitude'], alpha=0.1, s=1, color='red')
            axes[1, 0].set_title('Velocidade vs Altitude')
            axes[1, 0].set_xlabel('Velocidade (km/h)')
            axes[1, 0].set_ylabel('Altitude (m)')
            
            # Heatmap de correlação
            corr_data = df[['rpm', 'velocidade', 'altitude', 'hora']].corr()
            im = axes[1, 1].imshow(corr_data, cmap='coolwarm', aspect='auto')
            axes[1, 1].set_title('Matriz de Correlação')
            axes[1, 1].set_xticks(range(len(corr_data.columns)))
            axes[1, 1].set_yticks(range(len(corr_data.columns)))
            axes[1, 1].set_xticklabels(corr_data.columns)
            axes[1, 1].set_yticklabels(corr_data.columns)
            
            plt.tight_layout()
            plt.savefig(f'{deposito}/estudo_02_correlacoes.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 Gráficos salvos em:")
            print(f"   - estudo_02_distribuicoes.png")
            print(f"   - estudo_02_dispersao_rpm_marcas.png")
            print(f"   - estudo_02_unidades_fora_padrao_graficos.png")
            print(f"   - estudo_02_analise_temporal.png")
            print(f"   - estudo_02_correlacoes.png")
            
            # ============= RELATÓRIO RESUMO =============
            print(f"\n📋 {colored('Gerando relatório resumo...', 'blue')}")
            
            marca_rpm = df.groupby('marca')['rpm'].mean().sort_values()
            
            resumo = {
                'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_registros': len(df),
                'total_unidades': df['unidade_id'].nunique(),
                'total_empresas': df['empresa'].nunique(),
                'total_marcas': df['marca'].nunique(),
                'total_modelos': df['modelo'].nunique(),
                'periodo_dados': f"{df['datetime'].min()} até {df['datetime'].max()}",
                'rpm_medio_geral': round(df['rpm'].mean(), 2),
                'rpm_desvio_padrao': round(df['rpm'].std(), 2),
                'velocidade_media_geral': round(df['velocidade'].mean(), 2),
                'altitude_media_geral': round(df['altitude'].mean(), 2),
                'outliers_detectados': len(all_outliers),
                'percentual_outliers': round(len(all_outliers) / len(df) * 100, 2),
                'distribuicao_faixas_rpm': dict(df['faixa_rpm'].value_counts()),
                'marca_mais_eficiente': marca_rpm.index[0] if len(marca_rpm) > 0 else 'N/A',
                'marca_menos_eficiente': marca_rpm.index[-1] if len(marca_rpm) > 0 else 'N/A',
                'padroes_identificados': len(padroes_especificos),
                'unidades_fora_padrao_total': len(desvios_detalhados),
                'marcas_analisadas_dispersao': len(desvios_por_marca),
            }
            
            # Salvar resumo
            resumo_df = pd.DataFrame([resumo]).T
            resumo_df.columns = ['Valor']
            resumo_df.to_excel(f'{deposito}/estudo_02_resumo_executivo.xlsx')
            
            # ============= RESULTADO FINAL =============
            print(colored("="*50, 'cyan'))
            print(colored("ESTUDO ESTATÍSTICO AVANÇADO CONCLUÍDO COM SUCESSO!", 'green'))
            print(colored("="*50, 'cyan'))
            
            print(f"📊 {colored('RESUMO DOS RESULTADOS:', 'yellow')}")
            print(f"   • Total de registros analisados: {colored(f'{len(df):,}', 'green')}")
            print(f"   • Unidades analisadas: {colored(df['unidade_id'].nunique(), 'green')}")
            print(f"   • Empresas envolvidas: {colored(df['empresa'].nunique(), 'green')}")
            print(f"   • Marcas analisadas: {colored(df['marca'].nunique(), 'blue')}")
            print(f"   • Modelos analisados: {colored(df['modelo'].nunique(), 'blue')}")
            print(f"   • Outliers detectados: {colored(f'{len(all_outliers):,}', 'red')} ({colored(f'{len(all_outliers)/len(df)*100:.1f}%', 'red')})")
            print(f"   • RPM médio da frota: {colored(f'{df.rpm.mean():.0f}', 'blue')} RPM")
            print(f"   • Velocidade média: {colored(f'{df.velocidade.mean():.1f}', 'blue')} km/h")
            
            print(f"\n🏭 {colored('ANÁLISE POR MARCA:', 'yellow')}")
            if len(marca_rpm) > 0:
                print(f"   • Marca mais eficiente: {colored(marca_rpm.index[0], 'green')} ({colored(f'{marca_rpm.iloc[0]:.0f}', 'green')} RPM)")
                print(f"   • Marca menos eficiente: {colored(marca_rpm.index[-1], 'red')} ({colored(f'{marca_rpm.iloc[-1]:.0f}', 'red')} RPM)")
            
            print(f"\n🎯 {colored('ANÁLISE DE DISPERSÃO:', 'yellow')}")
            print(f"   • Unidades fora do padrão: {colored(len(desvios_detalhados), 'red')}")
            print(f"   • Marcas com análise de dispersão: {colored(len(desvios_por_marca), 'blue')}")
            
            if desvios_por_marca:
                marca_mais_problemas = max(desvios_por_marca, key=lambda x: desvios_por_marca[x]['percentual_fora_padrao'])
                print(f"   • Marca com mais unidades fora do padrão: {colored(marca_mais_problemas, 'red')} ({colored(f'{desvios_por_marca[marca_mais_problemas]['percentual_fora_padrao']:.1f}%', 'red')})")
            
            print(f"\n📁 {colored('ARQUIVOS GERADOS:', 'yellow')}")
            print(f"   • estudo_02_estatisticas_descritivas.xlsx")
            print(f"   • estudo_02_outliers_detectados.xlsx") 
            print(f"   • estudo_02_analise_por_unidade.xlsx")
            print(f"   • estudo_02_analise_por_marca.xlsx")
            print(f"   • estudo_02_analise_por_modelo.xlsx")
            print(f"   • estudo_02_comparativo_marcas.xlsx")
            print(f"   • estudo_02_unidades_fora_padrao.xlsx")
            print(f"   • estudo_02_dispersao_por_modelo.xlsx")
            print(f"   • estudo_02_analise_temporal.xlsx")
            print(f"   • estudo_02_matriz_correlacao.xlsx")
            print(f"   • estudo_02_analise_clusters.xlsx")
            print(f"   • estudo_02_padroes_especificos.xlsx")
            print(f"   • estudo_02_resumo_executivo.xlsx")
            print(f"   • estudo_02_distribuicoes.png")
            print(f"   • estudo_02_dispersao_rpm_marcas.png")
            print(f"   • estudo_02_unidades_fora_padrao_graficos.png")
            print(f"   • estudo_02_analise_temporal.png")
            print(f"   • estudo_02_correlacoes.png")
            
            print(f"\n🎯 {colored('PRINCIPAIS INSIGHTS:', 'yellow')}")
            print(f"   • Faixa de RPM mais comum: {colored(df['faixa_rpm'].mode().iloc[0], 'green')}")
            print(f"   • Horário de maior atividade: {colored(f'{hourly_rpm.idxmax()}h', 'green')}")
            print(f"   • Correlação RPM-Velocidade: {colored(f'{df.rpm.corr(df.velocidade):.3f}', 'blue')}")
            if len(marca_rpm) > 1:
                print(f"   • Diferença de eficiência entre marcas: {colored(f'{marca_rpm.iloc[-1] - marca_rpm.iloc[0]:.0f}', 'yellow')} RPM")
            
            return True
            
        except Exception as e:
            print(f"❌ {colored(f'Erro durante a análise: {str(e)}', 'red')}")
            import traceback
            traceback.print_exc()
            return False




###-----------------------------------------------------------------------------------------------------------------#####
# INVESTIGAÇÃO #
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

    def atualizador(self,nome="atualizador_unidades"):
            def comm(msg):
                print(colored("="*30, "yellow"))
                print(colored(f"{nome}:","green"))
                print(f"{msg}")
                print(colored("="*30, "yellow"))
            #lista as empresas registradas
            contador_sessoes = 0
            empresas = Empresa.objects.all()
            for empresa in empresas:
                comm(f'Empresa: {empresa.nome}')
                # Inicia a sessão Wialon para cada empresa
                sid=Wialon.authenticate_with_wialon(empresa.token)
                comm(f'Sessão Wialon iniciada para {empresa.nome}, ID de recurso: {empresa.id_recurso}')
                if not sid:
                    self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                    continue
                if sid:
                    contador_sessoes += 1


                unidades = Wialon.unidades_simples_03(sid,empresa)
                if not unidades:
                    self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
                    return

                comm(f'Unidades encontradas: {len(unidades)}')
                #
                #+-----
                #print(f'Unidades: {colored(f"{unidades}", "green")}')
                #+-----
                #

                #coloca os dados em um dataframe
                df_unidades = pd.DataFrame(unidades)
                comm(f'Unidades encontradas: {len(df_unidades)}')
                comm(f'Unidades: {df_unidades}')
                #
                #+-----
                #df_unidades.to_excel(f'{deposito}/{empresa.nome}_unidades.xlsx', index=False)
                #comm(f'Arquivo {deposito}/{empresa.nome}_unidades.xlsx salvo.')
                #+-----
                #
                

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

                    #
                    #+---
                    #comm(f'Nome da unidade: {nome}, Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Cor: {cor}, Placa: {placa}')
                    #+---
                    #

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
                            'modelo': modelo,
                            'id_wialon': id,
                        }
                    )
                    comm(f'Veículo {nome} atualizado/criado com ID {unidade_id}.')
                
                #adiciona também os motoristas

                motoristas = Wialon.motoristas_simples2(sid)
                df_motoristas = pd.DataFrame(motoristas)
                comm(f'Motoristas encontrados: {len(df_motoristas)}')
                comm(f'Motoristas: {df_motoristas}')
                for motorista in df_motoristas.itertuples(index=False):
                    motorista_id = motorista.driver_id
                    motorista_nome = motorista.driver_name
                    cls = 'Motorista'


                    motorista_id = f"{empresa.nome}_{motorista_id}"

                    comm(f'Motorista: {motorista_nome} | ID: {motorista_id} | Classe: {cls} | Empresa: {empresa.nome}')

                    # Atualiza o motorista no banco de dados
                    Unidade.objects.update_or_create(
                        id=motorista_id,
                        defaults={
                            'nm': motorista_nome,
                            'cls': cls,
                            'empresa': empresa,
                            'id_wialon': motorista_id,
                        }
                        
                    )
            #faz logout
            Wialon.wialon_logout(sid)
            return contador_sessoes

            #-------------------------------------------------------------------------------------------------------------#

    def atualizador_02(self,sid, nome="atualizador_unidades", empresa='CPBracell', flags=8388609):
            def comm(msg):
                print(colored("="*30, "yellow"))
                print(colored(f"{nome}:","green"))
                print(f"{msg}")
                print(colored("="*30, "yellow"))


            unidades = Wialon.unidades_simples_04(sid, empresa=empresa, flags=flags)
            if not unidades:
                self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
                return

            comm(f'Unidades encontradas: {len(unidades)}')
            #
            #+-----
            #print(f'Unidades: {colored(f"{unidades}", "green")}')
            #+-----
            #

            #coloca os dados em um dataframe
            df_unidades = pd.DataFrame(unidades)
            comm(f'Unidades encontradas: {len(df_unidades)}')
            comm(f'Unidades: {df_unidades}')
            #
            #+-----
            #df_unidades.to_excel(f'{deposito}/{empresa.nome}_unidades.xlsx', index=False)
            #comm(f'Arquivo {deposito}/{empresa.nome}_unidades.xlsx salvo.')
            #+-----
            #
            

            for unidade in df_unidades.itertuples(index=False):
                id=unidade.unit_id
                nome=unidade.unit_name
                marca=unidade.brand
                modelo=unidade.model
                ano=unidade.year
                cor=unidade.color
                placa=unidade.registration_plate
                cls = 'Veículo'
                unidade_id = f"{empresa}_{id}"

                #
                #+---
                #comm(f'Nome da unidade: {nome}, Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Cor: {cor}, Placa: {placa}')
                #+---
                #

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
                        'modelo': modelo,
                        'id_wialon': id,
                    }
                )
                comm(f'Veículo {nome} atualizado/criado com ID {unidade_id}.')
            
            #adiciona também os motoristas

            motoristas = Wialon.motoristas_simples2(sid)
            df_motoristas = pd.DataFrame(motoristas)
            comm(f'Motoristas encontrados: {len(df_motoristas)}')
            comm(f'Motoristas: {df_motoristas}')
            for motorista in df_motoristas.itertuples(index=False):
                motorista_id = motorista.driver_id
                motorista_nome = motorista.driver_name
                cls = 'Motorista'


                motorista_id = f"{empresa}_{motorista_id}"

                comm(f'Motorista: {motorista_nome} | ID: {motorista_id} | Classe: {cls} | Empresa: {empresa}')

                # Atualiza o motorista no banco de dados
                Unidade.objects.update_or_create(
                    id=motorista_id,
                    defaults={
                        'nm': motorista_nome,
                        'cls': cls,
                        'empresa': empresa,
                        'id_wialon': motorista_id,
                    }
                    
                )

    def atualizador_03(self,sid,id_criador,  flags=8388613):
        

        def comm(msg):
            print(colored("="*30, "yellow"))
            print(colored(f"Atualizador de Unidades:","green"))
            print(f"{msg}")
            print(colored("="*30, "yellow"))


        unidades = Wialon.unidades_simples_05(sid,  flags=flags)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return

        comm(f'Unidades encontradas: {len(unidades)}')
        #coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        comm(f'Unidades encontradas: {len(df_unidades)}')
        comm(f'Unidades: {df_unidades}')

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
                print(f'A unidade {nome} pertence à empresa CARGO POLO.')
                empresa = Empresa.objects.get(id_criador=id_criador)
                print(colored(f'Empresa encontrada: {empresa.nome}, ID Criador: {empresa.id_criador}', 'red'))
                empresa_nome = empresa.nome
                unidade_id = f"{empresa.nome}_{id}"


                comm(f'Nome da unidade: {nome}, Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Cor: {cor}, Placa: {placa}')
                #+---
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
                        'modelo': modelo,
                        'id_wialon': id,
                    }
                )
                comm(f'Veículo {nome} atualizado/criado com ID {unidade_id}.')
            else:
                comm(f'A unidade {nome} não pertence à empresa CARGO POLO. ID Criador: {id_criador_unidade}')

            #adiciona também os motoristas

            motoristas = Wialon.motoristas_simples_03(sid, flags=5)
            df_motoristas = pd.DataFrame(motoristas)
            comm(f'Motoristas encontrados: {len(df_motoristas)}')
            comm(f'Motoristas: {df_motoristas}')


            for motorista in df_motoristas.itertuples(index=False):
                motorista_id = motorista.driver_id
                motorista_nome = motorista.driver_name
                cls = 'Motorista'
                id_criador_unidade = unidade.id_criador
                if id_criador_unidade == id_criador:
                    print(f'A unidade {nome} pertence à empresa CARGO POLO.')
                    empresa = Empresa.objects.get(id_criador=id_criador)
                    print(colored(f'Empresa encontrada: {empresa.nome}, ID Criador: {empresa.id_criador}', 'red'))
                    empresa_nome = empresa.nome
                    unidade_id = f"{empresa.nome}_{id}"


                    motorista_id = f"{empresa}_{motorista_id}"

                    comm(f'Motorista: {motorista_nome} | ID: {motorista_id} | Classe: {cls} | Empresa: {empresa}')

                    # Atualiza o motorista no banco de dados
                    Unidade.objects.update_or_create(
                        id=motorista_id,
                        defaults={
                            'nm': motorista_nome,
                            'cls': cls,
                            'empresa': empresa,
                            'id_wialon': motorista_id,
                        }
                        
                    )
                else:
                    comm(f'A unidade {nome} não pertence à empresa CARGO POLO. ID Criador: {id_criador_unidade}')




    def atualizador_teste(self, sid, nome="atualizador_unidades_04", flags=8388613):
        def comm(msg):
            print(colored("="*30, "yellow"))
            print(colored(f"{nome}:", "green"))
            print(f"{msg}")
            print(colored("="*30, "yellow"))

        unidades = Wialon.unidades_simples_05(sid, flags=flags)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return

        comm(f'Unidades encontradas: {len(unidades)}')
        
        # Coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        comm(f'Unidades encontradas: {len(df_unidades)}')
        
        # Busca todas as empresas cadastradas com seus id_criador
        empresas_dict = {}
        empresas = Empresa.objects.all()
        
        for empresa in empresas:
            if empresa.id_criador:
                empresas_dict[empresa.id_criador] = empresa
                comm(f'Empresa cadastrada: {empresa.nome} - ID Criador: {empresa.id_criador}')

        if not empresas_dict:
            comm("⚠️ Nenhuma empresa com id_criador encontrada. Verifique o cadastro das empresas.")
            return

        # Contadores para estatísticas
        unidades_processadas = 0
        unidades_vinculadas = 0
        unidades_sem_empresa = 0

        for unidade in df_unidades.itertuples(index=False):
            unidades_processadas += 1
            
            # Extrai dados da unidade
            unit_id = unidade.unit_id
            unit_name = unidade.unit_name
            id_criador_unidade = unidade.id_criador
            
            # Extrai campos do profile se existirem
            brand = getattr(unidade, 'brand', '')
            model = getattr(unidade, 'model', '')
            year = getattr(unidade, 'year', '')
            color = getattr(unidade, 'color', '')
            registration_plate = getattr(unidade, 'registration_plate', '')
            
            # Verifica se a unidade pertence a alguma empresa cadastrada
            empresa_vinculada = empresas_dict.get(id_criador_unidade)
            
            if empresa_vinculada:
                unidades_vinculadas += 1
                cls = 'Veículo'
                
                # Cria o ID único da unidade
                unidade_id = f"{empresa_vinculada.nome}_{unit_id}"
                
                comm(f'✅ Unidade {unit_name} pertence à empresa {empresa_vinculada.nome}')
                comm(f'   Marca: {brand}, Modelo: {model}, Ano: {year}, Cor: {color}, Placa: {registration_plate}')
                
                # Atualiza/cria a unidade no banco de dados
                try:
                    veiculo, created = Veiculo.objects.update_or_create(
                        id=unidade_id,
                        defaults={
                            'nm': unit_name,
                            'placa': registration_plate,
                            'marca': brand,
                            'cls': cls,
                            'empresa': empresa_vinculada,
                            'cor': color,
                            'modelo': model,
                            'ano': int(year) if year and str(year).isdigit() else None,
                            'id_wialon': unit_id,
                            'id_criador': id_criador_unidade,
                        }
                    )
                    
                    action = "criado" if created else "atualizado"
                    comm(f'✅ Veículo {unit_name} {action} com ID {unidade_id}')
                    
                except Exception as e:
                    comm(f'❌ Erro ao processar veículo {unit_name}: {e}')
                    
            else:
                unidades_sem_empresa += 1
                comm(f'⚠️ Unidade {unit_name} (ID Criador: {id_criador_unidade}) não pertence a nenhuma empresa cadastrada')

        # Processamento dos motoristas (se necessário)
        comm("Processando motoristas...")
        motoristas = Wialon.motoristas_simples2(sid)
        df_motoristas = pd.DataFrame(motoristas)
        
        motoristas_processados = 0
        motoristas_vinculados = 0
        
        for motorista in df_motoristas.itertuples(index=False):
            motoristas_processados += 1
            
            motorista_id_wialon = motorista.driver_id
            motorista_nome = motorista.driver_name
            resource_id = motorista.resource_id
            
            # Tenta identificar a empresa do motorista pelo resource_id
            # (assumindo que o resource corresponde ao id_criador da empresa)
            empresa_motorista = empresas_dict.get(str(resource_id))
            
            if empresa_motorista:
                motoristas_vinculados += 1
                cls = 'Motorista'
                motorista_id = f"{empresa_motorista.nome}_{motorista_id_wialon}"

                comm(f'✅ Motorista {motorista_nome} pertence à empresa {empresa_motorista.nome}')

                try:
                    unidade, created = Unidade.objects.update_or_create(
                        id=motorista_id,
                        defaults={
                            'nm': motorista_nome,
                            'cls': cls,
                            'empresa': empresa_motorista,
                            'id_wialon': motorista_id_wialon,
                        }
                    )
                    
                    action = "criado" if created else "atualizado"
                    comm(f'✅ Motorista {motorista_nome} {action} com ID {motorista_id}')
                    
                except Exception as e:
                    comm(f'❌ Erro ao processar motorista {motorista_nome}: {e}')
            else:
                comm(f'⚠️ Motorista {motorista_nome} (Resource ID: {resource_id}) não pertence a nenhuma empresa cadastrada')

        # Relatório final
        comm("="*50)
        comm("RELATÓRIO FINAL:")
        comm(f"📊 Unidades processadas: {unidades_processadas}")
        comm(f"✅ Unidades vinculadas: {unidades_vinculadas}")
        comm(f"⚠️ Unidades sem empresa: {unidades_sem_empresa}")
        comm(f"📊 Motoristas processados: {motoristas_processados}")
        comm(f"✅ Motoristas vinculados: {motoristas_vinculados}")
        comm("="*50)

        # Salva log detalhado se necessário
        if unidades_sem_empresa > 0:
            comm(f"⚠️ {unidades_sem_empresa} unidades não puderam ser vinculadas.")
            comm("Verifique se os id_criador das empresas estão corretos no banco de dados.")


    ############################################################################################
    ###+---------------------------------------------------------------------------------------------+
    # DEMOLIÇÃO #
    def CLTDR_UMBRELLA(self):
        def comm(msg):
            print(colored("="*30, "blue"))
            print(colored("CLTDR_UMBRELLA:","green"))
            print(f"{msg}")
            print(colored("="*30, "blue"))
        
        comm("Iniciando processamento global...")
        sid = Wialon.authenticate_with_wialon(WIALON_TOKEN_UMBR)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return

        #Wialon.set_locale()

        ###__UNIDADES__TODAS__###
        comm("Processando Unidades...")
        processamento_df = pd.DataFrame()

        ###


        ###__CARGO__POLO__###
        # VEÍCULOS
        self.CARGO_POLO_veiculos(sid, processamento_df)
        processamento_df = pd.DataFrame()

        #motoristas
        self.CARGO_POLO_motoristas(sid, processamento_df)
        processamento_df = pd.DataFrame()

        self.CARGO_POLO(sid)

        ###__PLACIDO__###
        # VEÍCULOS
        self.PLACIDO_veiculos(sid, processamento_df)
        processamento_df = pd.DataFrame()

        #Motoristas
        self.PLACIDO_motoristas(sid, processamento_df)
        processamento_df = pd.DataFrame()

        ###__SFRESGATE__###
        # VEÍCULOS
        self.SFRESGATE_veiculos(sid, processamento_df)
        processamento_df = pd.DataFrame()
        
        #motoristas 
        self.SFRESGATE_motoristas(sid, processamento_df)
        processamento_df = pd.DataFrame()

        ###__checkpoints e infrações__###
        self.CLTDR_CP_01(sid, processamento_df, recurso=401755650, template=1, flag=16777218, Objeto=401946382, dias=30)
        processamento_df = pd.DataFrame()   

        self.CLTDR_INFRA_01(sid, processamento_df, recurso=401872803, template=7, flag=16777218, Objeto=401929585, dias=30)
        processamento_df = pd.DataFrame()

        Wialon.wialon_logout(sid)

    def SFRESGATE_motoristas(self, sid, processamento_df):
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401872803, template=48, Objeto=401872803, flag=16777224, dias=1, periodo="Últimos 30 dias")

    def SFRESGATE_veiculos(self, sid, processamento_df):
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_sfre, dias=30, periodo="Últimos 30 dias")

    def PLACIDO_motoristas(self, sid, processamento_df):
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_02(sid, processamento_df, recurso=401768999, template=48, Objeto=401768999, flag=16777224, dias=1, periodo="Últimos 30 dias")

    def PLACIDO_veiculos(self, sid, processamento_df):
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=1, periodo="Ontem")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_03(sid, processamento_df, recurso=401756219, template=59, flag=16777218, Objeto=frt_plac, dias=30, periodo="Últimos 30 dias")

    def CARGO_POLO_motoristas(self, sid, processamento_df):
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777218, dias=1, periodo="Ontem")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777220, dias=1, periodo="Últimos 7 dias")
        self.CLTDR_MOT_01(sid, processamento_df, Objeto=401756219, flag=16777224, dias=1, periodo="Últimos 30 dias")

    def CARGO_POLO_veiculos(self, sid, processamento_df):
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=1, periodo="Ontem")
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=7, periodo="Últimos 7 dias")
        self.CLTDR_04(sid, processamento_df, recurso=401756219, template=9, flag=16777218, Objeto=frt_cpbr, dias=30, periodo="Últimos 30 dias")
    
        
        
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
    #+---


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

    ###+---

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

        ###+---
    


    
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

    # DEMOLIÇÃO #
    ###+---------------------------------------------------------------------------------------------+
    ############################################################################################
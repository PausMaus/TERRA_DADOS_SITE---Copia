from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.models import Empresa, Unidade, Viagem_Base, CheckPoint, Infrações, Veiculo, ConfiguracaoSistema, Viagem_eco, Viagem_Detalhada, Driver, Estatistica_Diaria_Motorista
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
from collections import defaultdict
from datetime import date







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

        #self.UMBRELLA(cor1="blue", cor2="green")
        ##################################################
        # MENSAGENS #

        self.MENSAGENS(3,"Petitto")
        self.MENSAGENS(3,"CPBRACELL")

        #self.MENSAGENS_02(1,"Petitto")
        #self.MENSAGENS_02(1,"CPBRACELL")
        
        ##################################################
        # 🔥 GERAR ESTATÍSTICAS DIÁRIAS #
        # Descomente uma das opções abaixo:
        
        # Opção 1: Processar últimos 30 dias de todas as empresas
        self.gerar_estatisticas_de_viagens_eco(dias=30)
        
        # Opção 2: Processar últimos 7 dias da empresa Petitto
        #self.gerar_estatisticas_de_viagens_eco(empresa="Petitto", dias=7)
        
        # Opção 3: Processar TODOS os dados históricos (pode demorar)
        #self.gerar_estatisticas_de_viagens_eco()
        
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




    def UMBRELLA(self, cor1, cor2, tool="CLTDR_UMBRELLA"):
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
        #self.CLTDR_empresas(sid, cor1="blue" , cor2="white", tool= "CLTDR_empresas")

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
        #lista_unidades = Veiculo.objects.filter(nm__icontains="1037").values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas


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

                    with open(f'{deposito}/messages_{unidade_nome}_{unidade_id}.json', 'w') as f:
                        json.dump(result, f, indent=4)

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
                        
                        df_messages.to_excel(f'{deposito}/{unidade_nome}_{unidade_id}.xlsx', index=False)
                        print(f"DataFrame salvo em {deposito}/{unidade_nome}_{unidade_id}.xlsx")

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






    def MENSAGENS_02(self, tempo, empresa):
        
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

        
        #lista_unidades = Veiculo.objects.filter(nm__icontains="1037").values_list('id_wialon', flat=True)  # IDs das unidades a serem processadas
        lista_unidades = Veiculo.objects.filter(empresa__nome=empresa).values_list('id_wialon',flat=True)[:10]

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

                    with open(f'{deposito}/messages_{unidade_nome}_{unidade_id}.json', 'w') as f:
                        json.dump(result, f, indent=4)

                    if result and isinstance(result, list):
                        df_messages = self.processar_mensagens_wialon(result)

                        unidade_obj = Veiculo.objects.get(id_wialon=unidade_id)
                        if unidade_obj and not df_messages.empty:
                            motoristas_por_dia = defaultdict(lambda: {
                                'pontos': [],
                                'veiculos': set(),
                                'timestamps': []
                            })
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
                                    
                                    # Converter timestamp para data
                                    data_viagem = date.fromtimestamp(timestamp_valor)
                                    
                                    # Classificar a viagem
                                    classificacao = classificar_viagem(rpm_tratado, velocidade_valor)
                                    
                                    # Converter avl_driver para driver_code
                                    driver_code_valor = avl_to_driver_code(avl_driver_valor)
                                    nome_motorista_obj = None
                                    # Buscar motorista pelo driver_code
                                    nome_motorista_obj = None

                                    if driver_code_valor and driver_code_valor != 0:
                                        nome_motorista_obj = Driver.objects.filter(
                                            codigo=driver_code_valor,
                                            empresa=unidade_obj.empresa
                                        ).first()
                                        
                                    
                                    if nome_motorista_obj:
                                        key = (nome_motorista_obj.id, data_viagem)
                                        
                                        motoristas_por_dia[key]['pontos'].append({
                                            'rpm': rpm_tratado,
                                            'velocidade': velocidade_valor,
                                            'classificacao': classificacao
                                        })
                                        motoristas_por_dia[key]['veiculos'].add(unidade_obj.id)
                                        motoristas_por_dia[key]['timestamps'].append(timestamp_valor)

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
                            
                            # 🔥 DEBUG: Verificar dados coletados antes de processar
                            print(f"\n🔍 DEBUG - Dados coletados para estatísticas:")
                            print(f"   Total de chaves (motorista, data): {colored(len(motoristas_por_dia), 'cyan')}")
                            if motoristas_por_dia:
                                print(f"   Exemplo de chave: {list(motoristas_por_dia.keys())[0]}")
                                exemplo_dados = list(motoristas_por_dia.values())[0]
                                print(f"   Exemplo de dados: {len(exemplo_dados['pontos'])} pontos, {len(exemplo_dados['veiculos'])} veículos")
                            else:
                                print(f"   ⚠️ {colored('NENHUM DADO COLETADO!', 'yellow')}")
                            
                            # 🔥 NOVO: Criar/atualizar estatísticas diárias
                            self.processar_estatisticas_diarias(motoristas_por_dia)
                        
                        print(f"\nDataFrame criado com {len(df_messages)} mensagens:")
                        print(df_messages.head())
                        
                        df_messages.to_excel(f'{deposito}/{unidade_nome}_{unidade_id}.xlsx', index=False)
                        print(f"DataFrame salvo em {deposito}/{unidade_nome}_{unidade_id}.xlsx")

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


    def processar_estatisticas_diarias(self, motoristas_por_dia):
        """
        Processa e salva estatísticas diárias pré-calculadas
        """
        import json
        
        print(f"\n{'='*60}")
        print(f"🔥 PROCESSANDO ESTATÍSTICAS DIÁRIAS")
        print(f"{'='*60}")
        print(f"Total de motoristas/dias para processar: {colored(len(motoristas_por_dia), 'cyan')}")
        
        if not motoristas_por_dia:
            print(f"⚠️ {colored('NENHUM DADO PARA PROCESSAR!', 'yellow')}")
            return
        
        estatisticas_criadas = 0
        estatisticas_atualizadas = 0
        erros = 0
        
        for (motorista_id, data), dados in motoristas_por_dia.items():
            try:
                motorista = Driver.objects.get(id=motorista_id)
                
                # Contar pontos por classificação
                total_pontos = len(dados['pontos'])
                pontos_ocioso = sum(1 for p in dados['pontos'] if p['classificacao']['ocioso'])
                pontos_azul = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_azul'])
                pontos_verde = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_verde'])
                pontos_amarela = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_amarela'])
                pontos_vermelha = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_vermelha'])
                
                # Calcular médias
                rpm_medio = sum(p['rpm'] for p in dados['pontos']) / total_pontos if total_pontos > 0 else 0
                velocidade_media = sum(p['velocidade'] for p in dados['pontos']) / total_pontos if total_pontos > 0 else 0
                
                # Timestamps
                timestamps = sorted(dados['timestamps'])
                timestamp_inicio = timestamps[0] if timestamps else None
                timestamp_fim = timestamps[-1] if timestamps else None
                
                # Veículos
                total_veiculos = len(dados['veiculos'])
                veiculos_ids_json = json.dumps(list(dados['veiculos']))
                
                # Debug detalhado
                print(f"\n  📊 Processando: {colored(motorista.nm, 'yellow')} - {colored(data, 'cyan')}")
                print(f"     Total pontos: {total_pontos}")
                print(f"     Ocioso: {pontos_ocioso} | Azul: {pontos_azul} | Verde: {pontos_verde} | Amarela: {pontos_amarela} | Vermelha: {pontos_vermelha}")
                print(f"     RPM médio: {rpm_medio:.2f} | Velocidade média: {velocidade_media:.2f}")
                print(f"     Veículos: {total_veiculos}")
                
                # Criar ou atualizar estatística
                estatistica, created = Estatistica_Diaria_Motorista.objects.update_or_create(
                    motorista=motorista,
                    data=data,
                    defaults={
                        'total_pontos': total_pontos,
                        'pontos_ocioso': pontos_ocioso,
                        'pontos_faixa_azul': pontos_azul,
                        'pontos_faixa_verde': pontos_verde,
                        'pontos_faixa_amarela': pontos_amarela,
                        'pontos_faixa_vermelha': pontos_vermelha,
                        'rpm_medio': rpm_medio,
                        'velocidade_media': velocidade_media,
                        'timestamp_inicio': timestamp_inicio,
                        'timestamp_fim': timestamp_fim,
                        'total_veiculos': total_veiculos,
                        'veiculos_ids': veiculos_ids_json,
                    }
                )
                
                if created:
                    estatisticas_criadas += 1
                    print(f"     ✅ {colored('CRIADA', 'green')}")
                else:
                    estatisticas_atualizadas += 1
                    print(f"     🔄 {colored('ATUALIZADA', 'blue')}")
                    
            except Driver.DoesNotExist:
                erros += 1
                print(f"     ❌ {colored(f'Motorista ID {motorista_id} não encontrado', 'red')}")
                continue
            except Exception as e:
                erros += 1
                print(f"     ❌ {colored(f'Erro: {str(e)}', 'red')}")
                import traceback
                traceback.print_exc()
                continue
        
        # Resumo final
        print(f"\n{'='*60}")
        print(f"📈 RESUMO DO PROCESSAMENTO")
        print(f"{'='*60}")
        print(f"✅ Estatísticas criadas: {colored(estatisticas_criadas, 'green')}")
        print(f"🔄 Estatísticas atualizadas: {colored(estatisticas_atualizadas, 'blue')}")
        print(f"❌ Erros: {colored(erros, 'red')}")
        print(f"{'='*60}\n")

    def gerar_estatisticas_de_viagens_eco(self, empresa=None, dias=None):
        """
        🔥 FUNÇÃO STANDALONE: Processa dados de Viagem_eco e cria Estatistica_Diaria_Motorista
        Pode ser executada a qualquer momento para gerar/atualizar estatísticas
        
        Args:
            empresa: Nome da empresa (opcional, None = todas)
            dias: Número de dias para processar (opcional, None = todos os dados)
        """
        from datetime import date, timedelta
        from collections import defaultdict
        import json
        
        print(f"\n{'='*70}")
        print(f"🔥 GERANDO ESTATÍSTICAS DIÁRIAS A PARTIR DE VIAGEM_ECO")
        print(f"{'='*70}")
        
        # Construir query base
        viagens_query = Viagem_eco.objects.select_related('nome_motorista', 'unidade__empresa')
        viagens_query = viagens_query.filter(nome_motorista__isnull=False)
        
        # Filtrar por empresa se especificado
        if empresa:
            viagens_query = viagens_query.filter(unidade__empresa__nome=empresa)
            print(f"📊 Empresa filtrada: {colored(empresa, 'cyan')}")
        else:
            print(f"📊 Processando: {colored('TODAS as empresas', 'cyan')}")
        
        # Filtrar por período se especificado
        if dias:
            from datetime import datetime
            data_limite = datetime.now() - timedelta(days=dias)
            timestamp_limite = int(data_limite.timestamp())
            viagens_query = viagens_query.filter(timestamp__gte=timestamp_limite)
            print(f"📅 Período: {colored(f'Últimos {dias} dias', 'cyan')}")
        else:
            print(f"📅 Período: {colored('TODOS os dados históricos', 'yellow')}")
        
        # Contar total de viagens
        total_viagens = viagens_query.count()
        print(f"🚛 Total de viagens a processar: {colored(f'{total_viagens:,}', 'green')}")
        
        if total_viagens == 0:
            print(f"⚠️ {colored('Nenhuma viagem encontrada!', 'yellow')}")
            return
        
        print(f"\n{'─'*70}")
        print(f"🔄 Agrupando dados por motorista e data...")
        print(f"{'─'*70}\n")
        
        # Dicionário para agrupar dados: {(motorista_id, data): dados}
        motoristas_por_dia = defaultdict(lambda: {
            'pontos': [],
            'veiculos': set(),
            'timestamps': []
        })
        
        # Processar viagens em lotes para economizar memória
        batch_size = 10000
        total_processadas = 0
        
        # Usar iterator() para processar em batches
        viagens_iterator = viagens_query.iterator(chunk_size=batch_size)
        
        print(f"⏳ Processando em lotes de {batch_size:,} viagens...")
        
        for viagem in viagens_iterator:
            try:
                # Converter timestamp para data
                data_viagem = date.fromtimestamp(viagem.timestamp)
                motorista_id = viagem.nome_motorista.id
                
                # Determinar classificação
                classificacao = {
                    'ocioso': viagem.ocioso,
                    'faixa_azul': viagem.faixa_azul,
                    'faixa_verde': viagem.faixa_verde,
                    'faixa_amarela': viagem.faixa_amarela,
                    'faixa_vermelha': viagem.faixa_vermelha
                }
                
                # Calcular RPM tratado (dividir por 8 conforme sua lógica)
                rpm_tratado = (viagem.rpm / 8) if viagem.rpm else 0
                
                # Agrupar por motorista e data
                key = (motorista_id, data_viagem)
                motoristas_por_dia[key]['pontos'].append({
                    'rpm': rpm_tratado,
                    'velocidade': viagem.velocidade or 0,
                    'classificacao': classificacao
                })
                motoristas_por_dia[key]['veiculos'].add(viagem.unidade.id)
                motoristas_por_dia[key]['timestamps'].append(viagem.timestamp)
                
                total_processadas += 1
                
                # Mostrar progresso a cada 10k viagens
                if total_processadas % 10000 == 0:
                    print(f"   ⚙️ Processadas: {colored(f'{total_processadas:,}', 'cyan')} / {colored(f'{total_viagens:,}', 'green')} viagens ({total_processadas/total_viagens*100:.1f}%)")
                
            except Exception as e:
                print(f"   ⚠️ Erro ao processar viagem ID {viagem.id}: {e}")
                continue
        
        print(f"\n✅ Total de viagens processadas: {colored(f'{total_processadas:,}', 'green')}")
        print(f"📊 Total de combinações (motorista, data): {colored(len(motoristas_por_dia), 'cyan')}")
        
        # Agora criar as estatísticas
        print(f"\n{'─'*70}")
        print(f"💾 Salvando estatísticas no banco de dados...")
        print(f"{'─'*70}\n")
        
        estatisticas_criadas = 0
        estatisticas_atualizadas = 0
        erros = 0
        
        for (motorista_id, data), dados in motoristas_por_dia.items():
            try:
                motorista = Driver.objects.get(id=motorista_id)
                
                # Contar pontos por classificação
                total_pontos = len(dados['pontos'])
                pontos_ocioso = sum(1 for p in dados['pontos'] if p['classificacao']['ocioso'])
                pontos_azul = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_azul'])
                pontos_verde = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_verde'])
                pontos_amarela = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_amarela'])
                pontos_vermelha = sum(1 for p in dados['pontos'] if p['classificacao']['faixa_vermelha'])
                
                # Calcular médias
                rpm_medio = sum(p['rpm'] for p in dados['pontos']) / total_pontos if total_pontos > 0 else 0
                velocidade_media = sum(p['velocidade'] for p in dados['pontos']) / total_pontos if total_pontos > 0 else 0
                
                # Timestamps
                timestamps = sorted(dados['timestamps'])
                timestamp_inicio = timestamps[0] if timestamps else None
                timestamp_fim = timestamps[-1] if timestamps else None
                
                # Veículos
                total_veiculos = len(dados['veiculos'])
                veiculos_ids_json = json.dumps(list(dados['veiculos']))
                
                # Criar ou atualizar estatística
                estatistica, created = Estatistica_Diaria_Motorista.objects.update_or_create(
                    motorista=motorista,
                    data=data,
                    defaults={
                        'total_pontos': total_pontos,
                        'pontos_ocioso': pontos_ocioso,
                        'pontos_faixa_azul': pontos_azul,
                        'pontos_faixa_verde': pontos_verde,
                        'pontos_faixa_amarela': pontos_amarela,
                        'pontos_faixa_vermelha': pontos_vermelha,
                        'rpm_medio': rpm_medio,
                        'velocidade_media': velocidade_media,
                        'timestamp_inicio': timestamp_inicio,
                        'timestamp_fim': timestamp_fim,
                        'total_veiculos': total_veiculos,
                        'veiculos_ids': veiculos_ids_json,
                    }
                )
                
                if created:
                    estatisticas_criadas += 1
                else:
                    estatisticas_atualizadas += 1
                
                # Mostrar progresso
                total_stats = estatisticas_criadas + estatisticas_atualizadas
                if total_stats % 50 == 0:
                    print(f"   💾 Salvas: {colored(total_stats, 'cyan')} estatísticas...")
                    
            except Driver.DoesNotExist:
                erros += 1
                print(f"   ❌ Motorista ID {motorista_id} não encontrado")
                continue
            except Exception as e:
                erros += 1
                print(f"   ❌ Erro ao salvar estatística para motorista {motorista_id} - {data}: {e}")
                continue
        
        # Resumo final
        print(f"\n{'='*70}")
        print(f"📊 RESUMO FINAL")
        print(f"{'='*70}")
        print(f"✅ Estatísticas CRIADAS: {colored(estatisticas_criadas, 'green')}")
        print(f"🔄 Estatísticas ATUALIZADAS: {colored(estatisticas_atualizadas, 'blue')}")
        print(f"❌ Erros: {colored(erros, 'red')}")
        print(f"📈 Taxa de sucesso: {colored(f'{((estatisticas_criadas + estatisticas_atualizadas) / len(motoristas_por_dia) * 100):.1f}%', 'green')}")
        print(f"{'='*70}\n")

###-----------------------------------------------------------------------------------------------------------------#####
# INVESTIGAÇÃO #
        #######################################################################################
    def INVESTIGAÇÃO(self):

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
    def DEMOLICAO(self):
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




    # DEMOLIÇÃO #
    ###+---------------------------------------------------------------------------------------------+
    ############################################################################################
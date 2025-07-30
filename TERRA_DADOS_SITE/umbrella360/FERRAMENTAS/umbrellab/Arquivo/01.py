


import requests
import json
import ast
import numpy as np
import time
from datetime import datetime, timedelta
from base import wialon_login, wialon_logout, search_units, json_to_dict, unidades_simples, BSCDR_Reports, buscadora_reports, execute_report, GET_REPORT_DATA
from CLTDR import CLDR_Reports, CLDR_Reports_02
from suporte import flatten_dict
import pandas as pd
import os
from termcolor import colored

wall = "###" * 30

WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc38CB9EA0831FCACD2BF547F1352F9AAB1DFD9D98A"
WIALON_BASE_URL = "https://hst-api.wialon.com"
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
BETA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito\BETA"




def Teste_Unidades_01(BETA, sid):

    nome = "Teste_Unidades_01"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    units = search_units(sid)
        #coloca as unidades em pandas dataframe
    units = [flatten_dict(unit) for unit in units]
    unidades = pd.DataFrame(units)
    unidades = unidades.rename(columns={
            'id': 'ID',
            'nm': 'Nome'
        })
    comm(unidades)
    unidades.to_excel(os.path.join(BETA, 'unidades.xlsx'), index=False)
    comm(f"Unidades salvas em {os.path.join(BETA, 'unidades.xlsx')}")

def Teste_Unidades_02(BETA, sid):

    nome = "Teste_Unidades_01"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    units = unidades_simples(sid)
        #coloca as unidades em pandas dataframe
    units = [flatten_dict(unit) for unit in units]
    unidades_s = pd.DataFrame(units)
    unidades_s = unidades_s.rename(columns={
            'id': 'ID',
            'nm': 'Nome'
        })
    comm(unidades_s)
    unidades_s.to_excel(os.path.join(BETA, 'unidades_s.xlsx'), index=False)
    comm(f"Unidades salvas em {os.path.join(BETA, 'unidades_s.xlsx')}")

def RELATORIOS_01(sid):
    nome = "Teste_RELATORIOS_01"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    reports = buscadora_reports(sid)
    for report in reports:
        print(f"ID: {report['id']}, Nome: {report['nm']}")
    relatorios = [flatten_dict(report) for report in reports]
        # Coloca os relatórios em pandas dataframe
    relatorios = pd.DataFrame(relatorios)
    relatorios = relatorios.rename(columns={
            'id': 'ID',
            'nm': 'Nome'
        })

    comm(relatorios)
    relatorios.to_excel(os.path.join(BETA, 'relatorios.xlsx'), index=False)
    comm(f"Relatórios salvos em {os.path.join(BETA, 'relatorios.xlsx')}")


###############################################################################################


def CONJUNTO_TESTE_01():
    """
    Função de teste para executar uma série de testes e relatórios.
    """
    nome = "CONJUNTO_TESTE_01"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    comm("Iniciando conjunto de testes...")
    
    # Teste de unidades
    Teste_Unidades_01(BETA, sid)
    Teste_Unidades_02(BETA, sid)
    
    # Teste de relatórios
    RELATORIOS_01(sid)
    
    print("Conjunto de testes concluído.")



############################################################################
def RELATORIOS_02(BETA, sid):
    nome = "Teste_RELATORIOS_02"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    reports = CLDR_Reports(sid)
        # Coloca os relatórios em pandas dataframe
    relatorios = pd.DataFrame(reports)

    relatorios.to_excel(os.path.join(BETA, 'relatorios.xlsx'), index=False)
    print(colored("Relatórios salvos em relatorios.xlsx", "green"))

def RELATORIOS_03(BETA, sid):
    nome = "Teste_RELATORIOS_03"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    reports = CLDR_Reports(sid)
        #salva os relatórios em um arquivo Excel
    reports = [flatten_dict(reports) for report in reports]
    relatorios = pd.DataFrame(report)

    relatorios.to_excel(os.path.join(BETA, 'RELATORIOS_03.xlsx'), index=False)
    print(colored("Relatórios salvos em RELATORIOS_03.xlsx", "green"))


def RELATORIOS_teste(BETA, sid):
    nome = "Teste_RELATORIOS_04"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    relatorio = execute_report(session_id=sid, resource_id , template_id, unit_id )
    comm(relatorio)
    dados = GET_REPORT_DATA(sid)
    comm(dados)



    #relatorios.to_excel(os.path.join(BETA, 'RELATORIOS_04.xlsx'), index=False)
    #print(colored("Relatórios salvos em RELATORIOS_04.xlsx", "green"))


if __name__ == "__main__":
    # Exemplo de uso
    sid = wialon_login(WIALON_TOKEN)
    if sid:
        # Aqui você pode chamar outras funções, como executar relatórios ou buscar dados
        # Por exemplo:
        #CONJUNTO_TESTE_01()


        RELATORIOS_teste(BETA, sid)


        

        # Para executar um relatório, você pode usar a função execute_report
        # report_data = execute_report(session_id, RESOURCE_ID, REPORT_TEMPLATE_ID, UNIT_ID, start_time, end_time)
        # print(report_data)
        
        wialon_logout(sid)
    else:
        print(colored("Falha no login.", "red"))
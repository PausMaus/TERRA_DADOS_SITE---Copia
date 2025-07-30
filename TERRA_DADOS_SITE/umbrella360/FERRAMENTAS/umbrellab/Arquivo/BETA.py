import requests
import json
import ast
import numpy as np
import time
from datetime import datetime, timedelta
from base import wialon_login, wialon_logout, search_units, json_to_dict, unidades_simples, BSCDR_Reports, buscadora_reports, execute_report, GET_REPORT_DATA, parsing, clean_up_result
from CLTDR import CLDR_Reports, CLDR_Reports_02
from suporte import flatten_dict
import pandas as pd
import os
from termcolor import colored

wall = "###" * 30

WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc38CB9EA0831FCACD2BF547F1352F9AAB1DFD9D98A"
WIALON_BASE_URL = "https://hst-api.wialon.com"
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
BETA = rf"D:\LABORATORIUM\umbreLAB\BETA"




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



def extract_report_headers(data):
    """
    Extrai a lista de headers (nomes das colunas) do resultado de relatório Wialon.
    Retorna uma lista de strings ou uma lista vazia se não encontrado.
    """
    try:
        tables = data.get('reportResult', {}).get('tables', [])
        if tables and isinstance(tables, list):
            header = tables[0].get('header', [])
            if isinstance(header, list):
                return header
    except Exception as e:
        print(f"Erro ao extrair headers: {e}")
    return []


def RELATORIOS_teste(BETA, sid):
    nome = "Teste_RELATORIOS_04"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    
    relatorio = execute_report(sid)
    comm(relatorio)
    print(type(relatorio))
    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")
    # Verifica se os headers foram extraídos corretamente
    if headers:
        comm(f"Headers extraídos: {headers}")
    else:
        comm("Nenhum header encontrado no relatório.")

    # Obtenha os dados do relatório
    dados = GET_REPORT_DATA(sid)
    comm(dados)
    print(type(dados))

    # Construa o DataFrame usando os headers como colunas
    rows = []
    for row in dados:
        if 'c' in row:
            flat_row = []
            for cell in row['c']:
                if isinstance(cell, dict):
                    flat_row.append(json.dumps(cell, ensure_ascii=False))
                else:
                    flat_row.append(cell)
            rows.append(flat_row)
    df = pd.DataFrame(rows, columns=headers)
    comm(df)

    # Salva os relatórios em um arquivo Excel
    df.to_excel(os.path.join(BETA, 'RELATORIOS_05.xlsx'), index=False)
    comm(f"Relatórios salvos em {os.path.join(BETA, 'RELATORIOS_05.xlsx')}")



    #relatorios.to_excel(os.path.join(BETA, 'RELATORIOS_04.xlsx'), index=False)
    #print(colored("Relatórios salvos em RELATORIOS_04.xlsx", "green"))




def RELATORIOS_teste_02(BETA, sid):
    """
    Executa o relatório 18 para todas as unidades, concatena os resultados em um DataFrame,
    salva os headers em 'headers_18.xlsx' e o relatório completo em 'Relatorio_18.xlsx'.
    """
    nome = "RELATORIOS_teste_02"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    # 1. Cria DataFrame vazio
    RELATORIO = pd.DataFrame()

    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    comm(f"Unidades encontradas: {len(unidades)}")

    # 3. Executa relatório 18 para a primeira unidade para extrair headers
    if not unidades:
        comm("Nenhuma unidade encontrada.")
        return
    unidade_exemplo = unidades[0]
    unit_id = unidade_exemplo.get('id')
    report_result = execute_report(sid, resource_id=401756219, template_id=18, unit_id=unit_id)
    headers = extract_report_headers(report_result)
    comm(f"Headers extraídos: {headers}")
    if not headers:
        comm("Não foi possível extrair headers do relatório.")
        return
    # Salva headers
    pd.DataFrame([headers]).to_excel(os.path.join(BETA, 'headers_18.xlsx'), index=False, header=False)

    # 4. Para cada unidade, executa o relatório, extrai dados e concatena
    all_rows = []
    for unidade in unidades:
        unit_id = unidade.get('id')
        comm(f"Executando relatório para unidade: {unidade.get('nm', unit_id)} (ID: {unit_id})")
        report_result = execute_report(sid, resource_id=401756219, template_id=18, unit_id=unit_id)
        dados = GET_REPORT_DATA(sid, table_index=0, index_from=0, index_to=0)
        rows = dados.get('rows', []) if isinstance(dados, dict) else []
        # Limpa resultado do relatório
        clean_up_result(sid)
        # Constrói DataFrame parcial
        if rows:
            df_parcial = pd.DataFrame([[cell if not isinstance(cell, dict) else json.dumps(cell, ensure_ascii=False) for cell in row.get('c', [])] for row in rows], columns=headers)
            # Adiciona coluna de unidade
            df_parcial['Unidade'] = unidade.get('nm', unit_id)
            all_rows.append(df_parcial)
        else:
            comm(f"Sem dados para unidade {unidade.get('nm', unit_id)}")

    # 5. Concatena todos os DataFrames
    if all_rows:
        RELATORIO = pd.concat(all_rows, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        RELATORIO.to_excel(os.path.join(BETA, 'Relatorio_18.xlsx'), index=False)
        comm(f"Relatório salvo em {os.path.join(BETA, 'Relatorio_18.xlsx')}")
    else:
        comm("Nenhum dado de relatório foi gerado.")


def MAIN():
    # Exemplo de uso
    sid = wialon_login(WIALON_TOKEN)
    if sid:
        # Aqui você pode chamar outras funções, como executar relatórios ou buscar dados
        # Por exemplo:
        #CONJUNTO_TESTE_01()


        #RELATORIOS_teste(BETA, sid)
        RELATORIOS_teste_02(BETA, sid)

        

        # Para executar um relatório, você pode usar a função execute_report
        # report_data = execute_report(session_id, RESOURCE_ID, REPORT_TEMPLATE_ID, UNIT_ID, start_time, end_time)
        # print(report_data)
        
        wialon_logout(sid)
    else:
        print(colored("Falha no login.", "red"))
import requests
import json
import ast
import numpy as np
import time
from datetime import datetime, timedelta
from base import WIALON_TOKEN, wialon_login, wialon_logout, search_units, unidades_simples,  buscadora_reports, execute_report, GET_REPORT_DATA, clean_up_result
from CLTDR import CLDR_Reports, CLDR_Reports_02
import pandas as pd
import os
from termcolor import colored
import tqdm
from tqdm import tqdm

wall = "###" * 30

WIALON_BASE_URL = "https://hst-api.wialon.com"
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
BETA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\umbreLAB\V7\deposito"




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



####################--------- DEMOLIÇÃO----------################################
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
    ####################--------- DEMOLIÇÃO----------################################


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

    
    relatorio = execute_report(sid, resource_id=401756219, template_id=59, unit_id=3849196688227)
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
    #df.to_excel(os.path.join(BETA, 'RELATORIOS_05.xlsx'), index=False)
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
    report_result = execute_report(sid, resource_id=401756219, template_id=18, unit_id=401788719)
    headers = extract_report_headers(report_result)
    comm(f"Headers extraídos: {headers}")
    if not headers:
        comm("Não foi possível extrair headers do relatório.")
        return
    # Salva headers
    pd.DataFrame([headers]).to_excel(os.path.join(BETA, 'headers_18.xlsx'), index=False, header=False)

    # 4. Para cada unidade, executa o relatório, extrai dados e concatena
    all_rows = []
    unidades_selecionadas = unidades[:3]
    for unidade in unidades_selecionadas:
        # Limpa resultado do relatório
        clean_up_result(sid)
        unit_id = unidade.get('id')
        comm(f"Executando relatório para unidade: {unidade.get('nm', unit_id)} (ID: {unit_id})")
        report_result = execute_report(sid, resource_id=401756219, template_id=18, unit_id=unit_id)
        dados = GET_REPORT_DATA(sid, table_index=0, index_from=0, index_to=0)
        rows = dados.get('rows', []) if isinstance(dados, dict) else []

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


def RELATORIOS_teste_03(BETA, sid):
    """
    Executa o relatório 18 para todas as unidades, concatena os resultados em um DataFrame,
    salva os headers em 'headers_18.xlsx' e o relatório completo em 'Relatorio_18.xlsx'.
    """
    nome = "RELATORIOS_teste_03"
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
    # 3. Executa relatório 18 para a unidade teste para extrair headers

    report_result = execute_report(sid, resource_id=401756219, template_id=18, unit_id=401788719)
    headers = extract_report_headers(report_result)
    comm(f"Headers extraídos: {headers}")
    if not headers:
        comm("Não foi possível extrair headers do relatório.")
        return
    # Salva headers
    pd.DataFrame([headers]).to_excel(os.path.join(BETA, 'cabecalhos_18.xlsx'), index=False, header=False)

    # adiciona o cabeçalho ao DataFrame
    RELATORIO = pd.DataFrame(columns=headers)
    comm(RELATORIO)


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



def RELATORIOS_teste_04(BETA, sid):
    nome = "RELATORIOS_teste_04"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    ################################################
    # 1. Cria DataFrame vazio
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    comm(f"Unidades encontradas: {len(unidades)}")


    # 3. Executa relatório 18 para a unidade teste para extrair headers
    relatorio = execute_report(sid, 401756219 , 59, 401761212)
    comm(relatorio)
    print(type(relatorio))


    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")

    # testa a extração de relatorios em pequena escala
    unidades_selecionadas = 401790521, 401756228, 401756229, 401756256, 401761197
    # Obtenha os dados do relatório
    for unidade in unidades_selecionadas:
        # Limpa resultado do relatório
        clean_up_result(sid)
        comm(f"Executando relatório para unidade: {unidade}")
        relatorio = execute_report(sid, resource_id=401756219, template_id=59, unit_id=unidade)
        comm(relatorio)
        print(type(relatorio))
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
    # 4. Concatena todos os DataFrames
    if not df.empty:
        RELATORIO = pd.concat([RELATORIO, df], ignore_index=True)
        comm(RELATORIO)
    else:
        comm("Nenhum dado de relatório foi gerado.")

    # Salva os relatórios em um arquivo Excel
    df.to_excel(os.path.join(BETA, 'RELATORIOS_06.xlsx'), index=False)
    comm(f"Relatórios salvos em {os.path.join(BETA, 'RELATORIOS_06.xlsx')}")





def RELATORIOS_teste_05(BETA, sid):
    nome = "RELATORIOS_teste_05"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    # 1. Cria DataFrame vazio para acumular todos os dados
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    ids = [unidade['id'] for unidade in unidades]
    comm(f"IDs das unidades encontradas: {ids}")
    comm(f"Unidades encontradas: {len(unidades)}")

    # 3. Executa relatório 18 para a unidade teste para extrair headers
    relatorio = execute_report(sid)
    comm(relatorio)
    print(type(relatorio))


    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")

    # 4. Seleciona as unidades para teste
    unidades_selecionadas = [401790521, 401756228, 401756229, 401756256, 401761197]
    all_dfs = []

    for unidade_id in unidades_selecionadas:
        clean_up_result(sid)
        comm(f"Executando relatório para unidade: {unidade_id}")
        relatorio = execute_report(sid, resource_id=401756219, template_id=18, unit_id=unidade_id)
        dados = GET_REPORT_DATA(sid)
        comm(f"Dados brutos: {dados}")

        # Construa o DataFrame usando os headers como colunas
        rows = []
        if isinstance(dados, list):
            for row in dados:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        elif isinstance(dados, dict) and 'rows' in dados:
            for row in dados['rows']:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        df = pd.DataFrame(rows, columns=headers)
        if not df.empty:
            df['Unidade'] = unidade_id
            all_dfs.append(df)
            comm(df)
        else:
            comm(f"Nenhum dado encontrado para unidade {unidade_id}")

    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        RELATORIO.to_excel(os.path.join(BETA, 'RELATORIOS_07.xlsx'), index=False)
        comm(f"Relatórios salvos em {os.path.join(BETA, 'RELATORIOS_07.xlsx')}")
    else:
        comm("Nenhum dado de relatório foi gerado.")


def RELATORIOS_teste_06(BETA, sid):
    nome = "RELATORIOS_teste_06"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    # 1. Cria DataFrame vazio para acumular todos os dados
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    ids = [unidade['id'] for unidade in unidades]
    comm(f"IDs das unidades encontradas: {ids}")
    comm(f"Unidades encontradas: {len(unidades)}")

    # 3. Executa relatório 18 para a unidade teste para extrair headers
    relatorio = execute_report(sid, resource_id=401756219, template_id=59, unit_id=3849196688227)
    comm(relatorio)
    print(type(relatorio))


    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")

    # 4. Seleciona as unidades para teste
    unidades_selecionadas = ids[:10]  # Seleciona as primeiras 5 unidades para teste
    comm(f"Unidades selecionadas para teste: {unidades_selecionadas}")
    all_dfs = []

    for unidade_id in tqdm(unidades_selecionadas, desc="Processando unidades"):
        clean_up_result(sid)
        comm(f"Executando relatório para unidade: {unidade_id}")
        relatorio = execute_report(sid, resource_id=401756219, template_id=59, unit_id=unidade_id)
        dados = GET_REPORT_DATA(sid)
        comm(f"Dados brutos: {dados}")

        # Construa o DataFrame usando os headers como colunas
        rows = []
        if isinstance(dados, list):
            for row in dados:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        elif isinstance(dados, dict) and 'rows' in dados:
            for row in dados['rows']:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        df = pd.DataFrame(rows, columns=headers)
        if not df.empty:
            df['Unidade'] = unidade_id
            all_dfs.append(df)
            comm(df)
        else:
            comm(f"Nenhum dado encontrado para unidade {unidade_id}")

    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        #RELATORIO.to_excel(os.path.join(BETA, 'RELATORIOS_08.xlsx'), index=False)
        comm(f"Relatórios salvos em {os.path.join(BETA, 'RELATORIOS_08.xlsx')}")
    else:
        comm("Nenhum dado de relatório foi gerado.")





def RELATORIOS_teste_U(BETA, sid):
    nome = "RELATORIOS_teste_U"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    # 1. Cria DataFrame vazio para acumular todos os dados
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    ids = [unidade['id'] for unidade in unidades]
    comm(f"IDs das unidades encontradas: {ids}")
    comm(f"Unidades encontradas: {len(unidades)}")

    # 3. Executa relatório 18 para a unidade teste para extrair headers
    relatorio = execute_report(sid)
    comm(relatorio)
    print(type(relatorio))


    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")

    # 4. Seleciona as unidades para teste
    unidades_selecionadas = ids  
    templates = (18,19,36)
    all_dfs = []
    for unidade_id in tqdm(unidades_selecionadas, desc="Processando unidades"):
        clean_up_result(sid)
        relatorio = execute_report(sid, resource_id=401756219, template_id=18, unit_id=unidade_id)
        dados = GET_REPORT_DATA(sid)

        # Construa o DataFrame usando os headers como colunas
        rows = []
        if isinstance(dados, list):
            for row in dados:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        elif isinstance(dados, dict) and 'rows' in dados:
            for row in dados['rows']:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        df = pd.DataFrame(rows, columns=headers)
        if not df.empty:
            df['Unidade'] = unidade_id
            all_dfs.append(df)


    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        RELATORIO.to_excel(os.path.join(BETA, 'RELATORIOS_U.xlsx'), index=False)
        comm(f"Relatórios salvos em {os.path.join(BETA, 'RELATORIOS_U.xlsx')}")




def RLTR(BETA, sid, template_id):
    nome = "RLTR"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    # 1. Cria DataFrame vazio para acumular todos os dados
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    ids = [unidade['id'] for unidade in unidades]
    comm(f"IDs das unidades encontradas: {ids}")
    comm(f"Unidades encontradas: {len(unidades)}")

    # 3. Executa relatório 18 para a unidade teste para extrair headers
    relatorio = execute_report(sid, 401756219 , template_id, 401761212)
    comm(relatorio)
    print(type(relatorio))


    # Extrai os headers do relatório
    headers = extract_report_headers(relatorio)
    comm(f"Headers do relatório: {headers}")

    # 4. Seleciona as unidades para teste
    unidades_selecionadas = ids  
    templates = (18,19,36)

    all_dfs = []
    for unidade_id in tqdm(unidades_selecionadas, desc="Processando unidades"):
        clean_up_result(sid)
        relatorio = execute_report(sid, resource_id=401756219, template_id=template_id, unit_id=unidade_id)
        dados = GET_REPORT_DATA(sid)

        # Construa o DataFrame usando os headers como colunas
        rows = []
        if isinstance(dados, list):
            for row in dados:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        elif isinstance(dados, dict) and 'rows' in dados:
            for row in dados['rows']:
                if 'c' in row:
                    flat_row = []
                    for cell in row['c']:
                        if isinstance(cell, dict):
                            flat_row.append(json.dumps(cell, ensure_ascii=False))
                        else:
                            flat_row.append(cell)
                    rows.append(flat_row)
        df = pd.DataFrame(rows, columns=headers)
        if not df.empty:
            df['Unidade'] = unidade_id
            all_dfs.append(df)


    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        RELATORIO.to_excel(os.path.join(BETA, f'RLTR_{template_id}.xlsx'), index=False)
        comm(f"Relatório salvo em {os.path.join(BETA, f'RLTR_{template_id}.xlsx')}")

#************************************************************************************************
def GAMMA():
    # Exemplo de uso
    sid = wialon_login(WIALON_TOKEN)
    if sid:
        # Aqui você pode chamar outras funções, como executar relatórios ou buscar dados
        # Por exemplo:
        #CONJUNTO_TESTE_01(sid)


        RELATORIOS_teste(BETA, sid)
        #RELATORIOS_teste_02(BETA, sid)
        #RELATORIOS_teste_03(BETA, sid)
        #RELATORIOS_teste_04(BETA, sid)
        #RELATORIOS_teste_05(BETA, sid)
        #RELATORIOS_teste_06(BETA, sid)
        #RELATORIOS_teste_U(BETA, sid)
        
        #RLTR(BETA, sid, template_id=18)
        #RLTR(BETA, sid, template_id=19)
        #RLTR(BETA, sid, template_id=59)

        

        # Para executar um relatório, você pode usar a função execute_report
        # report_data = execute_report(session_id, RESOURCE_ID, REPORT_TEMPLATE_ID, UNIT_ID, start_time, end_time)
        # print(report_data)
        
        wialon_logout(sid)
    else:
        print(colored("Falha no login.", "red"))


if __name__ == "__main__":
    GAMMA()
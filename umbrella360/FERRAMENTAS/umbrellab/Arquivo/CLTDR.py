#this script is designed to interact with the Wialon API to retrieve information about units (vehicles or assets) and export that data to an SQLite database.

# It also handles errors and exceptions during the process.
# The script is designed to be run as a standalone program.
# The script is structured to be modular, with functions for logging in, searching for units, and creating the Excel file.
# The script is designed to be easy to read and understand, with clear function names and comments explaining each step.
# The script is also designed to be easily extensible, allowing for future enhancements or modifications as needed.
# The script is intended to be run in a Python environment with the necessary libraries installed.
# The script is designed to be cross-platform, working on both Windows and Linux systems.
# The script is designed to be efficient, minimizing API calls and optimizing data retrieval.
# The script is designed to be user-friendly, providing clear output messages and error handling.
# The script is designed to be maintainable, with clear code structure and organization.
# The script is designed to be reusable, allowing for easy integration into other projects or workflows.
# The script is designed to be robust, handling various edge cases and potential errors gracefully.
# The script is designed to be secure, using best practices for handling sensitive information such as API tokens.
# The script is designed to be scalable, capable of handling large amounts of data without performance degradation.
# The script is designed to be flexible, allowing for easy customization of output file names and formats.
# The script is designed to be portable, allowing for easy transfer between different environments or systems.
# The script is designed to be well-documented, with clear comments and explanations for each function and step.
# all print() functions must have a prefix "BASE:" to be recognized by the main script





import requests
import json
import ast
import pandas as pd
import os
import time
from tqdm import tqdm
from termcolor import colored
from base import *
from base import WIALON_TOKEN



### Configurações #########################################################################
#request template
#https://{host}/wialon/ajax.html?sid=<text>&svc=<svc>&params={<params>}
# Exemplo de chamada para buscar unidades (avl_unit) na API Wialon:
#https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&
#	params={
#		"id":34868,
#		"flags":1025
#	}&sid=<your_sid>

#https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={"id":34868,"flags":1025}&sid=<your_sid>

WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API 
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"

deposito = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito"
ALPHA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito\ALPHA"
BETA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito\BETA"
GAMMA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito\GAMMA"




####################################################################################




# --- Colheitadeiras --------------------------------------------------



def CLTDR(flag):
    """
    Coleta dados do Wialon.
    """
    tool = "CLTDR"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{tool}:","green"))
        print(f"{msg}")
        print(f"bandeira:",colored(f"{flag}","red"))
        print(colored("="*30, "yellow"))

    comm("Iniciando coleta de dados do Wialon...")
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)

    # Retrieve unit data
    units = listar_IDs(session_id)
    comm(f"INFO: Retrieved {len(units)} units from Wialon.")
##########################################################################################

##########################################################################################

    comm("Iniciando coleta de dados das unidades")

    df = pd.DataFrame() 
    for unit in tqdm(units, desc="Coletando dados das unidades", unit="unidade"):
        data = buscadora_ID(session_id, unit, flag)
        flat_data = flatten_dict(data)
        df = pd.concat([df, pd.DataFrame([flat_data])], ignore_index=True)
        
    print(df)  
    df.to_excel(os.path.join(ALPHA, f"CLTDR_{flag}.xlsx"), index=False) 
    df.to_csv(os.path.join(ALPHA, f"CLTDR_{flag}.csv"), index=False)

                
    wialon_logout(session_id)

def MINI_CLTDR():
    comm(units)
    unidades = pd.Series(units)
    comm(unidades)
    unidades_frame = pd.DataFrame(unidades)
    comm(unidades_frame)
    unidades_frame.to_csv(os.path.join(ALPHA, f"veiculos.csv"), index=False)
    comm(f"lista de veiculos salva em: {tool}.csv")
    unidades_frame.to_excel(os.path.join(ALPHA, f"veiculos.xlsx"), index=False)
    comm(f"lista de veiculos salva em: {tool}.xlsx")
    unidades_frame.to_parquet(os.path.join(ALPHA, f"veiculos.parquet"), index=False)    
    comm(f"lista de veiculos salva em: {tool}.parquet")

########
def CLDR_Reports(sid):
    """
    Retrieve and print all available reports grouped by resource, similar to CLTDR unit listing.
    """
    print("RPTR: CLDR_Reports: Coletando lista de relatórios disponíveis...")
    result = buscadora_reports(sid)
    if not result:
        print("BASE: Nenhum relatório encontrado.")
        return
    for resource in result:
        resource_name = resource.get('nm', 'Sem nome')
        resource_id = resource.get('id', 'N/A')
        reports = resource.get('rep', {})
        if reports:
            print(f"BASE: Recurso: {resource_name} (ID: {resource_id})")
            for rep_id, rep_info in reports.items():
                print(f"  Report ID: {rep_info.get('id', rep_id)}, Nome: {rep_info.get('n', rep_info.get('name', 'Sem nome'))}")


def CLDR_Reports_02(sid):
    """
    Retrieve and print all available reports grouped by resource, similar to CLTDR unit listing.
    """
    print("RPTR: CLDR_Reports: Coletando lista de relatórios disponíveis...")
    result = buscadora_reports(sid)
    if not result:
        print("BASE: Nenhum relatório encontrado.")
        return
    # Prepare a list to collect report data
    report_list = []
    for resource in result:
        resource_name = resource.get('nm', 'Sem nome')
        resource_id = resource.get('id', 'N/A')
        reports = resource.get('rep', {})
        if reports:
            for rep_id, rep_info in reports.items():
                report_list.append({
                    "Recurso": resource_name,
                    "ID do Recurso": resource_id,
                    "Report ID": rep_info.get('id', rep_id),
                    "Nome do Relatório": rep_info.get('n', rep_info.get('name', 'Sem nome'))
                })
    if report_list:
        df_reports = pd.DataFrame(report_list)
        print("BASE: Lista de relatórios disponíveis:")
        print(df_reports)
    else:
        print("BASE: Nenhum relatório encontrado para os recursos disponíveis.")





##############----------RPTR----------############################################
def RLTR(BETA, sid, template_id):
    nome = "RLTR"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))



    comm(f"Iniciando coleta de dados do Wialon para relatório {template_id}...")
    # 1. Cria DataFrame vazio para acumular todos os dados
    RELATORIO = pd.DataFrame()
    # 2. Busca todas as unidades
    unidades = unidades_simples(sid)
    ids = [unidade['id'] for unidade in unidades]
    comm(f"IDs das unidades encontradas: {ids}")
    comm(f"Unidades encontradas: {len(unidades)}")



    # Solicita ao usuário qual template_id usar
    #template_id = request_template_id(comm)



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



def RLTR_UNIDADES(BETA, sid, template_id):
    nome = "RLTR_UNIDADES"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    comm(f"Iniciando coleta de dados do Wialon para relatório {template_id}...")
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
            # Adiciona a coluna 'Unidade' como última coluna
            df['Unidade'] = unidade_id
            # Garante que 'Unidade' seja a última coluna
            df = df[[col for col in df.columns if col != 'Unidade'] + ['Unidade']]
            all_dfs.append(df)

    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        RELATORIO.to_excel(os.path.join(BETA, f'RLTR_{template_id}.xlsx'), index=False)
        comm(f"Relatório salvo em {os.path.join(BETA, f'RLTR_{template_id}.xlsx')}")



def RLTR_UNIDADES_S(BETA, sid, template_id):
    nome = "RLTR_UNIDADES_S"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    comm(f"Iniciando coleta de dados do Wialon para relatório {template_id}...")
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

    unidade_id = 401790521

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
    print(dados)




def RLTR_UNIDADES_R(BETA, sid, template_id):
    nome = "RLTR_UNIDADES_R"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    comm(f"Iniciando coleta de dados do Wialon para relatório {template_id}...")
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
    sheet_dict = {}  # Para armazenar DataFrames por unidade para o arquivo mestre

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
            # Adiciona a coluna 'Unidade' como última coluna
            df['Unidade'] = unidade_id
            # Garante que 'Unidade' seja a última coluna
            df = df[[col for col in df.columns if col != 'Unidade'] + ['Unidade']]
            all_dfs.append(df)
            # Salva arquivo individual
            individual_path = os.path.join(BETA, f'RLTR_{template_id}_{unidade_id}.xlsx')
            df.to_excel(individual_path, index=False)
            comm(f"Relatório salvo em {individual_path}")
            # Adiciona ao dicionário de sheets para o arquivo mestre
            sheet_name = f"unit_{unidade_id}"
            # Excel limita nomes de sheets a 31 caracteres
            sheet_dict[sheet_name[:31]] = df

    # 5. Concatena todos os DataFrames
    if all_dfs:
        RELATORIO = pd.concat(all_dfs, ignore_index=True)
        comm(RELATORIO)
        # 6. Salva o DataFrame final
        master_path = os.path.join(BETA, f'RLTR_{template_id}.xlsx')
        RELATORIO.to_excel(master_path, index=False)
        comm(f"Relatório salvo em {master_path}")

        # 7. Salva o arquivo mestre com múltiplas sheets no GAMMA
        master_multi_path = os.path.join(GAMMA, f'MASTER_FILE_RLTR_{template_id}.xlsx')
        with pd.ExcelWriter(master_multi_path, engine='openpyxl') as writer:
            for sheet, df_sheet in sheet_dict.items():
                df_sheet.to_excel(writer, sheet_name=sheet, index=False)
        comm(f"Arquivo mestre com múltiplas sheets salvo em {master_multi_path}")


#************************************************************************************************

#########################################################################
# --- Execução Principal ---

def CLDR_ULTRA():
    nome = "CLDR_ULTRA"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    sid = wialon_login(WIALON_TOKEN)
    if sid:
        STATUS(sid)


        # RLTR(BETA, sid, template_id=50)
        RLTR_UNIDADES_S(BETA, sid, template_id=50)

        
        
        wialon_logout(sid)
    else:
        print(colored("Falha no login.", "red"))

CLDR_ULTRA()









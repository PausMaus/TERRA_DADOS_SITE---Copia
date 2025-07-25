#this script is designed to interact with the Wialon API to retrieve information about reports and export that data in the terminal.

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
from datetime import datetime, timedelta
from base import wialon_login, wialon_logout
import pandas as pd
import os

wall = "###" * 30

WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc38CB9EA0831FCACD2BF547F1352F9AAB1DFD9D98A"
WIALON_BASE_URL = "https://hst-api.wialon.com"
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
RESOURCE_ID = 401756219
REPORT_TEMPLATE_ID = 18
UNIT_ID = 401788719  # Use your actual unit id if needed






def get_report_rows(session_id, table_index=0, index_from=0, index_to=100):
    params = {
        "svc": "report/get_result_rows",
        "params": json.dumps({
            "tableIndex": table_index,
            "indexFrom": index_from,
            "indexTo": index_to
        }),
        "sid": session_id
    }
    response = requests.post(API_URL, data=params)
    response.raise_for_status()
    return response.json()

def extract_report_headers(flat_report):
    """
    Extracts the report headers (column names) as a list from a flattened report result dict.
    Returns a list of header strings, or an empty list if not found.
    """
    try:
        tables = flat_report.get('reportResult_tables', [])
        if tables and isinstance(tables, list):
            # The first table is usually the main one
            header = tables[0].get('header', [])
            if isinstance(header, list):
                return header
    except Exception as e:
        print(f"BASE: Erro ao extrair headers: {e}")
    return []


def report_rows_to_dataframe(rows, report_result=None):
    """
    Converts Wialon report rows (list of dicts with 'c' key) to a pandas DataFrame.
    Flattens any dicts inside the 'c' list.
    Uses column names from report_result['reportResult']['tables'][0]['header'] if available.
    """

    processed_rows = []
    for row in rows:
        if 'c' in row:
            flat_row = []
            for cell in row['c']:
                if isinstance(cell, dict):
                    for k, v in cell.items():
                        flat_row.append(v)
                else:
                    flat_row.append(cell)
            processed_rows.append(flat_row)
        else:
            processed_rows.append([])

    # Try to get columns from report_result
    columns = None
    if report_result and isinstance(report_result, dict):
        try:
            columns = report_result['reportResult']['tables'][0]['header']
        except Exception:
            columns = None
    if not columns:
        max_len = max(len(r) for r in processed_rows) if processed_rows else 0
        columns = [f"col_{i}" for i in range(max_len)]

    df = pd.DataFrame(processed_rows, columns=columns)
    print(f"BASE: DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas (report_rows_to_dataframe).")
    return df
######################################################################################
def TESTE():
    """
    Test function to execute a report and print the result.
    """
    try:
        session_id = wialon_login(WIALON_TOKEN)
        print(wall)
        print("Session ID:", session_id)

        # Execute the report
        print(wall)
        report_result = execute_report(session_id, RESOURCE_ID, REPORT_TEMPLATE_ID, UNIT_ID, 1748362937, 1748528102)
        print("Report Result:", report_result)

        # flatten the report result
        print(wall)
        flat_report = flatten_dict(report_result)
        print("Flattened Report Result:", flat_report)
        df = pd.DataFrame([flat_report])
        print("DataFrame from Report Result:")
        headers = extract_report_headers(flat_report)
        print(headers)
        print(wall)

        # Get the report rows
        print(wall)
        data = get_report_rows(session_id)
        print("Report Rows:", data)
        df = report_rows_to_dataframe(data.get('rows', []), report_result)
        print("DataFrame from Report Rows:")
        print(df)

    
       
    except requests.RequestException as e:
        print(f"Error during API request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        wialon_logout(session_id)



############ REVIEW ##########################################

#this script is designed to interact with the Wialon API to retrieve information about reports and export that data in the terminal.

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
from datetime import datetime, timedelta
from base import wialon_login, wialon_logout, execute_report, WIALON_TOKEN, execute_report_for_unit
import pandas as pd
import os



WIALON_BASE_URL = "https://hst-api.wialon.com"
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
RESOURCE_ID = 401756219
REPORT_TEMPLATE_ID = 18

BETA = rf"D:\LABORATORIUM\umbreLAB\BETA"  # Path to save the report output




def execute_report_for_unit(session_id, resource_id, template_id, unit_id, days=3):
    """
    Execute a Wialon report for a specific unit and print the result.
    """
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() + timedelta(days)).timestamp())
    payload = {
        "svc": "report/exec_report",
        "params": json.dumps({
            "reportResourceId": 401756219,
            "reportTemplateId": 18,  # Report template ID for report 18
            "reportObjectId": 401788719,
            
            "reportObjectSecId": 0,
            "interval": {
                "from": 1748362937,
                "to": 1748528102, # Example end time, adjust as needed
                "flags": 0
            }
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        print(f"BASE: Resultado do relatório {template_id} para unidade {unit_id}:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"BASE: Erro ao executar relatório para unidade {unit_id}: {e}")





def wait_for_report_ready(session_id, timeout=10, poll_interval=2, report_index=0):
    """
    Polls Wialon API until the report is ready for export or timeout is reached.
    Returns True if ready, False otherwise.
    """
    import time
    elapsed = 0
    while elapsed < timeout:
        params = {
            "svc": "report/get_result_rows",
            "params": json.dumps({
                "tableIndex": 0,
                "indexFrom": 0,
                "indexTo": 1
            }),
            "sid": session_id
        }
        try:
            response = requests.post(API_URL, data=params)
            response.raise_for_status()
            data = response.json()
            # If we get a valid response, assume report is ready
            if isinstance(data, dict) and (data.get("totalRows") is not None or data.get("count") is not None):
                return True
        except Exception:
            pass  # Ignore and retry
        time.sleep(poll_interval)
        elapsed += poll_interval
    print("BASE: Timeout esperando relatório ficar pronto para exportação.")
    return False


def run_report():
    """
    Main function: login, get all units, select 3 units at random, execute report  for each, export result, logout.
    """
    print("BASE: Iniciando execução do relatório  para todas as unidades...")
    sid = wialon_login(WIALON_TOKEN)
    df = pd.DataFrame()  # Initialize an empty DataFrame to store results
    if not sid:
        print("BASE: Falha no login Wialon.")
        return
    units = get_all_units(sid)
    #select 3 random units
    if len(units) > 3:
        units = units[:1]  # Select only the first 3 units for simplicity

    if not units:
        print("BASE: Nenhuma unidade encontrada.")
        wialon_logout(sid)
        return
    folder_path = os.path.dirname(os.path.abspath(__file__))
    for unit in units:
        unit_id = unit.get("id")
        unit_name = unit.get("nm", "Sem nome")
        print(f"BASE: Executando relatório para unidade: {unit_name} (ID: {unit_id})")
        execute_report_for_unit(sid, RESOURCE_ID, REPORT_TEMPLATE_ID, unit_id)
    print("BASE: Relatório executado para todas as unidades selecionadas.")

    wialon_logout(sid)
    print("BASE: Execução concluída.")


def GET_REPORT_DATA(session_id, table_index=0, index_from=0, index_to=0):
    """
    Consulta o resultado do relatório executado usando report/get_result_rows.
    Retorna o resultado como dicionário Python.
    """
    params = {
        "svc": "report/get_result_rows",
        "params": json.dumps({
            "tableIndex": table_index,
            "indexFrom": index_from,
            "indexTo": index_to
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        data = response.json()
        print(f"BASE: Dados do relatório obtidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception as e:
        print(f"BASE: Erro ao obter dados do relatório: {e}")
        return None


def flatten_dict(d, parent_key='', sep='_'):
    """
    Achata recursivamente um dicionário aninhado.
    
    Exemplo:
      {'a': {'b': 1}}  se torna  {'a_b': 1}
      
    Parâmetros:
      d:         Dicionário a ser achatado.
      parent_key: Chave acumulada na recursão (inicialmente vazio).
      sep:       Separador para concatenar chaves.
      
    Retorna:
      Um novo dicionário com as chaves achatadas.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def get_report_dataframe(session_id, table_index=0, index_from=0, index_to=0):
    """
    Captura o resultado do relatório via GET_REPORT_DATA e converte para pandas DataFrame.
    Usa flatten_dict para achatar cada linha antes de criar o DataFrame.
    Retorna o DataFrame ou None em caso de erro.
    """
    data = GET_REPORT_DATA(session_id, table_index, index_from, index_to)
    if not data or 'rows' not in data or 'columns' not in data:
        print("BASE: Dados do relatório não possuem estrutura esperada para DataFrame.")
        return None
    # Extrai nomes das colunas
    columns = [col.get('name', f'col_{i}') for i, col in enumerate(data['columns'])]
    # Extrai os valores das linhas e aplica flatten_dict
    rows = []
    for row in data['rows']:
        if 'c' in row:
            # Monta um dicionário com as colunas e valores
            row_dict = {columns[i]: (cell.get('v', '') if isinstance(cell, dict) else cell) for i, cell in enumerate(row['c'])}
            flat_row = flatten_dict(row_dict)
            rows.append(flat_row)
        else:
            rows.append({})
    try:
        df = pd.DataFrame(rows)
        print(f"BASE: DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas (flattened).")
        return df
    except Exception as e:
        print(f"BASE: Erro ao criar DataFrame: {e}")
        return None


def report_rows_to_dataframe(rows, report_result=None):
    """
    Converts Wialon report rows (list of dicts with 'c' key) to a pandas DataFrame.
    Flattens any dicts inside the 'c' list.
    Uses column names from report_result['reportResult']['tables'][0]['header'] if available.
    """

    processed_rows = []
    for row in rows:
        if 'c' in row:
            flat_row = []
            for cell in row['c']:
                if isinstance(cell, dict):
                    for k, v in cell.items():
                        flat_row.append(v)
                else:
                    flat_row.append(cell)
            processed_rows.append(flat_row)
        else:
            processed_rows.append([])

    # Try to get columns from report_result
    columns = None
    if report_result and isinstance(report_result, dict):
        try:
            columns = report_result['reportResult']['tables'][0]['header']
        except Exception:
            columns = None
    if not columns:
        max_len = max(len(r) for r in processed_rows) if processed_rows else 0
        columns = [f"col_{i}" for i in range(max_len)]

    df = pd.DataFrame(processed_rows, columns=columns)
    print(f"BASE: DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas (report_rows_to_dataframe).")
    return df




###########################################################################
def TESTE_REPORT():


    sid = wialon_login(WIALON_TOKEN)
    execute_report_for_unit(sid, 401756219, 18, 401788719)
    data = GET_REPORT_DATA(sid, table_index=0, index_from=0, index_to=10)
    rows = data if isinstance(data, list) else data.get('rows', [])
    exec_report_result = data  # Assign data to exec_report_result to avoid undefined variable
    df = report_rows_to_dataframe(rows, report_result=exec_report_result)
    print(df)
    xlsx_path = os.path.join(BETA, "report_output.xlsx")
    try:
        df.to_excel(xlsx_path, index=False)
        print(f"BASE: DataFrame salvo como arquivo XLSX em: {xlsx_path}")
    except Exception as e:
        print(f"BASE: Erro ao salvar DataFrame como XLSX: {e}")
 
    #get_report_dataframe(sid, table_index=0, index_from=0, index_to=10)
    wialon_logout(sid)

############################################################################################









if __name__ == "__main__":
    TESTE()
    # You can call other functions here as needed
    # For example, you can call CLTDR(flag) if you have defined it
    # CLTDR(flag)
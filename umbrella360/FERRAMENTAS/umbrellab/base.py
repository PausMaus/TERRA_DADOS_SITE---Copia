
import requests
import json
import ast
import pandas as pd
import numpy as np
import os
import time
from termcolor import colored
from typing import Optional



# Substitua pelo seu token real gerado no Wialon
WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc3E8CA7EF917DE471D3CADA932B0B93F1BD2B8D124"

# Verifique se esta é a URL correta para sua instância Wialon (Hosting ou Local)
WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API 
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"

deposito = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito"
ALPHA = os.path.join(os.path.dirname(__file__), "ALPHA")



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



###################################################################
# --- Função centralizada de log ---
def log_base(msg: str, prefix: str = "INFO") -> None:
    print(f"BASE: [{prefix}] {msg}")

def log_colored(msg: str, color: str = "yellow", prefix: str = "BASE") -> None:
    print(colored("="*30, color))
    print(colored(f"{prefix}:", color))
    print(f"{msg}")
    print(colored("="*30, color))





########################################################################################
# --- Funções para Interagir com a API Wialon ------------------------------------------


def wialon_login(token):
    """
    Realiza o login na API Wialon usando um token.

    Args:
        token (str): O token de autorização do Wialon.

    Returns:
        str: O Session ID (eid) se o login for bem-sucedido, None caso contrário.
    """
    log_colored("Iniciando login na API Wialon...", "blue", "LOGIN")
    login_params = {
        "token": token,
        "appName": "UMBRELLA360", # Nome opcional para identificar sua aplicação
        "operateAs": "", # Deixe em branco para logar como o usuário dono do token
        # "fl": 0 # Flags opcionais, veja documentação
    }
    params = {
        "svc": "token/login",
        "params": json.dumps(login_params) # Os parâmetros específicos do serviço devem ser um JSON stringificado
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)
        result = response.json()


        if "error" in result:
            log_colored(f"Erro de API no login: {result}")
            # Tenta obter o código de erro específico do Wialon, se disponível
            wialon_error_code = result.get("error")
            if wialon_error_code == 1:
                log_base("-> Causa provável: Token inválido ou expirado.")
            elif wialon_error_code == 4:
                log_base("-> Causa provável: Usuário bloqueado ou sem acesso.")
            # Adicione mais códigos de erro conforme a documentação:
            # https://sdk.wialon.com/wiki/en/kit/remoteapi/apiref/apierrors
            return None

        if "eid" in result:
            session_id = result["eid"]
            user_info = result.get("user", {})
            log_colored(f"Login bem-sucedido! Session ID (SID): {session_id}\nLogado como: {user_info.get('nm', 'Usuário Desconhecido')}", "green", "LOGIN")
            return session_id
        else:
            log_colored(f"Login falhou. Resposta inesperada: {result}", "red", "LOGIN")
            return None

    except requests.exceptions.RequestException as e:
        log_base(f"Erro de conexão/HTTP durante o login: {e}", "ERROR")
        return None
    except json.JSONDecodeError:
        log_base(f"Erro ao decodificar resposta JSON do login: {response.text}", "ERROR")
        return None

######################################################################################


# --- Logout da Sessão Wialon ---
def wialon_logout(session_id):
    """
    Realiza o logout da sessão Wialon.

    Args:
        session_id (str): O Session ID ativo.
    """

    tool = "Wialon Logout"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{tool}:","red"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    params = {
        "svc": "core/logout",
        "params": "{}", # Parâmetros vazios para logout
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        if result.get("error") == 0:
             comm("Logout bem-sucedido.")
        else:
             comm(f"Logout retornou status: {result}")

    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão/HTTP durante o logout: {e}")
        return False
    except json.JSONDecodeError:
        comm(f"Erro ao decodificar resposta JSON do logout: {response.text}")
        return False
    return True






###########################################################################################
#BUSCADORES DE INFORMACAO ---------------------------------------------------
# --- Busca por Unidades na API Wialon ---
# A função search_units busca por unidades (avl_unit) na API Wialon e retorna uma lista de dicionários com as informações das unidades encontradas.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações sobre unidades registradas na plataforma Wialon, como veículos ou ativos monitorados.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
def search_units(session_id):
    """
    Busca por itens do tipo 'avl_unit' (unidades) na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.

    Returns:
        list: Uma lista de dicionários representando as unidades encontradas, ou None em caso de erro.
    """
    ##################################################################
    nome = "Buscadora de Unidades"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))

    ##################################################################
    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": "*",         # Buscar todas as unidades (wildcard)
        "sortType": "sys_name",       # Ordenar pelo nome
        # "propType": "property",     # Opcional: tipo da propriedade
        # "or_logic": False           # Opcional: lógica OR para máscaras
    }
    flags = (
        1 |       # 1: Inclui informações básicas (ID, nome)
        8 |       # 8: Inclui propriedades personalizadas
        256 |     # 256: Inclui o ícone da unidade
        4096      # 4096: Inclui informações do último status (posição, etc.)
        # Adicione mais flags conforme necessário: https://sdk.wialon.com/wiki/en/kit/flags
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    comm("\nBuscando unidades...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            comm(f"Erro de API ao buscar unidades: {result}")
            return None

        if "items" in result:
            units = result["items"]
            comm(f"Encontradas {len(units)} unidades.")
            return units
        else:
            comm(f"Resposta inesperada ao buscar unidades: {result}")
            return None

    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão/HTTP ao buscar unidades: {e}")
        return None
    except json.JSONDecodeError:
        comm(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None

def unidades_simples(session_id):
    """
    Retrieve all available units (avl_unit) from Wialon.
    """
    nome = "Buscadora de Unidades Simples"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 1,
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        return result.get("items", [])
    except Exception as e:
        comm(f"Erro ao buscar unidades: {e}")
        return []

def buscadora_reports(session_id):
    """
    Busca por relatorios na API Wialon.
    
    Returns:
        list: Uma lista de dicionários representando os relatórios encontrados, ou None em caso de erro.
    """
    nome = "Buscadora de Relatorios 02"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name",

            },
            "force": 1,
            "flags": 8193,
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            comm(f"Erro de API ao buscar relatórios: {result}")
            return None

        if "items" in result:
            users = result["items"]
            comm(f"Encontrados {len(users)} usuários.")
            return users
        else:
            comm(f"Resposta inesperada ao buscar usuários: {result}")
            return None

    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão/HTTP ao buscar usuários: {e}")
        return None
    except json.JSONDecodeError:
        comm(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None


def execute_report(session_id, resource_id , template_id, unit_id ):
    """
    Executa um relatório na API Wialon usando report/exec_report.

    """
    nome = "execute_report"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    payload = {
        "svc": "report/exec_report",
        "params": json.dumps({
            "reportResourceId": resource_id,
            "reportTemplateId": template_id,
            "reportObjectId": unit_id,
            "reportObjectSecId": 0,
            "interval": {
                "from": 1752441447,
                "to": 1752527847,
                "flags": 0
            }
        }),
        "sid": session_id
    }
    response = requests.post(API_URL, data=payload)
    response.raise_for_status()
    data = response.json()
    comm(f"Dados do relatório executado: {json.dumps(data, indent=2, ensure_ascii=False)}")
    if "error" in data:
        comm(f"Erro ao executar relatório: {data}")
        return None
    if "reportResult" in data:
        comm(f"Relatório executado com sucesso: {data['reportResult']}")
        return data['reportResult']

    return data


def execute_report_for_unit(session_id, resource_id, template_id, unit_id, days=3):
    """
    Execute a Wialon report for a specific unit and print the result.
    """

    payload = {
        "svc": "report/exec_report",
        "params": json.dumps({
            "reportResourceId": 401756219,
            "reportTemplateId": 18,  # Report template ID for report 18
            "reportObjectId": 401788719,
            
            "reportObjectSecId": 0,
            "interval": {
                "from": 0,
                "to": 1, # Example end time, adjust as needed
                "flags": 8
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



def GET_REPORT_DATA(session_id, table_index=0, index_from=0, index_to=0, verbose=False):
    """
    Consulta o resultado do relatório executado usando report/get_result_rows.

    Args:
        session_id (str): Session ID válido da Wialon API.
        table_index (int): Índice da tabela do relatório (default: 0).
        index_from (int): Índice inicial das linhas a serem retornadas (default: 0).
        index_to (int): Índice final das linhas a serem retornadas (default: 0).
        verbose (bool): Se True, imprime os dados do relatório.

    Returns:
        dict: Um dicionário Python contendo os dados do relatório, por exemplo:
            {
                "rows": [ ... ],  # lista de linhas do relatório
                "totalRowsCount": int,  # número total de linhas
                ... outros campos conforme resposta da API ...
            }
        None: Se ocorrer um erro de requisição, conexão ou decodificação JSON.

    Possíveis erros:
        - Retorna None em caso de erro de conexão, HTTP, ou se a resposta não for um JSON válido.
        - Pode retornar um dicionário contendo a chave "error" se a API Wialon retornar um erro.
    """
    payload = {
        "svc": "report/get_result_rows",
        "params": json.dumps({
            "tableIndex": table_index,
            "indexFrom": index_from,
            "indexTo": index_to
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if verbose:
            print(f"BASE: Dados do relatório obtidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception as e:
        print(f"BASE: Erro ao obter dados do relatório: {e}")
        return None







def clean_up_result(sid):
    """
    Limpa os resultados do relatório, removendo arquivos temporários ou dados desnecessários.
    """
    # Implementar limpeza de arquivos temporários ou dados desnecessários
    # Exemplo: remover arquivos temporários, limpar cache, etc.
    payload = {
        "svc": "report/cleanup_result",
        "params": "{}",
        "sid": sid
    }

    response = requests.post(API_URL, data=payload)
    response.raise_for_status()
    result = response.json()

    


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






def get_all_drivers(session_id):
    """
    Retrieve all drivers from Wialon API.
    Returns a list of drivers or an empty list on error.
    """
    print("BASE: get_all_drivers: Buscando todos os motoristas...")
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",
                "propName": "drivers",
                "propValueMask": "*",
                "sortType": "drivers"
            },
            "force": 1,
            "flags": 257,  # 8192 (drivers) + 1 (basic info)
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        drivers = []
        if "items" in result:
            for resource in result["items"]:
                drv_list = resource.get("drvrs", [])
                for drv in drv_list:
                    drivers.append(drv)
            print(f"BASE: get_all_drivers: Encontrados {len(drivers)} motoristas.")
            return drivers
        else:
            print("BASE: get_all_drivers: Nenhum recurso com motoristas encontrado.")
            return []
    except Exception as e:
        print(f"BASE: get_all_drivers: Erro ao buscar motoristas: {e}")
        return []
    

def remover_chaves(json_data, chaves_para_remover):
    for item in json_data:
        for chave in chaves_para_remover:
            item.pop(chave, None)
    return json_data






def buscadora_motoristas(session_id):
    """
    Retrieve all drivers from Wialon API.
    Returns a list of drivers or an empty list on error.
    """
    print("BASE: get_all_drivers: Buscando todos os motoristas...")
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",
                "propName": "drivers",
                "propValueMask": "*",
                "sortType": "drivers"
            },
            "force": 1,
            "flags": 1,  # 8192 (drivers) + 1 (basic info)
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    response = requests.post(API_URL, data=params)
    response.raise_for_status()
    result = response.json()
    return result.get("items", [])


def STATUS(sid):
    nome = "STATUS"
    def comm(msg):
        print(colored("*"*30, "green"))
        print(colored(f"{nome}:","red"))
        print(f"{msg}")
        print(colored("*"*30, "green"))
    relatorios = buscadora_reports(sid)
    chaves_para_remover = ["nm", "id"]
    dados_filtrados = remover_chaves(relatorios, chaves_para_remover)
    print(json.dumps(dados_filtrados, indent=4))
    #Busca_reports()
    comm("Buscando motoristas...")
    drivers  = buscadora_motoristas(sid)
    comm(drivers)
    chaves_para_remover = ["nm", "id"]
    dados_filtrados = remover_chaves(drivers, chaves_para_remover)
    print(json.dumps(dados_filtrados, indent=4))


















################################################################################################################################
################################################################################################################################
################################################################################################################################
# --- Busca por IDs de Unidades na API Wialon ---
# A função listar_IDs busca por itens do tipo 'avl_unit' (unidades) na API Wialon e retorna uma lista de dicionários com as informações das unidades encontradas.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações sobre unidades registradas na plataforma Wialon, como veículos ou ativos monitorados.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
# A função é semelhante à função search_units, mas pode ter parâmetros de busca e flags diferentes, dependendo das necessidades específicas.




def listar_IDs(session_id):
    """
    Busca por itens do tipo 'avl_unit' (unidades) na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.

    Returns:
        list: Uma lista de dicionários representando as unidades encontradas, ou None em caso de erro.
    """
    # Define o critério de busca para unidades AVL
    # (avl_unit) na API Wialon.
    # O critério de busca pode ser ajustado conforme necessário.
    # Aqui, estamos buscando todas as unidades (wildcard "*").
    # O critério de ordenação é pelo nome da unidade.
    print("BASE: listar_IDs: Buscando unidades...")
    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": "*",         # Buscar todas as unidades (wildcard)
        "sortType": "sys_name",       # Ordenar pelo nome
        # "propType": "property",     # Opcional: tipo da propriedade
        # "or_logic": False           # Opcional: lógica OR para máscaras
    }
    flags = (
        1      # 1: Inclui informações básicas (ID, nome)
        # Adicione mais flags conforme necessário: https://sdk.wialon.com/wiki/en/kit/flags
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    print("\nBuscando unidades...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidades: {result}")
            return None

        if "items" in result:
            units = result["items"]
            print(f"Encontradas {len(units)} unidades.")
            return units
        else:
            print(f"Resposta inesperada ao buscar unidades: {result}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidades: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None

# --- Busca por todas as informações sobre uma unica unidade por ID na API Wialon ---
# A função busca_unidade_por_id busca por uma unidade específica na API Wialon usando seu ID.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações detalhadas sobre uma unidade específica, como veículo ou ativo monitorado.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
# A função é semelhante à função search_units, mas busca uma unidade específica em vez de todas as unidades.


def buscadora_ID(session_id, unit_id, flag):
    """
    Testa a busca de uma unidade específica por ID na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    # Flags para detalhar os dados retornados
    # 1: Inclui informações básicas (ID, nome)
    # 8: Inclui propriedades personalizadas
    # 256: Inclui o ícone da unidade
    # 4096: Inclui informações do último status (posição, etc.)
    # 8192: Inclui informações de status do item (se disponível)
    # 4611686018427387903: Inclui todas as informações disponíveis (todas as flags)
    # 0: Não inclui informações adicionais (apenas ID e nome)

    url = f"https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={{\"id\":{unit_id},\"flags\":{flag}}}&sid={session_id}"
    #print(f"URL gerada para teste: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON: {response.text}")
        return None


def buscadora_usuarios(session_id):
    """
    Busca por usuários na API Wialon.
    
    Returns:
        list: Uma lista de dicionários representando os usuários encontrados, ou None em caso de erro.
    """
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",
                "propName": "drivers",
                "propValueMask": "*",
                "sortType": "drivers",
                "propType": "propitemname",
                "or_logic": False
            },
            "force": 1,
            "flags": 1,
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar usuários: {result}")
            return None

        if "items" in result:
            users = result["items"]
            print(f"Encontrados {len(users)} usuários.")

            # Exibe os IDs e nomes dos usuários encontrados

            return users
        else:
            print(f"Resposta inesperada ao buscar usuários: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar usuários: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None







###############################################################################################################
def para_txt(result):
    unit_name = result.get('item', {}).get('nm', 'unidade_desconhecida')
    file_path = f"{deposito}/{unit_name}.txt"
    with open(file_path, 'w') as file:
        file.write(json.dumps(result, indent=4))  # Salva o resultado formatado em JSON
    print(f"Resultado salvo em: {file_path}")



# --- Função para exportar dados de buscadora_ID para Excel ---
# A função para_excel exporta os dados obtidos pela função buscadora_ID para um arquivo Excel.
# A função utiliza a biblioteca pandas para criar um DataFrame e salvar os dados em um arquivo Excel.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
def para_excel(result):
    """
    Exporta os dados obtidos pela função buscadora_ID para um arquivo Excel.

    Args:
        result (dict): O resultado da busca da unidade.

    Returns:
        str: O caminho do arquivo Excel gerado.
    """
    unit_name = result.get('item', {}).get('nm', 'unidade_desconhecida')
    file_path = f"{deposito}/{unit_name}.xlsx"
    
    # Converte o dicionário em um DataFrame do pandas
    df = pd.DataFrame([result])

    # Salva o DataFrame em um arquivo Excel
    df.to_excel(file_path, index=False)
    
    print(f"Resultado exportado para: {file_path}")
    return file_path

############################################################################################

#funcao principal de parsing
# --- Função para exibir os dados em colunas ---
def parsing(result):
    # String com o dado recebido (formato de dicionário)

    # Converte a string para um dicionário Python
    data = ast.literal_eval(result)

    def flatten_dict(d, parent_key='', sep='_'):
        """
        Achata recursivamente um dicionário aninhado.
        
        Parâmetros:
        d: dicionário a ser achatado.
        parent_key: string com prefixo para renomear chaves aninhadas.
        sep: separador entre chaves concatenadas.
        
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

    # Achata o dicionário original
    flat_data = flatten_dict(data)

    # Exibe os dados separados em "colunas" (ou campos)
    print("Dados separados em colunas:")
    for key, value in flat_data.items():
        print(f"{key}: {value}")



def Decodificador_json(result):
    """
    Decodifica um JSON e exibe os dados em colunas.
    """

    dados = json.loads(result)  # Converte a string JSON para um dicionário Python
    #exibe os dados em colunas
    print("Dados separados em colunas:")
    for key, value in dados.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


    
# --- teste -------
def teste_busca_unidades():
    print("BASE: Testando a conexão com o Wialon...")
    sid = wialon_login(WIALON_TOKEN)

    if sid:
        units_list = search_units(sid)

        if units_list:
            print("\n--- Lista de Unidades ---")
            for unit in units_list:
                # Extrai algumas informações básicas
                unit_id = unit.get('id', 'N/A')
                unit_name = unit.get('nm', 'Sem Nome')
                last_message = unit.get('pos', None) # Última posição/status (requer flag 4096)
                latitude = "N/A"
                longitude = "N/A"
                timestamp = "N/A"

                if last_message:
                    latitude = last_message.get('y', 'N/A')
                    longitude = last_message.get('x', 'N/A')
                    # O timestamp é em segundos Unix
                    ts_unix = last_message.get('t', None)
                    if ts_unix:
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S UTC')

                print(f"ID: {unit_id}, Nome: {unit_name}, Lat: {latitude}, Lon: {longitude}, Última Msg: {timestamp}")

                # Você pode acessar outras propriedades aqui, dependendo das flags usadas
                # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
                # if props:
                #     print(f"  Propriedades: {props}")

        # Sempre tente fazer logout ao final
        wialon_logout(sid)
    else:
        print("\nNão foi possível continuar sem um Session ID válido.")


def busca_unidade_por_id(session_id, unit_id):
    """
    Busca por uma unidade específica na API Wialon usando seu ID.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    # Validar o unit_id para garantir que seja uma string e não vazio
    if not isinstance(unit_id, (int, str)) or not str(unit_id).strip():
        print(f"Erro: unit_id inválido: {unit_id}")
        return None

    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": str(unit_id).strip(),  # Buscar pela unidade específica
        "sortType": "sys_name",       # Ordenar pelo nome
    }
    flags = (
        1 |       # 1: Inclui informações básicas (ID, nome)
        8 |       # 8: Inclui propriedades personalizadas
        256 |     # 256: Inclui o ícone da unidade
        4096      # 4096: Inclui informações do último status (posição, etc.)
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    print(f"\nBASE: Buscando unidade com ID {unit_id}...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None

        if "items" in result and len(result["items"]) > 0:
            unit = result["items"][0]
            print(f"Unidade encontrada: {unit}")
            return unit
        else:
            print(f"Unidade com ID {unit_id} não encontrada.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None
    
def teste_busca_unidade_por_id(session_id, unit_id):
    """
    Testa a busca de uma unidade específica por ID na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    url = f"https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={{\"id\":{unit_id},\"flags\":1025}}&sid={session_id}"
    print(f"URL gerada para teste: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None

        print(f"Resposta da API: {result}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON: {response.text}")
        return None



def lista_unidades(sid):
    units_list = search_units(sid)
    print("\n--- Lista de Unidades ---")
    units_dict = {}
    for unit in units_list:
        # Extrai algumas informações básicas
        unit_id = unit.get('id', 'N/A')
        unit_name = unit.get('nm', 'Sem Nome')
        units_dict[unit_id] = unit_name
    return units_dict


def listar_IDs(sid):
    units_list = search_units(sid)
    ids_list = [unit.get('id', 'N/A') for unit in units_list]
    return ids_list



def teste_parsing():
    # String com o dado recebido (formato de dicionário)
    data_str = """{'item': {'nm': 'TLZ0C54_CPBracell', 'cls': 2, 'id': 401790184, 'mu': 0, 
    'pos': {'t': 1746440259, 'f': 7, 'lc': 0, 'y': -22.4147930145, 'x': -50.5946235657, 
    'c': 336, 'z': 486.700012207, 's': 64, 'sc': 13}, 
    'lmsg': {'t': 1746440259, 'f': 7, 'tp': 'ud', 
    'pos': {'y': -22.4147930145, 'x': -50.5946235657, 'c': 336, 'z': 486.700012207, 's': 64, 'sc': 13}, 
    'i': 0, 'o': 4, 'lc': 0, 'rt': 1746440261, 
    'p': {'fms_speed': 67, 'hdop': 0, 'fms_coolant_temp': 92, 'fms_fuel_percentage': 255, 
    'fms_eng_payload': 18, 'fms_accumulated_fuel_cons': 80764, 'ign_on_interval': 60, 
    'ign_off_interval': 3600, 'angle_interval': 15, 'distance_interval': 100, 'overspeed': 0, 
    'rssi': 72, 'gps_data': 77, 'gsensor_sens': 0, 'manager_status': 0, 'other': 0, 
    'heartbeat': 5, 'relay_status': 71, 'drag_alarm': 0, 'digital_io': 16832, 'ign': 1, 
    'digital_out': 32, 'adc1': 0, 'adc2': 0, 'alarm': 0, 'reserve': 213, 
    'odometer': 149519000, 'battery': 100, 'pwr_int': 3.9, 'pwr_ext': 28.93, 
    'rpm': 550, 'battery_monitoring': 0, 'temp_int': 42}}, 
    'uacl': 3849196688227}, 
    'flags': 1025}"""


    # Converte a string para um dicionário Python
    data = ast.literal_eval(data_str)

    def flatten_dict(d, parent_key='', sep='_'):
        """
        Achata recursivamente um dicionário aninhado.
        
        Parâmetros:
        d: dicionário a ser achatado.
        parent_key: string com prefixo para renomear chaves aninhadas.
        sep: separador entre chaves concatenadas.
        
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

    # Achata o dicionário original
    flat_data = flatten_dict(data)

    # Exibe os dados separados em "colunas" (ou campos)
    print("Dados separados em colunas:")
    for key, value in flat_data.items():
        print(f"{key}: {value}")


def PRINCIPAL():
    sid = wialon_login(WIALON_TOKEN)
    lista_unidades(sid)

    # Você pode acessar outras propriedades aqui, dependendo das flags usadas
    # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
    # if props:
    #     print(f"  Propriedades: {props}")

    wialon_logout(sid)




##########################################################################
def base():
        sid = wialon_login(WIALON_TOKEN)
        listar_IDs(sid)
        #busca_unidade_por_id(sid, 401790184)
        #teste_parsing()


        # Você pode acessar outras propriedades aqui, dependendo das flags usadas
        # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
        # if props:
        #     print(f"  Propriedades: {props}")

        wialon_logout(sid)

#######################################################################################
# --- Função para buscar usuários na API Wialon ---
# A função Busca_Users busca por usuários na API Wialon e exibe os IDs e nomes dos usuários encontrados.




def Busca_Users():
    sid = wialon_login(WIALON_TOKEN)
    usuarios = buscadora_usuarios(sid)
    print(usuarios)
    # Exibe os IDs e nomes dos usuários encontrados
    for usuario in usuarios:
        user_id = usuario.get('id', 'N/A')
        user_name = usuario.get('nm', 'Sem Nome')
        print(f"ID: {user_id}, Nome: {user_name}")
    #save_users_to_excel(usuarios)
    wialon_logout(sid)




def save_users_to_excel(usuarios):
    df = pd.DataFrame(usuarios)
    df.to_excel(os.path.join(ALPHA, f"usuarios.xlsx"), index=False)
    print(df)



def teste():
    sid = wialon_login(WIALON_TOKEN)
    relatorio = execute_report(sid, 401756219, 59, 401790521)
    print(relatorio)
    report_data = GET_REPORT_DATA(sid, table_index=0, index_from=0, index_to=100)
    print(report_data)
    wialon_logout(sid)
#####################################################################################
# teste wialon





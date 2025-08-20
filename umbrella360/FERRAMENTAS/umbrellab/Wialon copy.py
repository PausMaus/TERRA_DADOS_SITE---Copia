import json
import requests
import time
from termcolor import colored
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
import pandas as pd


# Verifique se esta é a URL correta para sua instância Wialon (Hosting ou Local)
WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API 
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"

# Caminho do depósito para salvar arquivos JSON
DEPOSITO = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"

def log_colored(message: str, color: str = "white") -> None:    
    """
    Exibe uma mensagem no terminal com a cor especificada.
    
    :param message: Mensagem a ser exibida.
    :param color: Cor da mensagem (default é "white").
    """
    print(colored(message, color))

def save_json_to_deposito(data: Any, filename: str) -> None:
    """
    Salva dados JSON no depósito.
    
    :param data: Dados a serem salvos.
    :param filename: Nome do arquivo (sem extensão).
    """
    try:
        if not os.path.exists(DEPOSITO):
            os.makedirs(DEPOSITO)
        
        filepath = os.path.join(DEPOSITO, f"{filename}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        log_colored(f"Dados salvos em: {filepath}", "green")
    except Exception as e:
        log_colored(f"Erro ao salvar {filename}.json: {str(e)}", "red")

def flatten_dict(d: Dict[str, Any]) -> Dict[str, Any]:  
    """
    Achata um dicionário aninhado em um dicionário plano.
    
    :param d: Dicionário a ser achatado.
    :return: Dicionário achatado.
    """
    flat_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            for sub_key, sub_value in flatten_dict(value).items():
                flat_dict[f"{key}.{sub_key}"] = sub_value
        else:
            flat_dict[key] = value
    return flat_dict

def authenticate_with_wialon(WIALON_TOKEN: str) -> Optional[str]:
    """
    Autentica na API Wialon e retorna o SID (Session ID).
    
    :return: SID se a autenticação for bem-sucedida, None caso contrário.
    """
    log_colored("Iniciando autenticação na API Wialon...", "yellow")
    
    # Seguindo a documentação: POST request com Content-Type application/x-www-form-urlencoded
    payload = {
        "svc": "token/login",
        "params": json.dumps({
            "token": WIALON_TOKEN,
            "appName": "UMBRELLA360",
            "operateAs": ""
        })
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(API_URL, data=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            log_colored(f"Erro de API no login: {result['error']}", "red")
            return None
        
        sid = result.get("eid")
        if sid:
            log_colored(f"Login bem-sucedido! SID: {sid}", "green")
            log_colored(f"Logado como: {result.get('user', {}).get('nm', 'Usuário não identificado')}", "cyan")
            return sid
        else:
            log_colored("Erro: SID não retornado pela API", "red")
            return None
            
    except requests.exceptions.RequestException as e:
        log_colored(f"Erro de conexão: {str(e)}", "red")
        return None
    except json.JSONDecodeError:
        log_colored("Erro ao decodificar resposta JSON", "red")
        return None

def wialon_logout(sid: str) -> bool:
    """
    Faz logout da sessão Wialon.
    
    :param sid: Session ID obtido após o login.
    :return: True se logout bem-sucedido, False caso contrário.
    """
    log_colored("Fazendo logout da sessão Wialon...", "yellow")
    
    payload = {
        "svc": "core/logout",
        "params": "{}",
        "sid": sid
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(API_URL, data=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            log_colored(f"Erro no logout: {result['error']}", "red")
            return False
        
        log_colored("Logout realizado com sucesso.", "green")
        return True
        
    except Exception as e:
        log_colored(f"Erro ao fazer logout: {str(e)}", "red")
        return False

def set_locale():
    """
    Define the locale for the application.
    """
    payload = {
        "svc": "render/set_locale",
        "params": {
            "tzOffset": 0,
            "language": "EN",
            "flags": 0,
            "formatDate": "%H:%M:%S %d-%m-%Y",
            "density": 1
        }
    }
    response = requests.post(API_URL, json=payload)
    print(f"Wialon: set_locale: Resposta da API: {response.json()}")

def clean_up_result(sid):
    """
    Limpa os resultados do relatório da memória do servidor.
    """
    nome = "clean_up_result"
    def comm(msg):
        print(colored("="*30, "cyan"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "cyan"))
    
    payload = {
        "svc": "report/cleanup_result",
        "params": "{}",  # Não requer parâmetros
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            error_code = data["error"]
            #comm(f"Erro {error_code} ao limpar resultado")
            return False

        #comm("Resultado limpo com sucesso")
        return True
        
    except Exception as e:
        #comm(f"Erro ao limpar resultado: {e}")
        return False

def wait_for_report_completion(sid, timeout=300, check_interval=5):
    """
    Aguarda a conclusão do relatório, verificando o status periodicamente.
    
    :param sid: Session ID obtido após o login.
    :param timeout: Tempo limite em segundos para aguardar (padrão: 300s/5min).
    :param check_interval: Intervalo em segundos entre verificações (padrão: 5s).
    :return: True se relatório concluído com sucesso, False caso contrário, 
             "status_16" se status desconhecido 16 for detectado.
    """
    nome = "wait_for_report_completion"
    def comm(msg):
        print(colored("="*30, "cyan"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "cyan"))
    
    comm(f"Aguardando conclusão do relatório (timeout: {timeout}s)...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status_data = get_report_status(sid)
        
        if status_data is None:
            comm("Erro ao obter status do relatório")
            return False
        
        status = status_data.get("status", 0)
        
        if status == 2:  # Relatório concluído com sucesso
            comm("Relatório concluído com sucesso!")
            return True
        elif status == 3:  # Relatório concluído com erro
            comm("Relatório concluído com erro!")
            return False
        elif status == 4:  # Relatório cancelado
            comm("Relatório foi cancelado!")
            return False
        elif status == 1:  # Relatório em execução
            progress = status_data.get("progress", 0)
            comm(f"Relatório em execução... Progresso: {progress}%")
        elif status == 0:  # Nenhum relatório em execução
            comm("Nenhum relatório em execução")
            return False
        elif status == 16:  # Status desconhecido 16
            comm("Status desconhecido 16 detectado - possível problema com a unidade")
            return "status_16"
        else:
            comm(f"Status desconhecido: {status}")
            return False
        
        time.sleep(check_interval)
    
    comm(f"Timeout atingido ({timeout}s) - Relatório não concluído")
    return False



#########################################################################################

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
            "flags": 1, #247
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        #-----
        #print(f"Wialon: unidades_simples: Resultado da busca: {result}")
        #-----
        return result.get("items", [])
    except Exception as e:
        comm(f"Erro ao buscar unidades: {e}")
        return []
    
def motoristas_simples(session_id):
    """
    Retrieve all available drivers (avl_resource) from Wialon.
    """
    nome = "Buscadora de Motoristas Simples"
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
            "flags": 257,  # 1 (basic info) + 256 (drivers info)
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        resultado = result.get("items", [])
        return resultado
    except Exception as e:
        comm(f"Erro ao buscar motoristas: {e}")
        return []
    
def motoristas_simples2(session_id):
    """
    Retrieve all available drivers (avl_resource) from Wialon and extract driver details.
    """
    nome = "Buscadora de Motoristas Simples v2"
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
                "propName": "drivers",
                "propValueMask": "*",
                "sortType": "drivers",
            },
            "force": 1,
            "flags": 257,  # 1 (basic info) + 256 (drivers info)
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        #comm(f"Resultado da busca: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        resources = result.get("items", [])
        motoristas_lista = []
        
        for resource in resources:
            resource_name = resource.get("nm", "Recurso sem nome")
            resource_id = resource.get("id", 0)
            
            # Extrai os motoristas do campo 'drvrs'
            drivers_dict = resource.get("drvrs", {})
            
            if drivers_dict:
                comm(f"Recurso '{resource_name}' (ID: {resource_id}): {len(drivers_dict)} motorista(s)")
                
                # Itera sobre o dicionário de motoristas
                for driver_key, driver_data in drivers_dict.items():
                    motorista_info = {
                        "resource_id": resource_id,
                        "resource_name": resource_name,
                        "driver_id": driver_data.get("id", 0),
                        "driver_name": driver_data.get("n", "Nome não disponível"),
                        "driver_code": driver_data.get("c", ""),
                        "driver_description": driver_data.get("ds", ""),
                        "phone": driver_data.get("p", ""),
                        "creation_time": driver_data.get("ct", 0),
                        "modification_time": driver_data.get("mt", 0),
                        "bound_unit": driver_data.get("pu", 0),  # Unidade vinculada
                        "bind_time": driver_data.get("bt", 0),   # Tempo de vinculação
                        "position": driver_data.get("pos", {}),  # Posição atual
                    }
                    motoristas_lista.append(motorista_info)
        
        comm(f"Total de motoristas encontrados: {len(motoristas_lista)}")
        
        # Log dos motoristas encontrados
        for motorista in motoristas_lista:
            #comm(f"ID: {motorista['driver_id']} | Nome: {motorista['driver_name']} | Código: {motorista['driver_code']}")
            pass
        return motoristas_lista
        
    except Exception as e:
        comm(f"Erro ao buscar motoristas: {e}")
        return []

def get_all_drivers_basic(session_id):
    """
    Retrieve all drivers with basic information from Wialon.
    Searches for avl_resource items that contain drivers.
    
    Args:
        session_id (str): The Session ID obtained from login.
    
    Returns:
        list: A list of dictionaries containing driver information, or empty list on error.
    """
    nome = "Buscadora de Motoristas - Informações Básicas"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:", "green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    
    # Search for resources that contain drivers
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",     # Resource type (contains drivers)
                "propName": "sys_name",          # Property to search by
                "propValueMask": "*",            # Search all resources
                "sortType": "sys_name"           # Sort by system name
            },
            "force": 1,                          # Force refresh
            "flags": 257,                       # 1 (basic info) + 256 (drivers info)
            "from": 0,                           # Start index
            "to": 0                              # End index (0 = all)
        }),
        "sid": session_id
    }
    
    try:
        comm("Buscando recursos com motoristas...")
        
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            comm(f"Erro de API: {result['error']}")
            return []
        
        drivers_list = []
        
        if "items" in result:
            resources = result["items"]
            comm(f"Encontrados {len(resources)} recursos.")
            
            # Extract drivers from each resource
            for resource in resources:
                resource_name = resource.get("nm", "Recurso sem nome")
                resource_id = resource.get("id", 0)
                
                # Get drivers from this resource
                drivers_data = resource.get("drvrs", [])
                
                if drivers_data:
                    comm(f"Recurso '{resource_name}': {len(drivers_data)} motorista(s)")
                    
                    for driver in drivers_data:
                        driver_info = {
                            "resource_id": resource_id,
                            "resource_name": resource_name,
                            "driver_id": driver.get("id", 0),
                            "driver_name": driver.get("n", "Nome não disponível"),
                            "driver_code": driver.get("c", ""),
                            "driver_description": driver.get("ds", ""),
                            "phone": driver.get("p", ""),
                            "email": driver.get("e", ""),
                            "creation_time": driver.get("ct", 0),
                            "modification_time": driver.get("mt", 0)
                        }
                        drivers_list.append(driver_info)
            
            comm(f"Total de motoristas encontrados: {len(drivers_list)}")
            return drivers_list
        else:
            comm("Nenhum recurso encontrado.")
            return []
            
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão: {e}")
        return []
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return []
    except Exception as e:
        comm(f"Erro inesperado: {e}")
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
    

def buscadora_reports(session_id):
    """
    Busca por relatorios na API Wialon.
    
    Returns:
        list: Uma lista de dicionários representando os relatórios encontrados, ou None em caso de erro.
    """
    nome = "Buscadora de Relatorios"
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
            users = [item["nm"] for item in result["items"]]
            comm(f"Encontrados {len(users)} usuários.")
            comm(f"Usuários encontrados: {users}")
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


def search_item(sid, id, flags):

    payload = {
        "svc": "core/search_item",
        "params": json.dumps({
            "id": id,
            "flags": flags
        }),
        "sid": sid
    }

    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            log_colored(f"Erro na busca de itens: {result['error']}", "red")
            return None

        log_colored("Busca de itens realizada com sucesso.", "green")
        return result.get("data", [])

    except Exception as e:
        log_colored(f"Erro ao buscar itens: {str(e)}", "red")
        return None



#######################################################################################################



def exec_report(sid, resource_id, template_id, unit_id, interval_from, interval_to):
    """
    Executa um relatório específico para uma unidade no Wialon.
    
    :param sid: Session ID obtido após o login.
    :param resource_id: ID do recurso onde o relatório está localizado.
    :param template_id: ID do modelo de relatório a ser executado.
    :param unit_id: ID da unidade para a qual o relatório será gerado.
    :return: Resultado do relatório ou None em caso de erro.
    """
    nome = "exec_report"
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
                "from": interval_from,
                "to": interval_to,
                "flags": 0  # CORREÇÃO: 0 para timestamps absolutos Unix
            }
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        
        if "error" in data:
            error_code = data["error"]
            comm(f"Erro {error_code} ao executar relatório")
            
            # Códigos de erro comuns
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado - verificar permissões do usuário",
                5: "Erro na requisição - parâmetros inválidos (IDs ou interval)",
                6: "Não autorizado - usuário sem permissão para este relatório",
                7: "Failed to fetch the report object and report resource with the desired ACL",
                14: "Relatório não encontrado",
                1001: "Parâmetros inválidos",
                1002: "Recurso não encontrado",
                1003: "Template não encontrado"
            }
            
            if error_code in error_messages:
                comm(f"Descrição: {error_messages[error_code]}")
            
            return None
            
        # Verifica se o relatório foi executado com sucesso
        if isinstance(data, dict) and data.get("error") is None:
            #comm(f"Relatório executado com sucesso")
            return data
            
        return data
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None

def exec_report_02(sid, resource_id, template_id, unit_id, interval_from, interval_to):
    """
    Executa um relatório específico para uma unidade no Wialon.
    
    :param sid: Session ID obtido após o login.
    :param resource_id: ID do recurso onde o relatório está localizado.
    :param template_id: ID do modelo de relatório a ser executado.
    :param unit_id: ID da unidade para a qual o relatório será gerado.
    :return: Resultado do relatório ou None em caso de erro.
    """
    nome = "exec_report-02"
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
            "reportObjectSecId": 1,
            "interval": {
                "from": interval_from,
                "to": interval_to,
                "flags": 0  # CORREÇÃO: 0 para timestamps absolutos Unix
            }
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        comm(f"Resposta da API: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None

def exec_report_03(sid, flag, dias, reportResourceId, reportTemplateId, reportObjectId, reportObjectSecId):
    """
    Executa um relatório específico para uma unidade no Wialon.
    
    :param sid: Session ID obtido após o login.
    :param resource_id: ID do recurso onde o relatório está localizado.
    :param template_id: ID do modelo de relatório a ser executado.
    :param unit_id: ID da unidade para a qual o relatório será gerado.
    :return: Resultado do relatório ou None em caso de erro.
    """
    nome = "exec_report-03"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    

    payload = {
        "svc": "report/exec_report",
        "params": json.dumps({
            "reportResourceId": reportResourceId,
            "reportTemplateId": reportTemplateId,
            "reportObjectId": reportObjectId,
            "reportObjectSecId": reportObjectSecId,
            "interval": {
                "from": 0,
                "to": dias,
                "flags": flag,
                "reportObjectIdList":[]  # CORREÇÃO: 0 para timestamps absolutos Unix
            }
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        comm(f"Resposta da API: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None




################################


def get_report_status(sid):
    """
    Obtém o status atual do relatório em execução.
    
    :param sid: Session ID obtido após o login.
    :return: Dicionário com informações do status do relatório ou None em caso de erro.
    """
    nome = "get_report_status"
    def comm(msg):
        print(colored("="*30, "yellow"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "yellow"))
    
    payload = {
        "svc": "report/get_report_status",
        "params": "{}",  # Não requer parâmetros adicionais
        "sid": sid
    }
    
    try:
        comm("Verificando status do relatório...")
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        comm(f"Resposta da API: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if "error" in data:
            error_code = data["error"]
            comm(f"Erro {error_code} ao obter status do relatório")
            
            # Códigos de erro comuns
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado",
                5: "Erro na requisição",
                6: "Não autorizado",
                7: "Limite de tempo excedido",
                14: "Nenhum relatório em execução",
                16: "Inválido"
            }
            
            if error_code in error_messages:
                comm(f"Descrição: {error_messages[error_code]}")
            
            return None
        
        # Interpreta o status retornado
        if isinstance(data, dict):
            status = data.get("status", 0)
            
            status_messages = {
                0: "Nenhum relatório em execução",
                1: "Relatório em execução",
                2: "Relatório concluído com sucesso",
                3: "Relatório concluído com erro",
                4: "Relatório cancelado"
            }
            
            status_msg = status_messages.get(status, f"Status desconhecido: {status}")
            comm(f"Status do relatório: {status_msg}")
            
            # Informações adicionais se disponíveis
            if "progress" in data:
                comm(f"Progresso: {data['progress']}%")
            
            if "time" in data:
                comm(f"Tempo decorrido: {data['time']} segundos")
            
            if "msgsCount" in data:
                comm(f"Número de mensagens processadas: {data['msgsCount']}")
            
            return data
        
        return data
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None



def get_result_rows(sid, table_index=0, index_from=0, index_to=0):
    """
    Obtém as linhas de dados de um relatório já executado.
    
    :param sid: Session ID obtido após o login.
    :param table_index: Índice da tabela do relatório (padrão: 0).
    :param index_from: Índice inicial dos dados (padrão: 0).
    :param index_to: Índice final dos dados (0 = todos os dados).
    :return: Lista de linhas de dados ou None em caso de erro.
    """
    nome = "get_result_rows"
    def comm(msg):
        print(colored("="*30, "magenta"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "magenta"))
    
    payload = {
        "svc": "report/get_result_rows",
        "params": json.dumps({
            "tableIndex": table_index,
            "indexFrom": index_from,
            "indexTo": index_to
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        # Não mostra resposta completa pois pode ser muito grande
        #comm(f"Resposta recebida - tamanho: {len(str(data))} caracteres")
        
        if "error" in data:
            error_code = data["error"]
            #comm(f"Erro {error_code} ao obter linhas do relatório")
            
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado",
                5: "Erro na requisição - parâmetros inválidos",
                6: "Não autorizado",
                7: "Limite de tempo excedido",
                14: "Nenhum relatório disponível para leitura",
                16: "Índice de tabela inválido"
            }
            
            if error_code in error_messages:
                #comm(f"Descrição: {error_messages[error_code]}")
                pass
            return None
        
        # Verifica se há dados retornados
        if isinstance(data, list):
            #comm(f"Obtidas {len(data)} linhas de dados")
            

            return data
        
        elif isinstance(data, dict):
            # Às vezes a resposta pode vir em formato diferente
            rows = data.get("rows", [])
            if rows:
                #comm(f"Obtidas {len(rows)} linhas de dados (formato dict)")
                return rows
            else:
                #comm("Nenhuma linha de dados encontrada")
                return []
        
        comm("Formato de resposta inesperado")
        return None
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None

def select_result_rows(sid, table_index, index_from, index_to, level):
    """
    Obtém as linhas de dados de um relatório já executado.
    
    :param sid: Session ID obtido após o login.
    :param table_index: Índice da tabela do relatório (padrão: 0).
    :param index_from: Índice inicial dos dados (padrão: 0).
    :param index_to: Índice final dos dados (0 = todos os dados).
    :return: Lista de linhas de dados ou None em caso de erro.
    """
    nome = "get_result_rows"
    def comm(msg):
        print(colored("="*30, "magenta"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "magenta"))
    

    payload = {
        "svc": "report/select_result_rows",
        "params": json.dumps({
            "tableIndex": table_index,
            "config": {
                "type": "range",
                "data": {"from": index_from, "to": index_to, "level": level}
            }
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        # Não mostra resposta completa pois pode ser muito grande
        #comm(f"Resposta recebida - tamanho: {len(str(data))} caracteres")
        
        if "error" in data:
            error_code = data["error"]
            #comm(f"Erro {error_code} ao obter linhas do relatório")
            
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado",
                5: "Erro na requisição - parâmetros inválidos",
                6: "Não autorizado",
                7: "Limite de tempo excedido",
                14: "Nenhum relatório disponível para leitura",
                16: "Índice de tabela inválido"
            }
            
            if error_code in error_messages:
                #comm(f"Descrição: {error_messages[error_code]}")
                pass
            return None
        
        # Verifica se há dados retornados
        if isinstance(data, list):
            #comm(f"Obtidas {len(data)} linhas de dados")
            

            return data
        
        elif isinstance(data, dict):
            # Às vezes a resposta pode vir em formato diferente
            rows = data.get("rows", [])
            if rows:
                #comm(f"Obtidas {len(rows)} linhas de dados (formato dict)")
                return rows
            else:
                #comm("Nenhuma linha de dados encontrada")
                return []
        
        comm("Formato de resposta inesperado")
        return None
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None

def get_result_subrows(sid, table_index=0, row_index=0, level=0):
    """
    Obtém sub-linhas de uma linha específica do relatório (para relatórios hierárquicos).
    
    :param sid: Session ID obtido após o login.
    :param table_index: Índice da tabela do relatório (padrão: 0).
    :param row_index: Índice da linha principal.
    :param level: Nível da hierarquia (padrão: 0).
    :return: Lista de sub-linhas ou None em caso de erro.
    """
    nome = "get_result_subrows"
    def comm(msg):
        print(colored("="*30, "magenta"))
        print(colored(f"{nome}:","green"))
        print(f"{msg}")
        print(colored("="*30, "magenta"))
    
    payload = {
        "svc": "report/get_result_subrows",
        "params": json.dumps({
            "tableIndex": table_index,
            "rowIndex": row_index,
            "level": level
        }),
        "sid": sid
    }
    
    try:
        comm(f"Obtendo sub-linhas da linha {row_index} (tabela {table_index}, nível {level})")
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            error_code = data["error"]
            comm(f"Erro {error_code} ao obter sub-linhas")
            
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado",
                5: "Erro na requisição - parâmetros inválidos",
                14: "Nenhum relatório disponível para leitura",
                16: "Índice inválido"
            }
            
            if error_code in error_messages:
                comm(f"Descrição: {error_messages[error_code]}")
            
            return None
        
        if isinstance(data, list):
            comm(f"Obtidas {len(data)} sub-linhas")
            return data
        
        comm("Nenhuma sub-linha encontrada")
        return []
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None

def Colheitadeira_JSON(sid, resource_id, unit_id, id_relatorio, tempo_dias, periodo):
    """
    Função para coletar dados de relatório de uma unidade específica para um período.
    
    :param sid: Session ID da API Wialon
    :param unit_id: ID da unidade
    :param id_relatorio: ID do template de relatório
    :param tempo_dias: Número de dias para buscar (7 ou 30)
    :param periodo: String descritiva do período
    :return: DataFrame com os dados ou None se não houver dados
    """
    nome = "Colheitadeira_JSON"
    def comm(msg):
        print(colored("="*30, "blue"))
        print(colored(f"{nome}:", "green"))
        print(f"{msg}")
        print(colored("="*30, "blue"))

    # CORREÇÃO: Calcula timestamps UNIX corretos
    current_time = int(time.time())
    interval_from = current_time - (tempo_dias * 24 * 3600)  # X dias atrás
    interval_to = current_time  # Agora
    
    try:
        # Executa o relatório
        relatorio = exec_report(
            sid=sid, 
            resource_id=resource_id, 
            template_id=id_relatorio, 
            unit_id=unit_id, 
            interval_from=interval_from, 
            interval_to=interval_to
        )
        print(relatorio)
        
        if not relatorio:
            comm(f"❌ Falha ao executar relatório para unidade {unit_id}")
            return None

        #print(f"Relatório executado: {relatorio}")

        # Verifica se há tabelas no resultado
        tables = relatorio.get('reportResult', {}).get('tables', [])
        if not tables:
            comm(f"⚠️ Nenhuma tabela encontrada no relatório para unidade {unit_id}")
            return None
        
        # Extrai headers
        headers = extract_report_headers(relatorio)
        if not headers:
            comm(f"⚠️ Nenhum header encontrado no relatório para unidade {unit_id}")
            return None
        
        #print(f"Headers do relatório: {headers}")
        
        # Obtém as linhas de dados
        rows = get_result_rows(sid)
        if not rows:
            comm(f"⚠️ Nenhuma linha de dados encontrada para unidade {unit_id}")
            return None
        
        #print(f"Linhas obtidas: {len(rows)}")
        
        # Verifica se há dados na primeira linha
        if len(rows) == 0:
            comm(f"⚠️ Array de linhas vazio para unidade {unit_id}")
            return None
        
        first_row = rows[0]
        if not isinstance(first_row, dict) or 'c' not in first_row:
            comm(f"⚠️ Estrutura de dados inválida para unidade {unit_id}: {first_row}")
            return None
        
        report_data = first_row['c']
        if not report_data:
            comm(f"⚠️ Dados de relatório vazios para unidade {unit_id}")
            return None
        
        #print(f"Dados do relatório: {report_data}")
        
        # Verifica compatibilidade entre headers e dados
        if len(headers) != len(report_data):
            comm(f"⚠️ Incompatibilidade: {len(headers)} headers vs {len(report_data)} dados para unidade {unit_id}")
            # Tenta ajustar usando o menor tamanho
            min_length = min(len(headers), len(report_data))
            headers = headers[:min_length]
            report_data = report_data[:min_length]
            comm(f"🔧 Ajustado para {min_length} colunas")
        
        # Cria o DataFrame
        relatorio_df = pd.DataFrame([report_data], columns=headers)
        
        # Adiciona metadados
        relatorio_df['id'] = f"{interval_from}_{interval_to}_{unit_id}"
        relatorio_df['unit_id'] = unit_id
        relatorio_df['periodo'] = periodo
        relatorio_df['timestamp_from'] = interval_from
        relatorio_df['timestamp_to'] = interval_to
        
        #print(f"✅ DataFrame criado com sucesso:")
        #print(relatorio_df)
        #print(f"Headers do DataFrame: {relatorio_df.columns.tolist()}")
        
        return relatorio_df
        
    except Exception as e:
        comm(f"❌ Erro inesperado ao processar unidade {unit_id}: {str(e)}")
        return None

def Colheitadeira_JSON_02(sid, resource_id, unit_id, id_relatorio, tempo_dias, periodo):
    """
    Função para coletar dados de relatório de uma unidade específica para um período.
    
    :param sid: Session ID da API Wialon
    :param unit_id: ID da unidade
    :param id_relatorio: ID do template de relatório
    :param tempo_dias: Número de dias para buscar (7 ou 30)
    :param periodo: String descritiva do período
    :return: DataFrame com os dados ou None se não houver dados
    """
    nome = "Colheitadeira_JSON"
    def comm(msg):
        print(colored("="*30, "blue"))
        print(colored(f"{nome}:", "green"))
        print(f"{msg}")
        print(colored("="*30, "blue"))

    # CORREÇÃO: Calcula timestamps UNIX corretos
    current_time = int(time.time())
    interval_from = current_time - (tempo_dias * 24 * 3600)  # X dias atrás
    interval_to = current_time  # Agora
    
    try:
        # Executa o relatório
        relatorio = exec_report_02(
            sid=sid, 
            resource_id=resource_id, 
            template_id=id_relatorio, 
            unit_id=unit_id, 
            interval_from=interval_from, 
            interval_to=interval_to
        )
        print(relatorio)
        
        if not relatorio:
            comm(f"❌ Falha ao executar relatório para unidade {unit_id}")
            return None

        #print(f"Relatório executado: {relatorio}")

        # Verifica se há tabelas no resultado
        tables = relatorio.get('reportResult', {}).get('tables', [])
        if not tables:
            comm(f"⚠️ Nenhuma tabela encontrada no relatório para unidade {unit_id}")
            return None
        
        # Extrai headers
        headers = extract_report_headers(relatorio)
        if not headers:
            comm(f"⚠️ Nenhum header encontrado no relatório para unidade {unit_id}")
            return None
        
        #print(f"Headers do relatório: {headers}")
        
        # Obtém as linhas de dados
        rows = get_result_rows(sid)
        if not rows:
            comm(f"⚠️ Nenhuma linha de dados encontrada para unidade {unit_id}")
            return None
        
        #print(f"Linhas obtidas: {len(rows)}")
        
        # Verifica se há dados na primeira linha
        if len(rows) == 0:
            comm(f"⚠️ Array de linhas vazio para unidade {unit_id}")
            return None
        
        first_row = rows[0]
        if not isinstance(first_row, dict) or 'c' not in first_row:
            comm(f"⚠️ Estrutura de dados inválida para unidade {unit_id}: {first_row}")
            return None
        
        report_data = first_row['c']
        if not report_data:
            comm(f"⚠️ Dados de relatório vazios para unidade {unit_id}")
            return None
        
        #print(f"Dados do relatório: {report_data}")
        
        # Verifica compatibilidade entre headers e dados
        if len(headers) != len(report_data):
            comm(f"⚠️ Incompatibilidade: {len(headers)} headers vs {len(report_data)} dados para unidade {unit_id}")
            # Tenta ajustar usando o menor tamanho
            min_length = min(len(headers), len(report_data))
            headers = headers[:min_length]
            report_data = report_data[:min_length]
            comm(f"🔧 Ajustado para {min_length} colunas")
        
        # Cria o DataFrame
        relatorio_df = pd.DataFrame([report_data], columns=headers)
        
        # Adiciona metadados
        relatorio_df['id'] = f"{interval_from}_{interval_to}_{unit_id}"
        relatorio_df['unit_id'] = unit_id
        relatorio_df['periodo'] = periodo
        relatorio_df['timestamp_from'] = interval_from
        relatorio_df['timestamp_to'] = interval_to
        
        #print(f"✅ DataFrame criado com sucesso:")
        #print(relatorio_df)
        #print(f"Headers do DataFrame: {relatorio_df.columns.tolist()}")
        
        return relatorio_df
        
    except Exception as e:
        comm(f"❌ Erro inesperado ao processar unidade {unit_id}: {str(e)}")
        return None

def Colheitadeira_JSON_03(sid, flag, unit_id, tempo_dias, periodo, reportResourceId, reportTemplateId, reportObjectId, reportObjectSecId):
    """
    Função para coletar dados de relatório de uma unidade específica para um período.
    
    :param sid: Session ID da API Wialon
    :param unit_id: ID da unidade
    :param tempo_dias: Número de dias para buscar (7 ou 30)
    :param periodo: String descritiva do período
    :return: DataFrame com os dados ou None se não houver dados
    """
    nome = "Colheitadeira_JSON_03"
    def comm(msg):
        print(colored("="*30, "blue"))
        print(colored(f"{nome}:", "green"))
        print(f"{msg}")
        print(colored("="*30, "blue"))

    # CORREÇÃO: Calcula timestamps UNIX corretos
    current_time = int(time.time())
    interval_from = current_time - (tempo_dias * 24 * 3600)  # X dias atrás
    interval_to = current_time  # Agora
    
    try:
        # Executa o relatório
        relatorio = exec_report_03(sid=sid, flag=flag, dias=tempo_dias, reportResourceId=reportResourceId, reportTemplateId=reportTemplateId, reportObjectId=reportObjectId, reportObjectSecId=reportObjectSecId)

        if not relatorio:
            comm(f"❌ Falha ao executar relatório para unidade {unit_id}")
            return None

        # Verifica se há tabelas no resultado
        tables = relatorio.get('reportResult', {}).get('tables', [])
        if not tables:
            comm(f"⚠️ Nenhuma tabela encontrada no relatório para unidade {unit_id}")
            return None
        n_rows = relatorio.get('reportResult', {}).get('tables', [])
        n_rows = tables[0].get('rows', [])

        #---
        #print(f"n_rows: {n_rows}")
        #---

        
        # Extrai headers
        headers = extract_report_headers(relatorio)
        if not headers:
            comm(f"⚠️ Nenhum header encontrado no relatório para unidade {unit_id}")
            return None
        
        comm(f"Headers do relatório: {headers}")
        
        # Obtém as linhas de dados
        rows = select_result_rows(sid, table_index=0, index_from=0, index_to=n_rows, level=1)
        if not rows:
            comm(f"⚠️ Nenhuma linha de dados encontrada para unidade {unit_id}")
            return None

        comm(f"Linhas obtidas: {len(rows)}")

        #-----
        #print(f"Linhas obtidas: {rows}")
        #-----
        
        # Verifica se há dados
        if len(rows) == 0:
            comm(f"⚠️ Array de linhas vazio para unidade {unit_id}")
            return None
        
        # Processa todas as linhas de dados - apenas os dados dos headers
        data_rows = []
        for row in rows:
            if isinstance(row, dict) and 'c' in row:
                row_data = row['c']
                if row_data:  # Verifica se há dados na linha
                    # Cria dicionário apenas com os dados das colunas do relatório
                    row_dict = {}
                    for i, value in enumerate(row_data):
                        if i < len(headers):
                            row_dict[headers[i]] = value
                        else:
                            row_dict[f'coluna_{i}'] = value  # Para colunas extras
                    
                    data_rows.append(row_dict)
        
        if not data_rows:
            comm(f"⚠️ Nenhum dado válido encontrado para unidade {unit_id}")
            return None
        
        # Cria o DataFrame apenas com os dados dos headers
        relatorio_df = pd.DataFrame(data_rows)
        
        # Adiciona apenas os metadados essenciais do período (opcional)
        relatorio_df['unit_id'] = unit_id
        relatorio_df['periodo'] = periodo
        #---
        #comm(f"✅ DataFrame criado com sucesso com {len(relatorio_df)} linhas")
        #---
        comm(f"Colunas do DataFrame: {relatorio_df.columns.tolist()}")
        
        return relatorio_df
        
    except Exception as e:
        comm(f"❌ Erro inesperado ao processar unidade {unit_id}: {str(e)}")
        return None


def Colheitadeira_JSON_CP_01(sid, flag, unit_id, tempo_dias, periodo, reportResourceId, reportTemplateId, reportObjectId, reportObjectSecId):
    """
    Função para coletar dados de relatório de uma unidade específica para um período.
    
    :param sid: Session ID da API Wialon
    :param unit_id: ID da unidade
    :param tempo_dias: Número de dias para buscar (7 ou 30)
    :param periodo: String descritiva do período
    :return: DataFrame com os dados ou None se não houver dados
    """
    nome = "Colheitadeira_JSON_CP_01"
    def comm(msg):
        print(colored("="*30, "blue"))
        print(colored(f"{nome}:", "green"))
        print(f"{msg}")
        print(colored("="*30, "blue"))

    # CORREÇÃO: Calcula timestamps UNIX corretos
    current_time = int(time.time())
    interval_from = current_time - (tempo_dias * 24 * 3600)  # X dias atrás
    interval_to = current_time  # Agora
    
    try:
        # Executa o relatório
        relatorio = exec_report_03(sid=sid, flag=flag, dias=tempo_dias, reportResourceId=reportResourceId, reportTemplateId=reportTemplateId, reportObjectId=reportObjectId, reportObjectSecId=reportObjectSecId)

        comm(f"Relatório executado: {relatorio}")

        if not relatorio:
            comm(f"❌ Falha ao executar relatório para unidade {unit_id}")
            return None

        # Verifica se há tabelas no resultado
        tables = relatorio.get('reportResult', {}).get('tables', [])
        if not tables:
            comm(f"⚠️ Nenhuma tabela encontrada no relatório para unidade {unit_id}")
            return None
        n_rows = relatorio.get('reportResult', {}).get('tables', [])
        n_rows = tables[0].get('rows', [])

        # Extrai headers
        headers = extract_report_headers(relatorio)
        if not headers:
            comm(f"⚠️ Nenhum header encontrado no relatório para unidade {unit_id}")
            return None
        
        comm(f"Headers do relatório: {headers}")
        
        # Obtém as linhas de dados
        rows = select_result_rows(sid, table_index=0, index_from=0, index_to=n_rows, level=1)
        if not rows:
            comm(f"⚠️ Nenhuma linha de dados encontrada para unidade {unit_id}")
            return None

        comm(f"Linhas obtidas: {len(rows)}")

        # Verifica se há dados
        if len(rows) == 0:
            comm(f"⚠️ Array de linhas vazio para unidade {unit_id}")
            return None
        
        # Processa todas as linhas de dados - apenas os dados dos headers
        data_rows = []
        for row in rows:
            if isinstance(row, dict) and 'c' in row:
                row_data = row['c']

                if row_data:  # Verifica se há dados na linha
                    # Cria dicionário apenas com os dados das colunas do relatório
                    row_dict = {}
                    for i, value in enumerate(row_data):
                        if i < len(headers):
                            header_name = headers[i]
                            
                            # CORREÇÃO: Parse específico para campos de data/hora
                            if header_name == 'Hora de entrada' and isinstance(value, dict) and 't' in value:
                                row_dict[header_name] = value['t']  # Extrai apenas o timestamp
                            elif header_name == 'Hora de saída' and isinstance(value, dict) and 't' in value:
                                row_dict[header_name] = value['t']  # Extrai apenas o timestamp
                            else:
                                row_dict[header_name] = value
                        else:
                            row_dict[f'coluna_{i}'] = value  # Para colunas extras
                    
                    data_rows.append(row_dict)
        
        if not data_rows:
            comm(f"⚠️ Nenhum dado válido encontrado para unidade {unit_id}")
            return None
        
        # Cria o DataFrame apenas com os dados dos headers
        relatorio_df = pd.DataFrame(data_rows)
        
        # Adiciona apenas os metadados essenciais do período (opcional)
        relatorio_df['unit_id'] = unit_id
        relatorio_df['periodo'] = periodo
        
        comm(f"Colunas do DataFrame: {relatorio_df.columns.tolist()}")
        
        return relatorio_df
        
    except Exception as e:
        comm(f"❌ Erro inesperado ao processar unidade {unit_id}: {str(e)}")
        return None
#########################################################################################


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

def extract_report_data(data):
    """
    Extrai os dados do relatório Wialon.
    Retorna uma lista de listas (linhas) ou uma lista vazia se não encontrado.
    """
    try:
        tables = data.get('', [])
        if tables and isinstance(tables, list):
            rows = tables[0].get('rows', [])
            if isinstance(rows, list):
                return rows
    except Exception as e:
        print(f"Erro ao extrair dados do relatório: {e}")
    return []

def extract_report_data_simple(data):
    """
    Versão simplificada que extrai apenas os valores do campo 'c'.
    Retorna uma lista de listas com os valores das colunas.
    """
    try:
        extracted_data = []
        
        # Se data já é uma lista de rows
        if isinstance(data):
            for row in data:
                if isinstance(row, dict) and 'c' in row:
                    c_values = row.get('c', [])
                    if isinstance(c_values, list):
                        extracted_data.append(c_values)
        
        return extracted_data
        
    except Exception as e:
        print(f"Erro ao extrair dados simples do relatório: {e}")
        return []


#######################################################

def report_exec_report(sid, resource_id, template_id, unit_id, interval_from, interval_to):
    """
    Executa um relatório específico para uma unidade no Wialon.
    
    :param sid: Session ID obtido após o login.
    :param resource_id: ID do recurso onde o relatório está localizado.
    :param template_id: ID do modelo de relatório a ser executado.
    :param unit_id: ID da unidade para a qual o relatório será gerado.
    :return: Resultado do relatório ou None em caso de erro.
    """
    nome = "exec_report"
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
                "from": interval_from,
                "to": interval_to,
                "flags": 0  # CORREÇÃO: 0 para timestamps absolutos Unix
            }
        }),
        "sid": sid
    }
    
    try:
        
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        
        
        if "error" in data:
            error_code = data["error"]
            comm(f"Erro {error_code} ao executar relatório")
            
            # Códigos de erro comuns
            error_messages = {
                1: "Token inválido ou expirado",
                4: "Acesso negado - verificar permissões do usuário",
                5: "Erro na requisição - parâmetros inválidos (IDs ou interval)",
                6: "Não autorizado - usuário sem permissão para este relatório",
                7: "Failed to fetch the report object and report resource with the desired ACL",
                14: "Relatório não encontrado",
                1001: "Parâmetros inválidos",
                1002: "Recurso não encontrado",
                1003: "Template não encontrado"
            }
            
            if error_code in error_messages:
                comm(f"Descrição: {error_messages[error_code]}")
            
            return None
            
        # Verifica se o relatório foi executado com sucesso
        if isinstance(data, dict) and data.get("error") is None:
            comm(f"Relatório executado com sucesso")
            return data
            
        return data
        
    except requests.exceptions.RequestException as e:
        comm(f"Erro de conexão HTTP: {e}")
        return None
    except json.JSONDecodeError as e:
        comm(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        comm(f"Erro inesperado: {e}")
        return None
    





###### TESTE ##################################

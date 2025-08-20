from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade, Viagem_Base, Viagem_CAM, Caminhao
import json
import pandas as pd
import time
from termcolor import colored
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from tqdm import tqdm
import decimal



deposito = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"

WIALON_TOKEN_BRAS = "517e0e42b9a966f628a9b8cffff3ffc3F57FA748F075501F5667A26AFA278AC983E1C616"

WIALON_TOKEN_PLAC = "82fee29da11ea1312f1c8235247a0d82DC991707A4435C60FE7FFB27BD0D0F32BF59B709"

WIALON_TOKEN_SF = "5a35fb756820f83c975a1bc846a35a43C16F97789A714DEC2BC5F4D3C6D26C06CC35CAAD"

WIALON_TOKEN_UMBR = "fcc5baae18cdbea20200265b6b8a4af142DD8BF34CF94701039765308B2527031174B00A"


class Command(BaseCommand):
    help = 'Importa dados da API Wialon'
    def handle(self, *args, **kwargs):
        start_time = datetime.now()
        self.stdout.write(self.style.SUCCESS(f'Iniciando comando às {start_time.strftime("%H:%M:%S")}'))

        #self.principal(Empresa.objects.get(nome="CPBRACELL").token, "CPBRACELL")
        #self.principal(Empresa.objects.get(nome="PLACIDO").token, "PLACIDO")
        #self.principal(Empresa.objects.get(nome="São Francisco Resgate").token, "São Francisco Resgate")
        self.localizzare(WIALON_TOKEN_UMBR)


        end_time = datetime.now()
        execution_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f'Comando concluído às {end_time.strftime("%H:%M:%S")}'))
        self.stdout.write(self.style.SUCCESS(f'Tempo total de execução: {execution_time}'))


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
        
        # DEBUG: Analisar estrutura dos motoristas
        self.debug_driver_issues(sid, df_motoristas)
        
        # NOVA INVESTIGAÇÃO: Verificar se estamos interpretando os dados corretamente
        self.investigate_driver_data_structure(sid)
        
        #seleciona os 10 primeiros motoristas do dataframe
        df_motoristas = df_motoristas.head(3)  # Reduzido para 3 para debug
        for motorista in df_motoristas.itertuples(index=False):
            motorista_id = motorista.driver_id
            resource_id = motorista.resource_id  # ID do recurso que contém o motorista

            print(colored(f"\n🔍 DEBUGGING Motorista ID: {motorista_id}, Resource ID: {resource_id}", "cyan"))
            
            # Testar diferentes abordagens para resolver o erro 7
            success = self.test_driver_report_approaches(sid, 401756219, 5, motorista_id, resource_id)
            if not success:
                print(colored(f"❌ Todas as abordagens falharam para motorista {motorista_id}", "red"))
            
            Wialon.clean_up_result(sid)





        Wialon.wialon_logout(sid)

    def exec_report_driver_fixed(self, sid, resource_id, template_id, driver_id, driver_resource_id, interval_from=None, interval_to=None, tempo_dias=1, periodo="teste"):
        """
        Executa um relatório específico para um motorista no Wialon (VERSÃO CORRIGIDA).
        
        :param sid: Session ID obtido após o login.
        :param resource_id: ID do recurso onde o relatório está localizado.
        :param template_id: ID do modelo de relatório a ser executado.
        :param driver_id: ID do motorista para o qual o relatório será gerado.
        :param driver_resource_id: ID do recurso que contém o motorista.
        :param tempo_dias: Número de dias para buscar (se interval_from/to não fornecidos).
        :return: Resultado do relatório ou None em caso de erro.
        """
        import requests
        
        # Calcula timestamps se não fornecidos
        if interval_from is None or interval_to is None:
            current_time = int(time.time())
            interval_from = current_time - (tempo_dias * 24 * 3600)
            interval_to = current_time
        
        payload = {
            "svc": "report/exec_report",
            "params": json.dumps({
                "reportResourceId": resource_id,
                "reportTemplateId": template_id,
                "reportObjectId": driver_id,          # ID do motorista
                "reportObjectSecId": driver_resource_id,  # CORREÇÃO: ID do recurso que contém o motorista
                "interval": {
                    "from": interval_from,
                    "to": interval_to,
                    "flags": 0
                }
            }),
            "sid": sid
        }
        
        try:
            print(colored(f"Executando relatório para motorista {driver_id} do recurso {driver_resource_id}", "yellow"))
            
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                error_code = data["error"]
                print(colored(f"Erro {error_code} ao executar relatório para motorista", "red"))
                
                error_messages = {
                    1: "Token inválido ou expirado",
                    4: "Acesso negado - verificar permissões do usuário",
                    5: "Erro na requisição - parâmetros inválidos",
                    6: "Não autorizado - usuário sem permissão para este relatório",
                    7: "Failed to fetch the report object and report resource with the desired ACL",
                    14: "Relatório não encontrado"
                }
                
                if error_code in error_messages:
                    print(colored(f"Descrição: {error_messages[error_code]}", "red"))
                
                return None
                
            print(colored(f"Relatório executado com sucesso para motorista {driver_id}", "green"))
            return data
            
        except Exception as e:
            print(colored(f"Erro inesperado: {e}", "red"))
            return None

    def debug_driver_issues(self, sid, df_motoristas):
        """Debug para investigar problemas com motoristas."""
        print(colored("="*50, "magenta"))
        print(colored("🔍 DEBUG: Investigando estrutura dos motoristas", "magenta"))
        print(colored("="*50, "magenta"))
        
        # Verificar templates de relatório disponíveis
        self.check_report_templates(sid, 401756219)
        
        if len(df_motoristas) > 0:
            first_driver = df_motoristas.iloc[0]
            print(f"Primeiro motorista:")
            print(f"  - driver_id: {first_driver.get('driver_id', 'N/A')}")
            print(f"  - resource_id: {first_driver.get('resource_id', 'N/A')}")
            print(f"  - driver_name: {first_driver.get('driver_name', 'N/A')}")
            print(f"  - resource_name: {first_driver.get('resource_name', 'N/A')}")
            
            # Verificar se o recurso realmente existe
            resource_id = first_driver.get('resource_id')
            if resource_id:
                #self.verify_resource_exists(sid, resource_id)
                pass

    def check_report_templates(self, sid, resource_id):
        """Verifica quais templates de relatório estão disponíveis."""
        print(colored(f"\n🔍 Verificando templates no recurso {resource_id}...", "yellow"))
        
        payload = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": resource_id,
                "flags": 8193  # flags para obter templates de relatório
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(colored(f"❌ Erro ao buscar templates: {result['error']}", "red"))
                return
            
            item = result.get("item", {})
            reports = item.get("rep", {})
            
            print(f"Templates encontrados: {len(reports)}")
            for template_id, template_data in reports.items():
                template_name = template_data.get("n", "Sem nome")
                print(f"  - ID: {template_id}, Nome: {template_name}")
                
                # Verificar se o template é específico para motoristas
                if any(keyword in template_name.lower() for keyword in ['motorista', 'driver', 'condutor']):
                    print(colored(f"    ✅ Template parece ser para motoristas", "green"))
                else:
                    print(colored(f"    ⚠️  Template pode não ser específico para motoristas", "yellow"))
                    
        except Exception as e:
            print(colored(f"❌ Erro na verificação de templates: {e}", "red"))

    def investigate_driver_data_structure(self, sid):
        """Investigação profunda da estrutura de dados dos motoristas."""
        print(colored("="*50, "blue"))
        print(colored("🔬 INVESTIGAÇÃO: Estrutura real dos dados de motoristas", "blue"))
        print(colored("="*50, "blue"))
        
        # Buscar recursos com motoristas diretamente
        params = {
            "svc": "core/search_items",
            "params": json.dumps({
                "spec": {
                    "itemsType": "avl_resource",
                    "propName": "sys_name",
                    "propValueMask": "*",
                    "sortType": "sys_name"
                },
                "force": 1,
                "flags": 257,  # 1 (basic info) + 256 (drivers info)
                "from": 0,
                "to": 3  # Apenas 3 recursos para análise
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=params)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(colored(f"❌ Erro na busca: {result['error']}", "red"))
                return
            
            resources = result.get("items", [])
            
            for resource in resources:
                resource_id = resource.get("id", 0)
                resource_name = resource.get("nm", "Sem nome")
                drivers_dict = resource.get("drvrs", {})
                
                print(colored(f"\n📁 Recurso: {resource_name} (ID: {resource_id})", "cyan"))
                print(f"   Estrutura do campo 'drvrs': {type(drivers_dict)}")
                
                if drivers_dict:
                    print(f"   Número de motoristas: {len(drivers_dict)}")
                    print(f"   Chaves dos motoristas: {list(drivers_dict.keys())}")
                    
                    # Analisar o primeiro motorista
                    first_key = list(drivers_dict.keys())[0]
                    first_driver = drivers_dict[first_key]
                    
                    print(f"\n   📋 Primeiro motorista (chave: {first_key}):")
                    print(f"      Estrutura: {type(first_driver)}")
                    print(f"      Campos disponíveis: {list(first_driver.keys()) if isinstance(first_driver, dict) else 'N/A'}")
                    
                    if isinstance(first_driver, dict):
                        driver_id = first_driver.get("id", "N/A")
                        driver_name = first_driver.get("n", "N/A")
                        print(f"      ID do motorista: {driver_id}")
                        print(f"      Nome do motorista: {driver_name}")
                        
                        # TESTE CRUCIAL: Verificar se este ID de motorista é válido
                        print(colored(f"\n   🧪 TESTE: Verificando se motorista ID {driver_id} é acessível...", "yellow"))
                        self.test_driver_accessibility(sid, driver_id, resource_id)
                        
                else:
                    print("   ⚠️  Nenhum motorista encontrado")
                    
        except Exception as e:
            print(colored(f"❌ Erro na investigação: {e}", "red"))

    def test_driver_accessibility(self, sid, driver_id, resource_id):
        """Testa se um motorista específico é acessível via API."""
        # Tentar buscar o motorista como item individual
        payload = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": driver_id,
                "flags": 1  # basic info
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" not in result and result.get("item"):
                item = result["item"]
                print(colored(f"      ✅ Motorista encontrado como item independente!", "green"))
                print(f"         Classe: {item.get('cls', 'N/A')}")
                print(f"         Nome: {item.get('nm', 'N/A')}")
                print(f"         Tipo: {self.get_item_type_name(item.get('cls', 0))}")
                
                # Se encontrou como item, pode ser que precise de abordagem diferente
                if item.get('cls') == 2:  # avl_unit
                    print(colored(f"      💡 DESCOBERTA: Este 'motorista' é na verdade uma UNIDADE!", "yellow"))
                    print(f"      💡 Tente usar reportObjectSecId = 0 para este item")
                    
            else:
                error_code = result.get("error", "desconhecido")
                print(colored(f"      ❌ Motorista não acessível como item individual (erro: {error_code})", "red"))
                print(f"      💡 Confirma que deve ser acessado via recurso {resource_id}")
                
        except Exception as e:
            print(colored(f"      ❌ Erro ao testar acessibilidade: {e}", "red"))

    def get_item_type_name(self, cls):
        """Retorna o nome do tipo de item baseado na classe."""
        types = {
            1: "avl_user",
            2: "avl_unit", 
            3: "avl_unit_group",
            4: "avl_retranslator",
            5: "avl_route",
            6: "avl_resource"
        }
        return types.get(cls, f"unknown_type_{cls}")

    def verify_resource_exists(self, sid, resource_id):
        """Verifica se um recurso específico existe e tem permissão."""
        print(colored(f"\n🔍 Verificando recurso {resource_id}...", "yellow"))
        
        payload = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": resource_id,
                "flags": 257  # 1 (basic info) + 256 (drivers info)
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(colored(f"❌ Erro ao acessar recurso {resource_id}: {result['error']}", "red"))
                return False
            
            item = result.get("item", {})
            if item:
                print(colored(f"✅ Recurso encontrado: {item.get('nm', 'Sem nome')}", "green"))
                drivers = item.get('drvrs', {})
                print(f"   Motoristas no recurso: {len(drivers)}")
                return True
            else:
                print(colored(f"❌ Recurso {resource_id} não encontrado", "red"))
                return False
                
        except Exception as e:
            print(colored(f"❌ Erro na verificação: {e}", "red"))
            return False

    def test_driver_report_approaches(self, sid, resource_id, template_id, driver_id, driver_resource_id):
        """Testa diferentes abordagens para executar relatório de motorista."""
        print(colored(f"\n🧪 Testando diferentes abordagens...", "cyan"))
        
        current_time = int(time.time())
        interval_from = current_time - (24 * 3600)
        interval_to = current_time
        
        # Abordagem 1: reportObjectSecId = driver_resource_id (nossa correção)
        print(colored("1️⃣ Testando com reportObjectSecId = driver_resource_id", "yellow"))
        if self.test_single_approach(sid, resource_id, template_id, driver_id, driver_resource_id, interval_from, interval_to):
            return True
            
        # Abordagem 2: reportObjectSecId = 0 (como unidades)
        print(colored("2️⃣ Testando com reportObjectSecId = 0", "yellow"))
        if self.test_single_approach(sid, resource_id, template_id, driver_id, 0, interval_from, interval_to):
            return True
            
        # Abordagem 3: reportObjectSecId = resource_id do template
        print(colored("3️⃣ Testando com reportObjectSecId = resource_id do template", "yellow"))
        if self.test_single_approach(sid, resource_id, template_id, driver_id, resource_id, interval_from, interval_to):
            return True
            
        # Abordagem 4: Tentar como se fosse unidade (pode ser que o motorista esteja registrado como unidade)
        print(colored("4️⃣ Testando como se fosse unidade...", "yellow"))
        if self.test_as_unit(sid, resource_id, template_id, driver_id, interval_from, interval_to):
            return True
            
        return False

    def test_single_approach(self, sid, resource_id, template_id, driver_id, sec_id, interval_from, interval_to):
        """Testa uma abordagem específica."""
        payload = {
            "svc": "report/exec_report",
            "params": json.dumps({
                "reportResourceId": resource_id,
                "reportTemplateId": template_id,
                "reportObjectId": driver_id,
                "reportObjectSecId": sec_id,
                "interval": {
                    "from": interval_from,
                    "to": interval_to,
                    "flags": 0
                }
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            data = response.json()
            
            if "error" not in data:
                print(colored(f"   ✅ SUCESSO com reportObjectSecId = {sec_id}!", "green"))
                return True
            else:
                error_code = data["error"]
                print(colored(f"   ❌ Erro {error_code} com reportObjectSecId = {sec_id}", "red"))
                return False
                
        except Exception as e:
            print(colored(f"   ❌ Exceção: {e}", "red"))
            return False

    def test_as_unit(self, sid, resource_id, template_id, driver_id, interval_from, interval_to):
        """Testa executar relatório como se o motorista fosse uma unidade."""
        # Primeiro verifica se existe uma unidade com esse ID
        payload = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": driver_id,
                "flags": 1  # basic info
            }),
            "sid": sid
        }
        
        try:
            response = requests.post("https://hst-api.wialon.com/wialon/ajax.html", data=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" not in result and result.get("item"):
                item = result["item"]
                item_type = item.get("cls", 0)
                print(f"   Item encontrado - Tipo: {item_type}, Nome: {item.get('nm', 'Sem nome')}")
                
                # Se for uma unidade (cls = 2), tenta executar como unidade
                if item_type == 2:  # avl_unit
                    print(colored("   Tentando como unidade...", "cyan"))
                    return self.test_single_approach(sid, resource_id, template_id, driver_id, 0, interval_from, interval_to)
            
            return False
            
        except Exception as e:
            print(colored(f"   ❌ Erro ao verificar como unidade: {e}", "red"))
            return False

        #######################################################################################

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

            print(f'Unidade: {placa} | ID: {unidade_id} | Restante do nome: {restante_nome} | Marca: {marca} | Classe: {cls} | Empresa: {empresa.nome}')

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

    def teste_processamento(self, sid):
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        if unidades_db_ids:
            unidades_db = unidades_db.filter(empresa__nome='CPBRASCELL')
            unidades_db = unidades_db.filter(cls__icontains='Veículo')  # Filtra por classe que contém "Veículo"
        unidade_id = unidades_db_ids
        unit_id_first = unidade_id[0] if unidade_id else None



        relatorio = Wialon.Colheitadeira_JSON_m(sid, 401756219, unit_id_first, unidade_id, 59, tempo_dias=1, periodo='Ontem')
        print(f'Relatório coletado: {relatorio}')



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


 

    def update_or_create_trip(self, processamento_df):
        if not processamento_df.empty:
            for index, row in processamento_df.iterrows():
                try:
                    unidade_instance = Unidade.objects.get(nm=row['Grouping'])
                    
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
                        km_media_value = float(km_media)
                        velocidade_media_value = float(velocidade_media)
                        rpm_medio_value = float(rpm_medio)
                        temperatura_media_value = float(temperatura_media)
                        co2_value = float(co2)
                    except (ValueError, TypeError):
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
                    self.stdout.write(self.style.SUCCESS(f'Viagem atualizada ou criada para a unidade {row["Grouping"]} no período {row["periodo"]} com quilometragem {quilometragem_value}'))
                
                except Unidade.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Unidade com nome "{row["Grouping"]}" não encontrada no banco de dados.'))
                    continue

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

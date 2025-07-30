from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade
import json
import pandas as pd
import time


deposito = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"




class Command(BaseCommand):
    help = 'Importa dados da API Wialon'

    def handle(self, *args, **options):
###############################################################        
        # Autentica na API Wialon
        sid = Wialon.authenticate_with_wialon()

###############################################################

###############################################################
        # Recupera a lista de unidades
        self.stdout.write(self.style.SUCCESS('Recuperando unidades...'))
        unidades = self.coletar_unidades(sid)
        if not unidades:
            self.stdout.write(self.style.WARNING("Nenhuma unidade encontrada."))
            return
        self.stdout.write(self.style.SUCCESS('Unidades recuperadas com sucesso.'))
        print(unidades)



###############################################################
        # Recupera a lista de motoristas
        self.stdout.write(self.style.SUCCESS('Recuperando motoristas...'))
        motoristas = self.coletar_motoristas_1(sid)

        # Verifica se motoristas foram encontrados
        if not motoristas:
            self.stdout.write(self.style.WARNING("Nenhum motorista encontrado."))

            return
        self.stdout.write(self.style.SUCCESS('Motoristas recuperados com sucesso.'))



###############################################################
# busca os relatorios
        self.stdout.write(self.style.SUCCESS('Buscando relatórios de viagens...'))
        relatorios = Wialon.buscadora_reports(sid)

        # Trata os dados para mostrar em dicionario
        relatorios = json.dumps(relatorios, indent=2, ensure_ascii=False)
        # Salva o arquivo json no deposito
        with open(f"{deposito}/relatorios.json", "w", encoding="utf-8") as f:
            f.write(relatorios)

        # Verifica se relatorios foram encontrados
        if not relatorios:
            self.stdout.write(self.style.WARNING("Nenhum relatório encontrado."))
            return
        self.stdout.write(self.style.SUCCESS('Relatórios recuperados com sucesso.'))

###############################################
# executa o relatorio para cada unidade



###############################################################
        # Lê o deposito para obter o número de caminhões 
        unidades_data = self.read_unidades_json()
        #transforma unidades_data em um dataframe Pandas
        unidades_data = pd.DataFrame.from_records(unidades_data)
        print(unidades_data)
        #cria uma lista com os IDs das unidades
        unidades_ids = unidades_data['id'].tolist()
        self.stdout.write(self.style.SUCCESS(f"IDs das unidades: {unidades_ids}"))

        # salva o pandas dataframe em um arquivo excel
        unidades_data.to_excel(f"{deposito}/unidades.xlsx", index=False, engine='openpyxl')
        self.stdout.write(self.style.SUCCESS('Unidades salvas em Excel com sucesso.'))

        #separa as colunas de id e nome
        unidades_data = unidades_data[['id', 'nm']]
        #adiciona uma coluna de empresa com o nome da empresa
        unidades_data['empresa'] = 'CPBrascell'
        #checa se a coluna 'nm' possui o valor 'Scania', se sim, substitui

        #adiciona uma coluna de descricao com o nome da unidade
        unidades_data['descricao'] = 'Volvo'
        #checa se a coluna 'nm' possui o valor 'Scania', se sim, substitui a descricao por 'Scania'
        unidades_data.loc[unidades_data['nm'].str.contains('Scania', case=False), 'descricao'] = 'Scania'
        #adiciona uma coluna de cls com o nome da classe
        unidades_data['cls'] = 'Caminhão'
        print(unidades_data)






        # Lê o deposito para obter o número de motoristas
        motoristas_data = self.read_motoristas_json()
        motoristas_data = pd.DataFrame.from_records(motoristas_data)
        print(motoristas_data)
        # cria uma lista com os IDs dos motoristas
        motoristas_ids = motoristas_data['driver_id'].tolist()
        self.stdout.write(self.style.SUCCESS(f"IDs dos motoristas: {motoristas_ids}"))
        # salva o pandas dataframe em um arquivo excel
        motoristas_data.to_excel(f"{deposito}/motoristas.xlsx", index=False, engine='openpyxl')
        self.stdout.write(self.style.SUCCESS('Motoristas salvos em Excel com sucesso.'))

        #separa as colunas de id e nome
        motoristas_data = motoristas_data[['driver_id', 'nome', 'resource_name', 'descricao']]
        #renomeia as colunas
        motoristas_data.rename(columns={
            'driver_id': 'id',
            'nome': 'nm',
            'resource_name': 'empresa',
            'descricao': 'descricao'
        }, inplace=True)
        #adiciona uma coluna de cls com o nome da classe
        motoristas_data['cls'] = 'Motorista'
        print(motoristas_data)





        # Conta o número de caminhões e motoristas
        qtd_caminhoes = len(unidades_data)
        qtd_motoristas = len(motoristas_data)

        self.stdout.write(self.style.SUCCESS(f"Número de caminhões: {qtd_caminhoes}"))

########################################################################

        #recupera um relatorio para teste
        unidade_aleatoria = unidades_ids[10]  # Seleciona a décima unidade para teste

        relatorio = Wialon.Colheitadeira_JSON(sid, unidade_aleatoria, id_relatorio=59, tempo_dias=7, periodo='7 dias')
        print(f"Relatório para a unidade {unidade_aleatoria}:")
        print(relatorio)

        #importa do relatorio para o model Viagem_Unidade
        for index, row in relatorio.iterrows():
            viagem_unidade, created = Viagem_Unidade.objects.update_or_create(
                id=row['id'],
                defaults={
                    'periodo': row['periodo'],
                    'quilometragem': row['km'],
                    'consumido': row['consumed'],
                    'quilometragem_media': row['km_avg'],
                    'horas_motor': row['engine_hours'],
                    'velocidade_media': row['speed_avg'],
                    'rpm_medio': row['rpm_avg'],
                    'temperatura_media': row['temp_avg'],
                    'emissoes_co2': row['co2_emissions']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Viagem Unidade {viagem_unidade.id} criada."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Viagem Unidade {viagem_unidade.id} atualizada."))







############################################################################################

        # Atualizar ou criar empresa CPBrascell com o número de caminhões
        #self.update_or_create_empresa_cpbrascell(qtd_caminhoes, qtd_motoristas)
############################################################################################

        #concatena os dados dos motoristas e unidades
        units_data = pd.concat([unidades_data, motoristas_data], ignore_index=True)
        print(units_data)

        #atualizar o model Unidades
        self.update_or_create_unidades(units_data)
    





##################################################################

        # Faz logout da sessão Wialon
        self.stdout.write(self.style.SUCCESS('Deslogando da API Wialon...'))
        Wialon.wialon_logout(sid)







    def coletar_motoristas_1(self, sid):
        motoristas = Wialon.motoristas_simples(sid)
        motoristas = json.dumps(motoristas, indent=2, ensure_ascii=False)
        #with open(f"{deposito}/motoristas.json", "w", encoding="utf-8") as f:
            #f.write(motoristas)
        return motoristas
    
    def coletar_motoristas_2(self, sid):
        #recupera os motoristas
        motoristas = Wialon.motoristas_simples(sid)
        motoristas = json.dumps(motoristas, indent=2, ensure_ascii=False)
        with open(f"{deposito}/motoristas.json", "w", encoding="utf-8") as f:
            f.write(motoristas)
        return motoristas
    
    

    def coletar_unidades(self, sid):
        unidades = Wialon.unidades_simples(sid)
        unidades = json.dumps(unidades, indent=2, ensure_ascii=False)
        #with open(f"{deposito}/unidades.json", "w", encoding="utf-8") as f:
            #f.write(unidades)

        return unidades



###################################################################







    def update_or_create_empresa_cpbrascell(self, qtd_caminhoes, qtd_motoristas):
        empresa, created = Empresa.objects.update_or_create(
            nome="CPBrascell",
            defaults={"qtd_caminhoes": qtd_caminhoes, "qtd_motoristas": qtd_motoristas}
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Empresa CPBrascell criada com {qtd_caminhoes} caminhões.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Empresa CPBrascell atualizada com {qtd_caminhoes} caminhões e {qtd_motoristas} motoristas.")
            )

    def update_or_create_unidades(self, unidades_data):
        for index, row in unidades_data.iterrows():
            unidade, created = Unidade.objects.update_or_create(
                id=row['id'],
                defaults={
                    "nm": row['nm'],
                    "cls": row['cls'],
                    "empresa": row['empresa'],
                    "descricao": row['descricao']
                }
            )


    def read_motoristas_json(self):
        """
        Lê o arquivo motoristas.json e extrai informações dos motoristas dentro de drvrs.
        Retorna uma lista de dicionários com id, nome (n), código (c) e descrição (ds).
        """
        with open(f"{deposito}/motoristas.json", "r", encoding="utf-8") as f:
            motoristas_data = json.load(f)
        
        motoristas_extraidos = []
        
        # Verifica se existe a estrutura "items" no JSON
        if "items" in motoristas_data:
            for resource in motoristas_data["items"]:
                resource_name = resource.get("nm", "Recurso sem nome")
                resource_id = resource.get("id", 0)
                
                # Extrai motoristas do campo "drvrs"
                drivers = resource.get("drvrs", {})
                
                for driver_key, driver_data in drivers.items():
                    motorista_info = {
                        "resource_id": resource_id,
                        "resource_name": resource_name,
                        "driver_id": driver_data.get("id", 0),
                        "nome": driver_data.get("n", "Nome não disponível"),
                        "codigo": driver_data.get("c", ""),
                        "descricao": driver_data.get("ds", "")
                    }
                    motoristas_extraidos.append(motorista_info)
        
        return motoristas_extraidos

    def read_unidades_json(self):
        with open(f"{deposito}/unidades.json", "r", encoding="utf-8") as f:
            unidades_data = json.load(f)
        return unidades_data

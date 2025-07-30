import os
from django.core.management.base import BaseCommand
import Wialon
from Wialon import WIALON_TOKEN
import json
import pandas as pd
import time
import random
from tqdm import tqdm 




deposito = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"
deposito_relatorios = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\relatorios"
dep_59_07 = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito\relatorios\59\7"
dep_59_30 = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito\relatorios\59\30"


def Colheitadeira_JSON(sid, unit_id, id_relatorio, tempo_dias):
    """
    Função para coletar dados de relatório de uma unidade específica para um período.
    
    :param sid: Session ID da API Wialon
    :param unit_id: ID da unidade
    :param armazenamento: Pasta onde salvar os dados
    :param id_relatorio: ID do template de relatório
    :param tempo_dias: Número de dias para buscar (7 ou 30)
    """

    # CORREÇÃO: Calcula timestamps corretos
    current_time = int(time.time())
    interval_from = current_time - (tempo_dias * 24 * 3600)  # X dias atrás
    interval_to = current_time  # Agora
    

#############################################################################

    Wialon.exec_report(sid=sid, resource_id=401756219, template_id=id_relatorio, unit_id=unit_id, interval_from=interval_from, interval_to=interval_to)
    rows = Wialon.get_result_rows(sid)
    if rows:
        print(f"Relatório para a unidade {unit_id}: RECUPERADO")
        #print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    else:
        print(f"Falha ao gerar relatório para a unidade {unit_id}.")
    # achata o dicionário de linhas
    flattened_rows = [Wialon.flatten_dict(row) for row in rows if isinstance(row, dict)]







    # Limpa o relatório da memória
    Wialon.clean_up_result(sid)
    return flattened_rows


    #Executa o relatorio para cada unidade
    







################################################################################################




if __name__ == "__main__":

    sid = Wialon.authenticate_with_wialon()
    if not sid:
        print("Falha na autenticação.")
        exit()

    ##### Coleta unidades
    print("Coletando unidades...")
    unidades = Wialon.search_units(sid)
    if not unidades:
        print("Nenhuma unidade encontrada.")
        exit()

    # Converte unidades para DataFrame
    unidades_df = pd.DataFrame([Wialon.flatten_dict(unit) for unit in unidades])
    print("Unidades encontradas:")
    print(unidades_df)

    #lista os IDs das unidades
    unidades_ids = unidades_df['id'].tolist()


    unidades_ids = unidades_ids[:10]  # Pega as 10 primeiras unidades para teste

    #cria um dataframe 
    relatorio = pd.DataFrame()


    ### Coleta dados da colheitadeira
    for unidade in tqdm(unidades_ids, desc="Coletando dados das unidades"):
        rows = Colheitadeira_JSON(sid, unidade, id_relatorio=59, tempo_dias=7)
        print(rows)

    Wialon.wialon_logout(sid)
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


def Colheitadeira_JSON(sid, unit_id, armazenamento, id_relatorio, tempo_dias):
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

    relatorio = Wialon.exec_report(sid=sid, resource_id=401756219, template_id=id_relatorio, unit_id=unit_id, interval_from=interval_from, interval_to=interval_to)
    if relatorio:
        print(f"Relatório para a unidade {unit_id}: RECUPERADO")
        #print(json.dumps(relatorio, indent=2, ensure_ascii=False))

    else:
        print(f"Falha ao gerar relatório para a unidade {unidade_aleatoria}.")

    rows = Wialon.get_result_rows(sid)
    print(rows)
    
    save_report_rows_to_json(unit_id, armazenamento, rows)


    # Limpa o relatório da memória
    Wialon.clean_up_result(sid)

    #Executa o relatorio para cada unidade
    







def print_report_headers(relatorio):
    print("3. Obtendo dados do relatório...")
    #imprime os headers do relatorio
    report_result = relatorio.get("reportResult", {})
    tables = report_result.get("tables", [])
    primeira_tabela = tables[0]
    headers = primeira_tabela.get("header", [])
    print("   Headers do relatório:")
    print(headers)






def create_report_dataframe(unit_id, tempo_dias, headers, rows):
    relatorio_df = pd.DataFrame(rows, columns=headers)
    print("   DataFrame do relatório:")
    print(relatorio_df)
    #concatena os os rows da unidade ao relatorio
    relatorio_df['unit_id'] = unit_id
    relatorio_df['tempo'] = tempo_dias
    print("   DataFrame do relatório com unit_id:")
    print(relatorio_df)

def save_report_rows_to_json(unit_id, armazenamento, rows):
    if rows:
        #print(f"   ✅ Obtidas {len(rows)} linhas")
        # Salva apenas as linhas na

        filename = f"{armazenamento}/{unit_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        #print(f"   📁 Linhas salvas em: {filename}")
    else:
        print("   ❌ Falha ao obter linhas do relatório")






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
    print("IDs das unidades:")
    print(unidades_ids)

    #seleciona uma unidade aleatoriamente
    unidade_aleatoria = random.choice(unidades_ids)
    print("Unidade selecionada aleatoriamente:")
    print(unidade_aleatoria)
    unit_id = unidade_aleatoria

    ### Coleta dados da colheitadeira
    Colheitadeira_JSON(sid, unit_id, dep_59_07, id_relatorio=59, tempo_dias=7)
    Colheitadeira_JSON(sid, unit_id, dep_59_30, id_relatorio=59, tempo_dias=30)


    Wialon.wialon_logout(sid)
import os
import glob
from pathlib import Path
import json
import pandas as pd


def ler_jsons_pasta_para_dataframe(caminho_pasta, incluir_metadados=True):
    """
    Lê todos os arquivos JSON de uma pasta e consolida em um DataFrame.
    
    :param caminho_pasta: Caminho da pasta com arquivos JSON
    :param incluir_metadados: Se True, inclui informações do arquivo como colunas
    :return: DataFrame consolidado ou None se não encontrar arquivos
    """
    print(f"\n=== LENDO JSONs DA PASTA ===")
    print(f"Pasta: {caminho_pasta}")
    
    # Verifica se a pasta existe
    if not os.path.exists(caminho_pasta):
        print(f"❌ Pasta não encontrada: {caminho_pasta}")
        return None
    
    # Busca todos os arquivos JSON na pasta
    arquivos_json = glob.glob(os.path.join(caminho_pasta, "*.json"))
    
    if not arquivos_json:
        print(f"❌ Nenhum arquivo JSON encontrado na pasta")
        return None
    
    print(f"✅ Encontrados {len(arquivos_json)} arquivos JSON")
    
    # Lista para armazenar os DataFrames de cada arquivo
    dataframes = []
    
    # Define os headers baseados na estrutura conhecida
    headers = [
        "Grouping",
        "Quilometragem", 
        "Consumido por AbsFCS",
        "Quilometragem média por unidade de combustível por AbsFCS",
        "Horas de motor",
        "Velocidade média", 
        "RPM médio do motor",
        "Temperatura média",
        "Emissões de CO2"
    ]
    
    for arquivo_json in arquivos_json:
        try:
            print(f"📄 Processando: {os.path.basename(arquivo_json)}")
            
            # Lê o arquivo JSON
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
            
            # Verifica se há dados
            if not dados_json:
                print(f"   ⚠️ Arquivo vazio: {arquivo_json}")
                continue
            
            # Processa cada registro no JSON
            for registro in dados_json:
                # Extrai os dados da coluna 'c' (dados principais)
                dados_linha = registro.get('c', [])
                
                if not dados_linha:
                    print(f"   ⚠️ Nenhum dado encontrado no registro")
                    continue
                
                # Cria um dicionário com os dados
                linha_dados = {}
                
                # Preenche com os dados principais
                for i, header in enumerate(headers):
                    if i < len(dados_linha):
                        linha_dados[header] = dados_linha[i]
                    else:
                        linha_dados[header] = None
                
                # Adiciona metadados se solicitado
                if incluir_metadados:
                    # Extrai ID da unidade do nome do arquivo
                    nome_arquivo = os.path.basename(arquivo_json)
                    unit_id = os.path.splitext(nome_arquivo)[0]
                    
                    linha_dados['unit_id'] = unit_id
                    linha_dados['arquivo_origem'] = nome_arquivo
                    linha_dados['n'] = registro.get('n', None)
                    linha_dados['i1'] = registro.get('i1', None)
                    linha_dados['i2'] = registro.get('i2', None)
                    linha_dados['t1'] = registro.get('t1', None)
                    linha_dados['t2'] = registro.get('t2', None)
                    linha_dados['d'] = registro.get('d', None)
                    linha_dados['mrk'] = registro.get('mrk', None)
                
                # Adiciona à lista de DataFrames
                df_linha = pd.DataFrame([linha_dados])
                dataframes.append(df_linha)
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {arquivo_json}: {e}")
            continue
    
    # Consolida todos os DataFrames
    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
        
        # Otimiza os tipos de dados
        df_consolidado = limpar_e_otimizar_dados(df_consolidado)
        
        print(f"\n✅ DataFrame consolidado criado!")
        print(f"📊 Shape: {df_consolidado.shape}")
        print(f"📋 Colunas: {list(df_consolidado.columns)}")
        
        return df_consolidado
    else:
        print("❌ Nenhum dado válido encontrado nos arquivos")
        return None


def limpar_e_otimizar_dados(df):
    """
    Limpa e otimiza os tipos de dados do DataFrame.
    
    :param df: DataFrame a ser otimizado
    :return: DataFrame otimizado
    """
    print("🔧 Otimizando tipos de dados...")
    
    # Colunas que devem ser numéricas
    colunas_numericas = [
        "Quilometragem",
        "Consumido por AbsFCS", 
        "Quilometragem média por unidade de combustível por AbsFCS",
        "Velocidade média",
        "RPM médio do motor",
        "Temperatura média",
        "Emissões de CO2"
    ]
    
    for coluna in colunas_numericas:
        if coluna in df.columns:
            # Remove unidades e texto
            df[coluna] = df[coluna].astype(str).str.replace(r'[^\d.,\-]', '', regex=True)
            # Substitui vírgula por ponto
            df[coluna] = df[coluna].str.replace(',', '.')
            # Converte para numérico
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
    
    # Processa coluna "Horas de motor" (formato especial)
    if "Horas de motor" in df.columns:
        df['Horas de motor (texto)'] = df["Horas de motor"]  # Mantém original
        # Converte para horas decimais
        df['Horas de motor (decimal)'] = df["Horas de motor"].apply(converter_tempo_para_horas)
    
    # Converte timestamps
    if 't1' in df.columns:
        df['timestamp_inicio'] = pd.to_datetime(df['t1'], unit='s', errors='coerce')
    if 't2' in df.columns:
        df['timestamp_fim'] = pd.to_datetime(df['t2'], unit='s', errors='coerce')
    
    print("✅ Otimização concluída")
    return df


def converter_tempo_para_horas(tempo_str):
    """
    Converte string de tempo como "2 days 22:52:37" para horas decimais.
    
    :param tempo_str: String de tempo
    :return: Horas em decimal ou None
    """
    try:
        if pd.isna(tempo_str) or tempo_str == '':
            return None
        
        tempo_str = str(tempo_str).strip()
        horas_total = 0
        
        # Procura por dias
        if 'day' in tempo_str:
            partes = tempo_str.split('day')
            dias = int(partes[0].strip())
            horas_total += dias * 24
            tempo_str = partes[1].strip()
            if tempo_str.startswith('s'):
                tempo_str = tempo_str[1:].strip()
        
        # Processa o restante (formato HH:MM:SS)
        if ':' in tempo_str:
            partes_tempo = tempo_str.split(':')
            if len(partes_tempo) >= 2:
                horas_total += int(partes_tempo[0])
                horas_total += int(partes_tempo[1]) / 60
                if len(partes_tempo) >= 3:
                    horas_total += int(partes_tempo[2]) / 3600
        
        return horas_total
    except:
        return None


def salvar_dataframe_consolidado(df, pasta_origem, nome_arquivo="dados_consolidados"):
    """
    Salva o DataFrame consolidado em diferentes formatos.
    
    :param df: DataFrame a ser salvo
    :param pasta_origem: Pasta onde os dados foram coletados
    :param nome_arquivo: Nome base para os arquivos
    """
    if df is None or df.empty:
        print("❌ DataFrame vazio, não será salvo")
        return
    
    # Determina a pasta de destino
    pasta_pai = Path(pasta_origem).parent
    
    # Salva em CSV
    csv_path = pasta_pai / f"{nome_arquivo}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"📁 CSV salvo: {csv_path}")
    
    # Salva em Excel
    xlsx_path = pasta_pai / f"{nome_arquivo}.xlsx"
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    print(f"📁 Excel salvo: {xlsx_path}")
    
    # Salva em JSON consolidado
    json_path = pasta_pai / f"{nome_arquivo}.json"
    df.to_json(json_path, orient='records', indent=2, force_ascii=False)
    print(f"📁 JSON salvo: {json_path}")


# Função principal para testar
def consolidar_dados_7_dias():
    """
    Consolida os dados da pasta de 7 dias.
    """
    caminho_7_dias = r"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito\relatorios\59\7"
    
    print("=" * 60)
    print("CONSOLIDANDO DADOS DE 7 DIAS")
    print("=" * 60)
    
    df = ler_jsons_pasta_para_dataframe(caminho_7_dias, incluir_metadados=True)
    
    if df is not None:
        print("\n=== RESUMO DOS DADOS ===")
        print(f"Total de registros: {len(df)}")
        print(f"Unidades únicas: {df['unit_id'].nunique() if 'unit_id' in df.columns else 'N/A'}")
        
        print("\nPrimeiras 3 linhas:")
        print(df.head(3))
        
        print("\nInformações sobre as colunas:")
        print(df.info())
        
        print("\nEstatísticas descritivas:")
        print(df.describe())
        
        # Salva os dados consolidados
        salvar_dataframe_consolidado(df, caminho_7_dias, "relatorio_7_dias_consolidado")
        
        return df
    else:
        print("❌ Falha ao consolidar dados")
        return None


def consolidar_dados_30_dias():
    """
    Consolida os dados da pasta de 30 dias.
    """
    caminho_30_dias = r"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito\relatorios\59\30"
    
    print("=" * 60)
    print("CONSOLIDANDO DADOS DE 30 DIAS")
    print("=" * 60)
    
    df = ler_jsons_pasta_para_dataframe(caminho_30_dias, incluir_metadados=True)
    
    if df is not None:
        print("\n=== RESUMO DOS DADOS ===")
        print(f"Total de registros: {len(df)}")
        print(f"Unidades únicas: {df['unit_id'].nunique() if 'unit_id' in df.columns else 'N/A'}")
        
        print("\nPrimeiras 3 linhas:")
        print(df.head(3))
        
        # Salva os dados consolidados
        salvar_dataframe_consolidado(df, caminho_30_dias, "relatorio_30_dias_consolidado")
        
        return df
    else:
        print("❌ Falha ao consolidar dados")
        return None


# Adicione ao final do arquivo para testar
if __name__ == "__main__":
    # Teste de consolidação
    df_7_dias = consolidar_dados_7_dias()
    df_30_dias = consolidar_dados_30_dias()
    

#!/usr/bin/env python
"""
Script para testar as importações com os arquivos reais
"""
import os
import sys
import pandas as pd

# Caminhos dos arquivos
CAMINHO_BACKUP = r"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE - BackUP\umbrella360\01"
CAMINHO_PROJETO = r"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE"

def analisar_arquivos():
    """Analisa a estrutura dos arquivos Excel"""
    arquivos = [
        "Lista_Motoristas.xlsx",
        "Lista_Caminhoes.xlsx", 
        "Viagens_Motoristas.xlsx",
        "Viagens_Caminhoes.xlsx"
    ]
    
    print("🔍 ANALISANDO ARQUIVOS EXCEL")
    print("=" * 60)
    
    for arquivo in arquivos:
        caminho_completo = os.path.join(CAMINHO_BACKUP, arquivo)
        
        if os.path.exists(caminho_completo):
            print(f"\n📄 ARQUIVO: {arquivo}")
            print("-" * 40)
            
            try:
                df = pd.read_excel(caminho_completo, engine='openpyxl')
                print(f"📊 Total de registros: {len(df)}")
                print(f"📋 Colunas disponíveis:")
                for i, col in enumerate(df.columns.tolist(), 1):
                    print(f"  {i:2d}. '{col}'")
                
                print(f"\n📝 Primeiros 2 registros:")
                print(df.head(2).to_string(index=False))
                
            except Exception as e:
                print(f"❌ Erro ao ler arquivo: {e}")
        else:
            print(f"\n❌ ARQUIVO NÃO ENCONTRADO: {arquivo}")
    
    print("\n" + "=" * 60)

def executar_importacoes():
    """Executa as importações na ordem correta"""
    print("\n🚀 EXECUTANDO IMPORTAÇÕES")
    print("=" * 60)
    
    # Navegar para o diretório do projeto
    os.chdir(CAMINHO_PROJETO)
    
    comandos = [
        f'python manage.py IMP_L_MOT "{os.path.join(CAMINHO_BACKUP, "Lista_Motoristas.xlsx")}"',
        f'python manage.py IMP_CAM "{os.path.join(CAMINHO_BACKUP, "Lista_Caminhoes.xlsx")}"',
        f'python manage.py importar_viagens_motoristas "{os.path.join(CAMINHO_BACKUP, "Viagens_Motoristas.xlsx")}"',
        f'python manage.py importar_viagens_caminhoes "{os.path.join(CAMINHO_BACKUP, "Viagens_Caminhoes.xlsx")}"'
    ]
    
    nomes = [
        "Motoristas",
        "Caminhões", 
        "Viagens de Motoristas",
        "Viagens de Caminhões"
    ]
    
    for i, (comando, nome) in enumerate(zip(comandos, nomes), 1):
        print(f"\n{i}. IMPORTANDO {nome.upper()}...")
        print(f"Comando: {comando}")
        
        try:
            resultado = os.system(comando)
            if resultado == 0:
                print(f"✅ {nome} importado com sucesso!")
            else:
                print(f"❌ Erro na importação de {nome}")
                break
        except Exception as e:
            print(f"❌ Erro ao executar comando: {e}")
            break

def main():
    print("🎯 SCRIPT DE TESTE DE IMPORTAÇÕES - UMBRELLA360")
    print("=" * 60)
    
    # Verificar se os arquivos existem
    if not os.path.exists(CAMINHO_BACKUP):
        print(f"❌ Diretório não encontrado: {CAMINHO_BACKUP}")
        return
    
    if not os.path.exists(CAMINHO_PROJETO):
        print(f"❌ Diretório do projeto não encontrado: {CAMINHO_PROJETO}")
        return
    
    # Analisar arquivos
    analisar_arquivos()
    
    # Perguntar se deve executar as importações
    resposta = input("\n❓ Deseja executar as importações? (s/n): ").strip().lower()
    
    if resposta == 's':
        executar_importacoes()
    else:
        print("⏭️  Importações canceladas pelo usuário.")
    
    print("\n✅ SCRIPT FINALIZADO!")

if __name__ == "__main__":
    main()

import pandas as pd
import os

# Caminhos dos arquivos
caminho_backup = r"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE - BackUP\umbrella360\01"
arquivos = [
    "Lista_Caminhoes.xlsx",
    "Lista_Motoristas.xlsx", 
    "Viagens_Caminhoes.xlsx",
    "Viagens_Motoristas.xlsx"
]

print("🔍 ANALISANDO ESTRUTURA DOS ARQUIVOS EXCEL")
print("=" * 60)

for arquivo in arquivos:
    caminho_completo = os.path.join(caminho_backup, arquivo)
    
    if os.path.exists(caminho_completo):
        print(f"\n📄 ARQUIVO: {arquivo}")
        print("-" * 40)
        
        try:
            df = pd.read_excel(caminho_completo, engine='openpyxl')
            print(f"📊 Total de registros: {len(df)}")
            print(f"📋 Colunas disponíveis:")
            for i, col in enumerate(df.columns.tolist(), 1):
                print(f"  {i:2d}. {col}")
            
            # Mostrar alguns dados de exemplo
            print(f"\n📝 Primeiros 3 registros:")
            print(df.head(3).to_string(index=False))
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
    else:
        print(f"\n❌ ARQUIVO NÃO ENCONTRADO: {arquivo}")

print("\n" + "=" * 60)
print("✅ ANÁLISE CONCLUÍDA")

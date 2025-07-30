# Configuração dos Caminhos dos Arquivos - Umbrella360

## 📁 Estrutura dos Arquivos

Para usar os comandos de importação, organize seus arquivos Excel da seguinte forma:

```
C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação\
├── Lista_Motoristas.xlsx      # Lista de motoristas únicos
├── Lista_Caminhoes.xlsx       # Lista de caminhões únicos
├── Viagens_Motoristas.xlsx    # Dados de viagens dos motoristas
└── Viagens_Caminhoes.xlsx     # Dados de viagens dos caminhões
```

## 📋 Colunas Obrigatórias por Arquivo

### 1. Lista_Motoristas.xlsx
- **Agrupamento**: Nome do motorista

### 2. Lista_Caminhoes.xlsx
- **Agrupamento**: Código do caminhão
- **Marca**: Marca do caminhão

### 3. Viagens_Motoristas.xlsx
- **Agrupamento**: Nome do motorista (deve existir em Lista_Motoristas.xlsx)
- **Quilometragem**: Quilometragem total
- **Consumido por AbsFCS**: Combustível consumido em litros
- **Quilometragem média por unidade de combustível por AbsFCS**: Média de consumo (km/l)
- **Horas de motor**: Horas de funcionamento do motor
- **Velocidade média**: Velocidade média em km/h
- **Emissões de CO2**: Emissões de CO2 em g/km
- **Mês**: Mês de referência

### 4. Viagens_Caminhoes.xlsx
- **Agrupamento**: Código do caminhão (deve existir em Lista_Caminhoes.xlsx)
- **Quilometragem**: Quilometragem total
- **Consumido por AbsFCS**: Combustível consumido em litros
- **Quilometragem média por unidade de combustível por AbsFCS**: Média de consumo (km/l)
- **Horas de motor**: Horas de funcionamento do motor
- **Velocidade média**: Velocidade média em km/h
- **RPM médio**: RPM médio do motor
- **Temperatura média**: Temperatura média em °C
- **Emissões de CO2**: Emissões de CO2 em g/km
- **Mês**: Mês de referência

## 🚀 Comandos de Importação

### Importação Individual

```bash
# 1. Importar motoristas
python manage.py IMP_L_MOT "C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação\Lista_Motoristas.xlsx"

# 2. Importar caminhões
python manage.py IMP_CAM "C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação\Lista_Caminhoes.xlsx"

# 3. Importar viagens de motoristas
python manage.py importar_viagens_motoristas "C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação\Viagens_Motoristas.xlsx"

# 4. Importar viagens de caminhões
python manage.py importar_viagens_caminhoes "C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação\Viagens_Caminhoes.xlsx"
```

### Importação Completa Automatizada

```bash
# Execute o script completo
umbrella360\management\commands\importar_tudo.bat
```

## ⚠️ Ordem de Importação Importante

**SEMPRE siga esta ordem:**
1. **Motoristas** primeiro (base para viagens de motoristas)
2. **Caminhões** segundo (base para viagens de caminhões)
3. **Viagens de Motoristas** terceiro (depende dos motoristas)
4. **Viagens de Caminhões** por último (depende dos caminhões)

## 🔧 Personalização dos Caminhos

Para alterar os caminhos padrão, edite o arquivo `importar_tudo.bat`:

```batch
set "CAMINHO_DADOS=SEU_CAMINHO_PERSONALIZADO"
set "MOTORISTAS=%CAMINHO_DADOS%\SEU_ARQUIVO_MOTORISTAS.xlsx"
set "CAMINHOES=%CAMINHO_DADOS%\SEU_ARQUIVO_CAMINHOES.xlsx"
set "VIAGENS_MOT=%CAMINHO_DADOS%\SEU_ARQUIVO_VIAGENS_MOT.xlsx"
set "VIAGENS_CAM=%CAMINHO_DADOS%\SEU_ARQUIVO_VIAGENS_CAM.xlsx"
```

## 📊 Validação dos Dados

### Antes da Importação
- Verifique se todos os arquivos existem
- Confirme que as colunas obrigatórias estão presentes
- Remova linhas vazias dos arquivos Excel

### Durante a Importação
- Use `--dry-run` para simular primeiro
- Verifique os relatórios de duplicatas
- Confirme que não há erros de referência

### Após a Importação
- Acesse o Django Admin para verificar os dados
- Confirme as quantidades importadas
- Verifique se os relacionamentos estão corretos

## 🚨 Problemas Comuns

### 1. "Motorista não encontrado no banco"
**Causa**: Tentativa de importar viagens antes dos motoristas
**Solução**: Importe motoristas primeiro

### 2. "Caminhão não encontrado no banco"
**Causa**: Tentativa de importar viagens antes dos caminhões
**Solução**: Importe caminhões primeiro

### 3. "Coluna não encontrada"
**Causa**: Nome da coluna diferente do esperado
**Solução**: Verifique os nomes das colunas no Excel

### 4. "Arquivo não encontrado"
**Causa**: Caminho incorreto ou arquivo não existe
**Solução**: Verifique se o arquivo existe no caminho especificado

## 💡 Dicas Importantes

- ✅ Use nomes de colunas exatos (case-sensitive)
- ✅ Remova acentos dos nomes de colunas se houver problemas
- ✅ Mantenha consistência nos nomes de agrupamento
- ✅ Faça backup do banco antes de importações grandes
- ✅ Teste com arquivos pequenos primeiro

## 🔄 Atualização de Dados

Para atualizar dados existentes:

```bash
# Atualizar motoristas
python manage.py IMP_L_MOT arquivo.xlsx --update

# Atualizar caminhões
python manage.py IMP_CAM arquivo.xlsx --update

# Viagens são únicas por motorista/caminhão + mês
# Não há duplicatas de viagens para o mesmo período
```

## 📱 Exemplo de Uso Completo

```bash
# 1. Navegar para o diretório do projeto
cd "C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE"

# 2. Ativar ambiente Python
conda activate VENV_01

# 3. Executar importação completa
umbrella360\management\commands\importar_tudo.bat

# 4. Verificar resultados
python manage.py runserver
# Acesse: http://localhost:8000/admin/
```

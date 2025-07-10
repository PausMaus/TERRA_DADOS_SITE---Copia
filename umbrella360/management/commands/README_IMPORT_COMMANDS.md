# Comandos de Importação - Umbrella360

## Visão Geral

Este documento descreve os comandos de importação refatorados para garantir que apenas registros únicos sejam importados, evitando duplicatas e fornecendo relatórios detalhados.

## Comandos Disponíveis

### 1. IMP_L_MOT.py - Importação de Motoristas

Importa motoristas únicos de um arquivo Excel, usando o campo "Agrupamento" como identificador único.

#### Uso Básico
```bash
python manage.py IMP_L_MOT caminho/para/arquivo.xlsx
```

#### Opções Disponíveis
- `--dry-run`: Simula a importação sem salvar no banco de dados
- `--update`: Atualiza registros existentes (funcionalidade expandível)

#### Exemplos
```bash
# Importação normal
python manage.py IMP_L_MOT dados/motoristas.xlsx

# Simulação (não salva no banco)
python manage.py IMP_L_MOT dados/motoristas.xlsx --dry-run

# Modo atualização
python manage.py IMP_L_MOT dados/motoristas.xlsx --update
```

#### Requisitos do Arquivo Excel
- Deve conter a coluna "Agrupamento"
- Linhas com valores vazios ou nulos em "Agrupamento" são ignoradas
- Duplicatas no próprio arquivo são removidas automaticamente

### 2. IMP_CAM.py - Importação de Caminhões

Importa caminhões únicos de um arquivo Excel, usando o campo "Agrupamento" como identificador único.

#### Uso Básico
```bash
python manage.py IMP_CAM caminho/para/arquivo.xlsx
```

#### Opções Disponíveis
- `--dry-run`: Simula a importação sem salvar no banco de dados
- `--update`: Atualiza registros existentes (atualiza a marca se for diferente)

#### Exemplos
```bash
# Importação normal
python manage.py IMP_CAM dados/caminhoes.xlsx

# Simulação (não salva no banco)
python manage.py IMP_CAM dados/caminhoes.xlsx --dry-run

# Modo atualização (atualiza marcas diferentes)
python manage.py IMP_CAM dados/caminhoes.xlsx --update
```

#### Requisitos do Arquivo Excel
- Deve conter as colunas "Agrupamento" e "Marca"
- Linhas com valores vazios ou nulos são ignoradas
- Duplicatas no próprio arquivo são removidas automaticamente

## Funcionalidades Avançadas

### 1. Detecção de Duplicatas
- **No arquivo**: Remove duplicatas mantendo apenas a primeira ocorrência
- **No banco**: Verifica se o registro já existe antes de importar
- **Relatório**: Mostra quantas duplicatas foram encontradas e removidas

### 2. Modo Dry-Run
- Simula a importação sem fazer alterações no banco
- Mostra exatamente o que seria importado
- Útil para validar dados antes da importação real

### 3. Modo Update
- **Motoristas**: Estrutura preparada para futuras atualizações
- **Caminhões**: Atualiza a marca se for diferente da existente

### 4. Relatórios Detalhados
Cada comando fornece:
- Total de registros no arquivo
- Número de duplicatas removidas
- Registros novos vs existentes
- Estatísticas finais pós-importação

## Exemplo de Saída

```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 1250
Motoristas novos para importar: 45
Motoristas já existentes no banco: 1205
Duplicatas removidas do arquivo: 23

⚠️  MOTORISTAS JÁ EXISTENTES (primeiros 5):
  - JOÃO SILVA
  - MARIA SANTOS
  - PEDRO OLIVEIRA
  - ANA COSTA
  - CARLOS PEREIRA
  ... e mais 1200

✅ 45 motoristas novos importados com sucesso!

📋 RESUMO FINAL:
✅ Novos importados: 45
⚠️  Já existiam: 1205
📊 Total no banco agora: 1250
```

## Tratamento de Erros

Os comandos incluem tratamento robusto de erros:
- Validação de arquivos existentes
- Verificação de colunas obrigatórias
- Tratamento de valores vazios/nulos
- Stack trace completo em caso de erro

## Melhores Práticas

### 1. Sempre use --dry-run primeiro
```bash
python manage.py IMP_L_MOT dados.xlsx --dry-run
```

### 2. Backup do banco antes de importações grandes
```bash
python manage.py dumpdata > backup_antes_importacao.json
```

### 3. Validação de dados
- Verifique se as colunas obrigatórias existem
- Remova linhas vazias do Excel antes da importação
- Use formatação consistente nos dados

### 4. Importação incremental
- Use os comandos regularmente para manter dados atualizados
- O sistema automaticamente ignora duplicatas

## Expansão Futura

### Campos Adicionais para Motoristas
Para adicionar novos campos, modifique:
1. O modelo `Motorista` em `models.py`
2. A lógica de importação em `IMP_L_MOT.py`
3. O modo `--update` para atualizar os novos campos

### Campos Adicionais para Caminhões
Para adicionar novos campos, modifique:
1. O modelo `Caminhao` em `models.py`
2. A lógica de importação em `IMP_CAM.py`
3. O modo `--update` para atualizar os novos campos

## Troubleshooting

### Erro: "Arquivo não encontrado"
- Verifique o caminho completo do arquivo
- Use barras invertidas duplas no Windows: `C:\\dados\\arquivo.xlsx`

### Erro: "Coluna não encontrada"
- Verifique se as colunas obrigatórias existem no Excel
- Nomes devem ser exatamente: "Agrupamento", "Marca"

### Erro: "Sem permissão para escrever"
- Execute como administrador ou verifique permissões do arquivo
- Certifique-se de que o arquivo Excel não está aberto

### Performance em arquivos grandes
- Use `--dry-run` para testar primeiro
- Considere dividir arquivos muito grandes (>10.000 registros)
- O `bulk_create` é otimizado para performance

## Changelog

### v2.0 (Atual)
- ✅ Detecção e remoção de duplicatas
- ✅ Modo dry-run
- ✅ Modo update
- ✅ Relatórios detalhados
- ✅ Tratamento robusto de erros
- ✅ Validação de dados

### v1.0 (Antigo)
- ❌ Importação simples sem verificação de duplicatas
- ❌ Sem relatórios detalhados
- ❌ Sem validação de dados

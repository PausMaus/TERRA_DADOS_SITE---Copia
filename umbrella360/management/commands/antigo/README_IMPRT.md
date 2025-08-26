# Comando IMPRT - Importação de Viagens

## Visão Geral
O comando IMPRT foi atualizado para processar automaticamente todos os arquivos Excel de uma pasta, usando o nome da pasta como período. Isso facilita a organização dos dados por período temporal.

## Novos Modos de Uso

### Modo 1: Processar uma pasta completa (RECOMENDADO)
```bash
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Ontem"
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Últimos 7 dias"
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Últimos 30 dias"
```

**Como funciona:**
- O comando lê todos os arquivos `.xlsx` e `.xls` da pasta especificada
- Usa o nome da pasta como período (ex: "Ontem", "Últimos 7 dias", "Últimos 30 dias")
- Processa cada arquivo sequencialmente
- Mostra progresso detalhado para cada arquivo

### Modo 2: Processar um arquivo específico (modo antigo)
```bash
python manage.py IMPRT --file "caminho/para/arquivo.xlsx" --periodo "Ontem"
```

## Estrutura de Pastas Recomendada

```
C:\TERRA DADOS\porto\UMBRELLA\
├── Ontem\
│   ├── arquivo1.xlsx
│   ├── arquivo2.xlsx
│   └── ...
├── Últimos 7 dias\
│   ├── arquivo1.xlsx
│   ├── arquivo2.xlsx
│   └── ...
└── Últimos 30 dias\
    ├── arquivo1.xlsx
    ├── arquivo2.xlsx
    └── ...
```

## Vantagens do Novo Sistema

1. **Automação completa**: Não é necessário especificar cada arquivo individualmente
2. **Organização por período**: O nome da pasta define automaticamente o período
3. **Processamento em lote**: Todos os arquivos de uma pasta são processados de uma só vez
4. **Compatibilidade**: O modo antigo ainda funciona para casos específicos
5. **Feedback detalhado**: Mostra progresso para cada arquivo processado

## Formato dos Arquivos Excel

Os arquivos devem ter as seguintes colunas na segunda planilha (índice 1):
- Agrupamento
- Quilometragem
- Consumido por AbsFCS
- Quilometragem média por unidade de combustível por AbsFCS
- Velocidade média
- Emissões de CO2

## Exemplos de Uso Prático

### Importar dados de ontem:
```bash
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Ontem"
```

### Importar dados dos últimos 7 dias:
```bash
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Últimos 7 dias"
```

### Importar dados dos últimos 30 dias:
```bash
python manage.py IMPRT --folder "C:\TERRA DADOS\porto\UMBRELLA\Últimos 30 dias"
```

## Mensagens de Log

O comando agora fornece feedback detalhado:
- Pasta sendo processada
- Período definido
- Número de arquivos encontrados
- Progresso de cada arquivo
- Resultado da importação para cada registro

# Exemplo Prático: Importação de Dados

Este exemplo mostra como usar os comandos de importação refatorados em uma situação real.

## Cenário

Você possui dois arquivos Excel:
- `motoristas_2024.xlsx` com 1.500 registros de motoristas
- `caminhoes_2024.xlsx` com 800 registros de caminhões

## Passo 1: Preparação dos Dados

### Arquivo de Motoristas
Certifique-se de que o arquivo `motoristas_2024.xlsx` tenha:
```
| Agrupamento          |
|---------------------|
| JOÃO SILVA          |
| MARIA SANTOS        |
| PEDRO OLIVEIRA      |
| ANA COSTA           |
| CARLOS PEREIRA      |
```

### Arquivo de Caminhões
Certifique-se de que o arquivo `caminhoes_2024.xlsx` tenha:
```
| Agrupamento | Marca      |
|-------------|------------|
| CAM001      | VOLVO      |
| CAM002      | SCANIA     |
| CAM003      | MERCEDES   |
| CAM004      | FORD       |
| CAM005      | IVECO      |
```

## Passo 2: Simulação da Importação

### Teste com Motoristas
```bash
# Navegar para o diretório do projeto
cd c:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE

# Simular importação de motoristas
python manage.py IMP_L_MOT C:\dados\motoristas_2024.xlsx --dry-run
```

**Saída esperada:**
```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 1.487
Motoristas novos para importar: 234
Motoristas já existentes no banco: 1.253
Duplicatas removidas do arquivo: 13

⚠️  MOTORISTAS JÁ EXISTENTES (primeiros 5):
  - JOÃO SILVA
  - MARIA SANTOS
  - PEDRO OLIVEIRA
  - ANA COSTA
  - CARLOS PEREIRA
  ... e mais 1248

🧪 MODO SIMULAÇÃO (DRY-RUN):
Nenhum dado foi salvo no banco de dados.
Seriam importados 234 motoristas novos.
```

### Teste com Caminhões
```bash
# Simular importação de caminhões
python manage.py IMP_CAM C:\dados\caminhoes_2024.xlsx --dry-run
```

**Saída esperada:**
```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 795
Caminhões novos para importar: 67
Caminhões já existentes no banco: 728
Duplicatas removidas do arquivo: 5

⚠️  CAMINHÕES JÁ EXISTENTES (primeiros 5):
  - CAM001 (VOLVO)
  - CAM002 (SCANIA)
  - CAM003 (MERCEDES)
  - CAM004 (FORD)
  - CAM005 (IVECO)
  ... e mais 723

🧪 MODO SIMULAÇÃO (DRY-RUN):
Nenhum dado foi salvo no banco de dados.
Seriam importados 67 caminhões novos.
Primeiros 3 que seriam importados:
  - CAM796 (VOLVO)
  - CAM797 (SCANIA)
  - CAM798 (MERCEDES)
```

## Passo 3: Importação Real

### Importar Motoristas
```bash
python manage.py IMP_L_MOT C:\dados\motoristas_2024.xlsx
```

**Saída esperada:**
```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 1.487
Motoristas novos para importar: 234
Motoristas já existentes no banco: 1.253
Duplicatas removidas do arquivo: 13

✅ 234 motoristas novos importados com sucesso!

📋 RESUMO FINAL:
✅ Novos importados: 234
⚠️  Já existiam: 1.253
📊 Total no banco agora: 1.487
```

### Importar Caminhões
```bash
python manage.py IMP_CAM C:\dados\caminhoes_2024.xlsx
```

**Saída esperada:**
```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 795
Caminhões novos para importar: 67
Caminhões já existentes no banco: 728
Duplicatas removidas do arquivo: 5

✅ 67 caminhões novos importados com sucesso!

📋 RESUMO FINAL:
✅ Novos importados: 67
⚠️  Já existiam: 728
📊 Total no banco agora: 795
```

## Passo 4: Importação com Atualização

Imagine que você recebeu um arquivo atualizado com algumas marcas de caminhões corrigidas:

```bash
python manage.py IMP_CAM C:\dados\caminhoes_2024_corrigido.xlsx --update
```

**Saída esperada:**
```
📊 RELATÓRIO DE IMPORTAÇÃO:
Total no arquivo (após limpar duplicatas): 795
Caminhões novos para importar: 0
Caminhões já existentes no banco: 795

📝 Atualizado: CAM123 - nova marca: VOLVO
📝 Atualizado: CAM456 - nova marca: SCANIA
📝 Atualizado: CAM789 - nova marca: MERCEDES

📝 3 caminhões atualizados!

📋 RESUMO FINAL:
✅ Novos importados: 0
⚠️  Já existiam: 795
📝 Atualizados: 3
📊 Total no banco agora: 795
```

## Passo 5: Verificação no Admin

Após a importação, verifique no Django Admin:

1. Acesse `http://localhost:8000/admin/`
2. Login com suas credenciais
3. Navegue para `Umbrella360 > Motoristas` e `Umbrella360 > Caminhões`
4. Verifique se os dados foram importados corretamente

### Filtros Úteis no Admin

**Para Motoristas:**
- Pesquisar por nome: use a barra de pesquisa
- Filtrar por data de criação: use o filtro lateral

**Para Caminhões:**
- Pesquisar por agrupamento: use a barra de pesquisa
- Filtrar por marca: use o filtro lateral

## Situações Especiais

### 1. Arquivo com Problemas
```bash
python manage.py IMP_L_MOT C:\dados\motoristas_problemas.xlsx --dry-run
```

**Saída com erro:**
```
❌ Erro ao importar: Colunas não encontradas: Agrupamento
Colunas disponíveis: Nome, Sobrenome, Departamento
```

**Solução:** Renomeie a coluna no Excel para "Agrupamento" ou ajuste o arquivo.

### 2. Arquivo Muito Grande
Para arquivos com mais de 10.000 registros, considere:
```bash
# Teste primeiro com dry-run
python manage.py IMP_L_MOT C:\dados\motoristas_grandes.xlsx --dry-run

# Se tudo estiver OK, importe
python manage.py IMP_L_MOT C:\dados\motoristas_grandes.xlsx
```

### 3. Importação Incremental Diária
```bash
# Script para importação diária
python manage.py IMP_L_MOT C:\dados\motoristas_diario.xlsx
python manage.py IMP_CAM C:\dados\caminhoes_diario.xlsx
```

O sistema automaticamente ignora duplicatas, tornando seguro executar diariamente.

## Backup e Restauração

### Antes de Importações Grandes
```bash
# Backup completo
python manage.py dumpdata > backup_pre_import.json

# Backup apenas dos apps umbrella360
python manage.py dumpdata umbrella360 > backup_umbrella360.json
```

### Em Caso de Problemas
```bash
# Restaurar backup
python manage.py loaddata backup_pre_import.json
```

## Monitoramento

### Verificar Quantidade de Registros
```bash
# Via Django shell
python manage.py shell

>>> from umbrella360.models import Motorista, Caminhao
>>> print(f"Motoristas: {Motorista.objects.count()}")
>>> print(f"Caminhões: {Caminhao.objects.count()}")
```

### Log de Importações
O sistema automaticamente gera logs detalhados. Considere redirecionar para arquivo:
```bash
python manage.py IMP_L_MOT dados.xlsx > import_log.txt 2>&1
```

## Próximos Passos

1. **Automatização**: Considere criar scripts batch/shell para importações regulares
2. **Validação**: Implemente validações adicionais nos modelos
3. **Relatórios**: Use os dados importados para gerar relatórios
4. **Integração**: Conecte com outros sistemas se necessário

## Dicas Importantes

- ✅ Sempre use `--dry-run` primeiro
- ✅ Faça backup antes de importações grandes
- ✅ Valide os dados no Excel antes da importação
- ✅ Use nomes de colunas exatos: "Agrupamento", "Marca"
- ✅ Remova linhas vazias do Excel
- ✅ Execute importações em horários de baixo uso
- ❌ Não interrompa importações em andamento
- ❌ Não edite arquivos Excel durante a importação

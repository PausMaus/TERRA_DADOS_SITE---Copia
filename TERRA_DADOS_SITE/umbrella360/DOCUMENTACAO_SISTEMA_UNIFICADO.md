# Sistema Umbrella360 - Versão Unificada Multi-Empresas

## Visão Geral

Este documento descreve as melhorias implementadas no sistema Umbrella360 para suportar múltiplas empresas e dados unificados.

## Principais Melhorias

### 1. Suporte a Múltiplas Empresas
- Novo modelo `Empresa` para gerenciar diferentes empresas
- Filtros dinâmicos por empresa
- Relatórios comparativos entre empresas

### 2. Tabela Unificada de Viagens
- Modelo `Viagem_Base` unifica dados de motoristas e veículos
- Modelo `Unidade` representa tanto motoristas quanto veículos
- Filtros por tipo de unidade (cls = 'motorista' ou 'veiculo')

### 3. Filtros Dinâmicos Avançados
- Filtro por empresa com atualização automática de marcas
- Filtro por marca específica da empresa selecionada
- Filtro por período
- Filtros de qualidade de dados (normais, erros, sem zeros)

### 4. Interface Melhorada
- Dashboard unificado com KPIs principais
- Tabelas separadas por tipo (empresa, marca, motoristas, veículos)
- Design responsivo e moderno

## Estrutura dos Novos Modelos

### Empresa
```python
class Empresa(models.Model):
    nome = models.CharField(max_length=100, unique=True)
```

### Unidade
```python
class Unidade(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # ID único
    nm = models.CharField(max_length=100)                   # Nome/Descrição
    cls = models.CharField(max_length=50)                   # Classe (motorista/veiculo)
    empresa = models.ForeignKey(Empresa)                    # Empresa proprietária
    marca = models.CharField(max_length=50)                 # Marca (para veículos)
    placa = models.CharField(max_length=20)                 # Placa (para veículos)
```

### Viagem_Base
```python
class Viagem_Base(models.Model):
    unidade = models.ForeignKey(Unidade)
    quilometragem = models.DecimalField(max_digits=10, decimal_places=2)
    Consumido = models.PositiveIntegerField()               # Combustível total
    Quilometragem_média = models.DecimalField(max_digits=5, decimal_places=2)  # km/L
    período = models.CharField(max_length=20)               # Mês/período
    # ... outros campos de telemetria
```

## Uso da Nova Interface

### 1. Acessar o Relatório Unificado
- URL: `/umbrella360/report-novo/`
- Menu: "Relatório Unificado"

### 2. Aplicar Filtros
1. **Empresa**: Selecione uma empresa específica ou "Todas as Empresas"
2. **Marca**: Automaticamente atualizada baseada na empresa selecionada
3. **Período**: Filtre por mês/período específico
4. **Filtro de Dados**: 
   - Todos os Dados
   - Sem Zeros (remove registros com consumo zero)
   - Valores Normais (apenas dados dentro de parâmetros esperados)
   - Possíveis Erros (dados suspeitos para revisão)

### 3. Análise dos Resultados
- **Dashboard Global**: KPIs principais da frota
- **Análise de Custos**: Comparação atual vs. objetivo
- **Por Empresa**: Desempenho comparativo entre empresas
- **Por Marca**: Análise por fabricante
- **Top Performers**: Melhores motoristas e veículos

## APIs Disponíveis

### Marcas por Empresa
- **GET** `/umbrella360/api/marcas/` - Todas as marcas
- **GET** `/umbrella360/api/marcas/{empresa_id}/` - Marcas de uma empresa específica

## Migração de Dados

Para migrar dados do sistema antigo para o novo:

1. **Criar Empresas**:
```python
empresa = Empresa.objects.create(nome="Empresa A")
```

2. **Criar Unidades** (Motoristas):
```python
for motorista in Motorista.objects.all():
    Unidade.objects.create(
        id=f"MOT_{motorista.id}",
        nm=motorista.agrupamento,
        cls="motorista",
        empresa=empresa
    )
```

3. **Criar Unidades** (Veículos):
```python
for caminhao in Caminhao.objects.all():
    Unidade.objects.create(
        id=caminhao.agrupamento,
        nm=f"{caminhao.marca} {caminhao.agrupamento}",
        cls="veiculo",
        empresa=empresa,
        marca=caminhao.marca
    )
```

4. **Migrar Viagens**:
```python
# Viagens de motoristas
for viagem in Viagem_MOT.objects.all():
    unidade = Unidade.objects.get(id=f"MOT_{viagem.agrupamento.id}")
    Viagem_Base.objects.create(
        unidade=unidade,
        quilometragem=viagem.quilometragem,
        Consumido=viagem.Consumido,
        # ... outros campos
        período=viagem.mês
    )

# Viagens de veículos
for viagem in Viagem_CAM.objects.all():
    unidade = Unidade.objects.get(id=viagem.agrupamento.agrupamento)
    Viagem_Base.objects.create(
        unidade=unidade,
        quilometragem=viagem.quilometragem,
        Consumido=viagem.Consumido,
        # ... outros campos
        período=viagem.mês
    )
```

## Benefícios da Nova Arquitetura

1. **Escalabilidade**: Suporta facilmente novas empresas
2. **Flexibilidade**: Tipos de unidades configuráveis
3. **Performance**: Menos JOINs, consultas mais eficientes
4. **Manutenibilidade**: Código mais limpo e organizado
5. **Usabilidade**: Interface mais intuitiva e filtros dinâmicos

## Próximos Passos

1. Implementar migração automática de dados
2. Adicionar gráficos interativos na nova interface
3. Criar relatórios específicos por empresa
4. Implementar exportação de dados filtrados
5. Adicionar alertas e notificações baseadas em desempenho

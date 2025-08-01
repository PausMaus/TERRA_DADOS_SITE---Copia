# Gráfico de Comparação - Médias por Veículo

## Descrição das Mudanças

O gráfico de barras de comparação entre marcas foi atualizado para mostrar **médias por veículo** ao invés de totais absolutos. Esta mudança permite uma comparação mais justa entre marcas com diferentes números de veículos na frota.

## Modificações Implementadas

### 1. Backend (views.py)

#### Função `calcular_stats_marca_novo`
- **Adicionado**: Contagem de veículos únicos por marca (`total_veiculos`)
- **Adicionado**: Cálculo de médias por veículo:
  - `quilometragem_por_veiculo`: Quilometragem total ÷ número de veículos
  - `consumo_por_veiculo`: Consumo total ÷ número de veículos  
  - `emissoes_por_veiculo`: Emissões totais ÷ número de veículos
  - `eficiencia_por_veiculo`: Mantém a eficiência média (já é uma média)

### 2. Frontend (report_novo.html)

#### Dados JavaScript
- **Atualizado**: Objeto `marcasData` para usar as novas métricas por veículo
- **Adicionado**: Campo `total_veiculos` para mostrar no tooltip

#### Configurações do Gráfico
- **Atualizados**: Labels dos gráficos para indicar "por veículo"
- **Atualizados**: Textos dos botões/tabs:
  - "Quilometragem por Veículo"
  - "Consumo por Veículo" 
  - "Emissões por Veículo"
  - "Eficiência Média" (mantido)

#### Tooltip Interativo
- **Adicionado**: Informação sobre o total de veículos da marca no tooltip
- **Formato**: "Total de veículos: X"

## Benefícios da Mudança

### 1. Comparação Mais Justa
- Marcas com poucos veículos não ficam prejudicadas no gráfico
- Marcas com muitos veículos não dominam visualmente os totais

### 2. Insights Mais Relevantes
- **Quilometragem por veículo**: Indica o uso médio por unidade
- **Consumo por veículo**: Mostra o gasto médio de combustível por unidade
- **Emissões por veículo**: Revela o impacto ambiental médio por unidade
- **Eficiência**: Mantém o mesmo significado (km/L médio)

### 3. Transparência
- Tooltip mostra quantos veículos cada marca possui
- Usuário pode entender o contexto dos dados

## Exemplo de Interpretação

**Antes (Totais)**:
- Marca A: 10.000 km total
- Marca B: 5.000 km total
- ❌ Marca A parece "melhor", mas pode ter mais veículos

**Depois (Médias por Veículo)**:
- Marca A: 2.000 km/veículo (5 veículos = 10.000 km total)
- Marca B: 2.500 km/veículo (2 veículos = 5.000 km total)  
- ✅ Marca B tem melhor utilização por veículo

## Compatibilidade

- ✅ Mantém todos os filtros existentes (empresa, período, classe, marca)
- ✅ Preserva o filtro de eficiência mínima (≥4 km/L)
- ✅ Interface responsiva para mobile
- ✅ Todas as funcionalidades anteriores funcionam normalmente

## Dados Técnicos

### Campos Calculados:
```python
# No views.py - função calcular_stats_marca_novo
stats['quilometragem_por_veiculo'] = total_quilometragem / total_veiculos
stats['consumo_por_veiculo'] = total_consumido / total_veiculos  
stats['emissoes_por_veiculo'] = total_emissoes / total_veiculos
stats['eficiencia_por_veiculo'] = media_quilometragem  # Já é média
```

### Proteção contra Divisão por Zero:
```python
total_veiculos = stats['total_veiculos'] or 1  # Evitar divisão por zero
```

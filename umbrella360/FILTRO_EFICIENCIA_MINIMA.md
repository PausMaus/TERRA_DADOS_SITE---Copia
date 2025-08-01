# FILTRO DE EFICIÊNCIA MÍNIMA - RELATÓRIO NOVO

## Implementação do Filtro de 4 km/L

### O que foi adicionado:

1. **Nova função de filtro**:
   ```python
   def aplicar_filtro_eficiencia_minima(queryset, eficiencia_minima=4.0):
       """Aplica filtro de eficiência mínima para remover dados irreais/com erros"""
       return queryset.filter(Quilometragem_média__gte=eficiencia_minima)
   ```

2. **Aplicação do filtro em todas as views do sistema novo**:
   - `report_novo()`: Filtra todas as viagens antes dos cálculos
   - `obter_unidades_com_stats()`: Aplica na busca de estatísticas por unidade
   - `detalhes_unidade()`: Filtra as viagens da unidade específica

### Onde é aplicado:

#### ✅ report_novo():
- Aplica o filtro após os filtros combinados normais
- Todos os cálculos (KPIs, estatísticas por marca/empresa) usam dados filtrados
- Gráfico de comparação entre marcas também usa dados filtrados

#### ✅ obter_unidades_com_stats():
- Filtra viagens de cada unidade individual
- Estatísticas de eficiência média calculadas apenas com dados válidos

#### ✅ detalhes_unidade():
- Todas as estatísticas da unidade baseadas em dados com eficiência ≥ 4 km/L
- Histórico de viagens também filtrado

### Benefícios:

1. **Qualidade dos dados**: Remove viagens com valores irreais/erros
2. **Relatórios mais precisos**: KPIs baseados apenas em dados válidos
3. **Gráficos limpos**: Comparações entre marcas sem outliers
4. **Consistência**: Todos os cálculos usam o mesmo padrão de qualidade

### Valor do filtro:

- **Padrão**: 4.0 km/L (configurável via parâmetro da função)
- **Justificativa**: Valores abaixo de 4 km/L geralmente indicam:
  - Erros de medição
  - Problemas no sistema de coleta
  - Dados corrompidos
  - Situações atípicas (marcha lenta excessiva, etc.)

### Sistema antigo:

❌ **Não aplicado** - Mantido sem alterações para preservar compatibilidade
- Views `report()`, `motoristas()`, `caminhoes()` seguem funcionando normalmente
- Dados históricos preservados para comparação

### Observações:

- O filtro é aplicado **apenas no sistema novo** (Viagem_Base)
- Sistema antigo (Viagem_MOT, Viagem_CAM) não foi alterado
- Fácil de ajustar o valor mínimo alterando o parâmetro da função
- Não afeta dados no banco - apenas filtra a consulta

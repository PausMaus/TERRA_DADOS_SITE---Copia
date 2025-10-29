# 📊 Análise de Jornada de Trabalho - Motoristas

## 🎯 Objetivo

Esta funcionalidade analisa o **tempo de trabalho efetivo** de cada motorista ao longo do dia, calculando quantas horas eles passaram ao volante com base nos registros de timestamp das viagens.

---

## 🚀 Como Funciona

### **Lógica de Cálculo**

1. **Agrupamento por Data e Motorista**
   - Todas as viagens do motorista são agrupadas por data
   - Registros são ordenados cronologicamente por timestamp

2. **Cálculo de Tempo ao Volante**
   - Considera a diferença entre timestamps consecutivos
   - **Sessão Contínua**: Diferença ≤ 5 minutos (300 segundos)
   - **Nova Sessão**: Diferença > 5 minutos e ≤ 1 hora
   - **Ignora**: Diferenças > 1 hora (pausas longas, almoço, etc.)

3. **Classificação de Jornada**
   - ✅ **Jornada Completa**: ≥ 8 horas/dia (média)
   - ⚠️ **Jornada Parcial**: 6 a 8 horas/dia (média)
   - ❌ **Jornada Reduzida**: < 6 horas/dia (média)

4. **Identificação de Turno**
   - 🌅 **Manhã**: Início antes das 12h
   - ☀️ **Tarde**: Início entre 12h e 18h
   - 🌙 **Noite**: Início após 18h

---

## 📈 Métricas Calculadas

### **Por Motorista**
- ⏱️ Total de horas trabalhadas (período completo)
- 📅 Total de dias trabalhados
- 📊 Média de horas por dia
- 🚗 Total de veículos utilizados
- 🎯 Classificação de jornada

### **Por Dia (Detalhamento)**
- 📅 Data
- 🌅/☀️/🌙 Turno predominante
- ⏰ Horário de início e fim
- ⏱️ Total de horas trabalhadas
- 🚗 Quantidade de veículos utilizados
- 🚀 Velocidade média
- 📍 Número de registros (pontos GPS)

### **Estatísticas Gerais**
- 👥 Total de motoristas analisados
- ⏱️ Total de horas trabalhadas (todos)
- 📊 Média de horas por motorista
- 📅 Média de dias trabalhados
- Distribuição por classificação de jornada

---

## 🔍 Filtros Disponíveis

### **Período Rápido**
- Últimos 7 dias
- Últimos 15 dias
- Últimos 30 dias (padrão)
- Últimos 60 dias
- Últimos 90 dias
- Personalizado (data início/fim)

### **Data Personalizada**
- Selecione "Personalizado" no dropdown
- Informe data de início
- Informe data de fim
- Clique em "Filtrar"

---

## 📊 Visualizações

### **1. Cards de Estatísticas**
- Total de motoristas
- Total de horas trabalhadas
- Média de horas por motorista
- Média de dias trabalhados

### **2. Classificação de Jornadas**
- ✅ Jornada Completa
- ⚠️ Jornada Parcial
- ❌ Jornada Reduzida

### **3. Gráfico de Evolução Temporal**
- 📈 Linha: Total de horas por dia
- 📈 Linha: Motoristas ativos por dia
- 📈 Linha: Média de horas por motorista/dia

### **4. Tabela Detalhada por Motorista**
- Card expandível com resumo
- Botão "Ver Detalhes por Dia"
- Tabela completa com todas as jornadas diárias

---

## 🎨 Recursos Visuais

- **Cores Dinâmicas**: Classificação colorida por performance
- **Emojis Intuitivos**: Identificação visual rápida
- **Design Responsivo**: Funciona em mobile e desktop
- **Gráficos Interativos**: Chart.js com tooltips detalhados
- **Expandir/Colapsar**: Detalhes por motorista sob demanda

---

## 🔗 Acesso

**URL**: `/jornada-motoristas/`

**Menu de Navegação**:
- Início → Painel → Performance → **Jornada**
- Ou acesse diretamente: `https://seusite.com/jornada-motoristas/`

---

## 💡 Casos de Uso

### **1. Gestão de Horas Extras**
- Identificar motoristas trabalhando acima de 8h/dia
- Calcular horas extras para folha de pagamento

### **2. Compliance Trabalhista**
- Verificar cumprimento de jornada
- Identificar jornadas irregulares
- Documentar pausas e descansos

### **3. Otimização de Escalas**
- Redistribuir motoristas subutilizados
- Balancear carga de trabalho
- Planejar contratações

### **4. Análise de Produtividade**
- Correlacionar horas trabalhadas com performance
- Identificar padrões de eficiência
- Comparar turnos (manhã vs tarde vs noite)

---

## ⚠️ Observações Importantes

### **Limitações**
- **Dependência de GPS**: Requer registros contínuos de Viagem_eco
- **Precisão de Timestamp**: Depende da qualidade dos dados
- **Pausas Curtas**: Pausas < 5min são consideradas trabalho contínuo
- **Pausas Longas**: Pausas > 1h são ignoradas (ex: almoço)

### **Recomendações**
- Use períodos de análise de 7-30 dias para dados significativos
- Verifique a qualidade dos dados de GPS antes da análise
- Compare com registros de ponto eletrônico (se disponível)
- Considere variações sazonais e datas especiais

---

## 🛠️ Manutenção

### **Ajustar Limites de Sessão**

Edite em `views.py` na função `jornada_motoristas()`:

```python
# Linha ~2706
if diferenca_segundos <= 300:  # Altere 300 para outro valor em segundos
    jornadas_por_data[data_viagem]['tempo_total_segundos'] += diferenca_segundos
```

### **Ajustar Classificações**

Edite em `views.py`:

```python
# Linha ~2771
if media_horas_dia >= 8:  # Altere o limite de 8 horas
    classificacao = "Jornada Completa"
elif media_horas_dia >= 6:  # Altere o limite de 6 horas
    classificacao = "Jornada Parcial"
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se há dados de Viagem_eco no período
2. Confirme que motoristas estão associados às viagens
3. Revise os logs de erro do Django
4. Entre em contato com o suporte técnico

---

**Desenvolvido por**: Umbrella360 Team  
**Versão**: 1.0  
**Data**: Outubro 2025

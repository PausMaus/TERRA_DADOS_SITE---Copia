# Tabelas Interativas - Umbrella360

## Funcionalidades Implementadas

### 1. Ordenação por Colunas
- **Como usar**: Clique em qualquer cabeçalho de tabela para ordenar por essa coluna
- **Indicadores visuais**: 
  - ↕ = Coluna não ordenada
  - ↑ = Ordenação crescente (A-Z, 0-9)
  - ↓ = Ordenação decrescente (Z-A, 9-0)
- **Tipos de ordenação**:
  - Numérica: Para valores com números (automaticamente detectado)
  - Alfabética: Para texto e valores mistos

### 2. Pesquisa em Tabelas
- **Disponível em**: Tabelas com mais de 5 registros
- **Como usar**: Digite no campo "Pesquisar na tabela..." 
- **Funcionalidade**: Filtra linhas em tempo real conforme você digita
- **Resetar**: Limpe o campo para ver todos os registros novamente

### 3. Contador de Registros
- **Localização**: Abaixo de cada tabela
- **Informações mostradas**:
  - Total de registros quando não há pesquisa ativa
  - "Mostrando: X de Y registros" durante pesquisa

### 4. Efeitos Visuais
- **Hover**: Linhas destacam quando o mouse passa sobre elas
- **Coluna ordenada**: Temporariamente destacada após ordenação
- **Animações**: Transições suaves durante ordenação
- **Responsive**: Adapta-se a diferentes tamanhos de tela

## Páginas com Tabelas Interativas

### 1. Relatório Global (`/report/`)
- ✅ Análise de Custos e Economia Potencial
- ✅ Caminhões Por Marca  
- ✅ Motoristas (por maior média de consumo)
- ✅ Caminhões (por maior média de consumo)

### 2. Motoristas (`/motoristas/`)
- ✅ Viagens de Motoristas (por maior média de consumo)

### 3. Caminhões (`/caminhoes/`)
- ✅ Caminhões (por maior média de consumo)

## Integração com Temas

As tabelas se adaptam automaticamente aos três temas disponíveis:

### Tema "Noite de Verão" (Padrão)
- Cores: Azul (#3498db) e tons de cinza
- Hover: Azul claro translúcido

### Tema "Café"
- Cores: Marrom (#8b4513) e tons terrosos
- Hover: Marrom claro translúcido

### Tema "Empresarial"
- Cores: Cinza escuro (#34495e) e tons corporativos
- Hover: Cinza claro translúcido

## Tecnologias Utilizadas

### JavaScript (`table-sort.js`)
- Ordenação inteligente (numérica/alfabética)
- Pesquisa em tempo real
- Animações e feedback visual
- Persistência de estado durante navegação

### CSS (integrado ao `style.css`)
- Estilos responsivos
- Adaptação automática aos temas
- Transições suaves
- Indicadores visuais

## Performance

- **Ordenação**: Otimizada para tabelas com até 1000 registros
- **Pesquisa**: Filtro instantâneo sem delay
- **Memória**: Baixo impacto, reutiliza elementos DOM existentes
- **Compatibilidade**: Funciona em todos os navegadores modernos

## Futuras Melhorias

1. **Exportação**: Permitir download dos dados filtrados/ordenados
2. **Filtros avançados**: Filtros por tipo de coluna (data, número, texto)
3. **Paginação**: Para tabelas muito grandes
4. **Múltipla ordenação**: Ordenar por várias colunas simultaneamente
5. **Personalização**: Salvar preferências de ordenação do usuário

## Códigos de Exemplo

### Adicionar funcionalidade a nova tabela:
```html
<table class="sortable-table">
  <thead>
    <tr>
      <th>Coluna 1</th>
      <th>Coluna 2</th>
    </tr>
  </thead>
  <tbody>
    <!-- dados aqui -->
  </tbody>
</table>
```

### JavaScript será automaticamente aplicado a todas as tabelas com `<thead>`.

---

**Desenvolvido para Umbrella360** - Sistema de Logística Inteligente
**Data**: Janeiro 2025
**Versão**: 1.0

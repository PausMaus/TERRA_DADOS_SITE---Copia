# Sistema de Filtro por Mês - Umbrella360

## Visão Geral

O sistema de filtro por mês foi refatorado para funcionar no backend (Django views) em vez de apenas no frontend (JavaScript). Isso proporciona:

- **Melhor Performance**: Filtros aplicados na consulta do banco de dados
- **Dados Consistentes**: Dashboards e estatísticas refletem os dados filtrados
- **SEO Friendly**: URLs com parâmetros de filtro (`?mes=janeiro`)
- **Navegação Intuitiva**: Estado do filtro preservado entre páginas

## Implementação

### 1. Views (Backend)

**Funções auxiliares em `views.py`:**

```python
def get_meses_disponiveis():
    """Retorna lista de meses disponíveis nos dados"""
    meses_mot = Viagem_MOT.objects.values_list('mês', flat=True).distinct()
    meses_cam = Viagem_CAM.objects.values_list('mês', flat=True).distinct()
    todos_meses = set(meses_mot) | set(meses_cam)
    return sorted([m for m in todos_meses if m])

def aplicar_filtro_mes(queryset, mes_selecionado):
    """Aplica filtro de mês no queryset"""
    if mes_selecionado and mes_selecionado != 'todos':
        return queryset.filter(mês__iexact=mes_selecionado)
    return queryset
```

**Implementação nas views:**

```python
def report(request):
    # Obter filtro de mês
    mes_selecionado = request.GET.get('mes', 'todos')
    meses_disponiveis = get_meses_disponiveis()
    
    # Aplicar filtro nas consultas
    viagens_motoristas_base = Viagem_MOT.objects.select_related('agrupamento')
    viagens_caminhoes_base = Viagem_CAM.objects.select_related('agrupamento')
    
    viagens_motoristas_filtradas = aplicar_filtro_mes(viagens_motoristas_base, mes_selecionado)
    viagens_caminhoes_filtradas = aplicar_filtro_mes(viagens_caminhoes_base, mes_selecionado)
    
    # Contexto com variáveis de filtro
    context = {
        'mes_selecionado': mes_selecionado,
        'meses_disponiveis': meses_disponiveis,
        'meses_choices': MESES_CHOICES,
        # ... outros dados
    }
```

### 2. Template Include

**Arquivo: `templates/umbrella360/includes/month_filter.html`**

Template reutilizável que renderiza o filtro de mês com:
- Dropdown com meses disponíveis
- URLs com parâmetros de filtro
- Ícones por mês
- Estado ativo/inativo

### 3. CSS Atualizado

**Arquivo: `static/umbrella360/style.css`**

```css
.month-filter-container {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 999;
}

.month-filter-toggle {
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50px;
    /* ... */
}

.filter-option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    text-decoration: none;
    /* ... */
}
```

## Uso

### Views Atualizadas

Todas as views principais foram atualizadas para suportar o filtro:

- `index(request)` - Página inicial
- `report(request)` - Relatório global
- `motoristas(request)` - Página de motoristas
- `caminhoes(request)` - Página de caminhões
- `grafico_emissoes_por_marca(request)` - Análise avançada

### Templates Atualizados

Todos os templates principais incluem o filtro:

- `index.html`
- `report.html` (template base)
- `motoristas.html` (herda de report.html)
- `caminhoes.html` (herda de report.html)
- `grafico_pizza.html` (herda de report.html)

### Como Funciona

1. **URL com Parâmetro**: `?mes=janeiro`
2. **Backend processa**: `request.GET.get('mes', 'todos')`
3. **Filtro aplicado**: `queryset.filter(mês__iexact=mes_selecionado)`
4. **Dados filtrados**: Todas as estatísticas refletem o filtro
5. **Template renderiza**: Com estado do filtro preservado

## Meses Disponíveis

O sistema detecta automaticamente os meses disponíveis nos dados:

```python
MESES_CHOICES = [
    ('todos', 'Todos os Meses'),
    ('janeiro', 'Janeiro'),
    ('fevereiro', 'Fevereiro'),
    ('março', 'Março'),
    ('abril', 'Abril'),
    ('maio', 'Maio'),
    ('junho', 'Junho'),
    ('julho', 'Julho'),
    ('agosto', 'Agosto'),
    ('setembro', 'Setembro'),
    ('outubro', 'Outubro'),
    ('novembro', 'Novembro'),
    ('dezembro', 'Dezembro'),
]
```

## Benefícios

1. **Performance**: Filtros aplicados no banco de dados
2. **Consistência**: Dashboards e estatísticas sempre sincronizados
3. **UX**: Estado preservado entre navegação
4. **SEO**: URLs compartilháveis com filtros
5. **Manutenibilidade**: Lógica centralizada no backend

## Arquivos Modificados

- `umbrella360/views.py` - Lógica de filtro
- `umbrella360/templates/umbrella360/includes/month_filter.html` - Template do filtro
- `umbrella360/templates/umbrella360/report.html` - Template base
- `umbrella360/templates/umbrella360/index.html` - Página inicial
- `umbrella360/templates/umbrella360/motoristas.html` - Página de motoristas
- `umbrella360/static/umbrella360/style.css` - Estilos do filtro

## Exemplo de Uso

```html
<!-- No template -->
{% include 'umbrella360/includes/month_filter.html' %}

<!-- URLs geradas -->
<a href="?mes=janeiro">Janeiro</a>
<a href="?mes=todos">Todos os Meses</a>
```

```python
# Na view
mes_selecionado = request.GET.get('mes', 'todos')
viagens_filtradas = aplicar_filtro_mes(viagens_base, mes_selecionado)
```

O sistema agora fornece uma experiência robusta e consistente de filtro por mês em todas as páginas da aplicação.

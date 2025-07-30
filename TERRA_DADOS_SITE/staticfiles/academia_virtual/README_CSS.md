# Academia Virtual - Documentação CSS

## 📁 Estrutura do CSS

O arquivo `style.css` foi completamente refatorado seguindo as melhores práticas de organização e manutenibilidade.

### 🎨 Sistema de Design

#### Variáveis CSS (CSS Custom Properties)
```css
:root {
    /* Cores principais, áreas da academia, neutros */
    /* Sistema de sombras (xs, sm, md, lg, xl, 2xl) */
    /* Sistema de transições (fast, normal, slow, bounce) */
    /* Sistema de bordas (xs até 3xl + full) */
    /* Sistema de espaçamentos (xs até 3xl) */
    /* Sistema de tipografia (tamanhos e pesos) */
}
```

### 📐 Estrutura Organizada

1. **Reset e Base Styles** - Normalização e estilos fundamentais
2. **Layout Principal** - Header, main content, footer
3. **Seções Principais** - Hero, data importance, CTA
4. **Sistema de Botões** - Variantes, tamanhos, estados
5. **Componentes - Instrutores** - Avatares flutuantes, labels
6. **Áreas da Academia** - Cardio, musculação, fitness
7. **Componentes - Professores** - Grid de professores
8. **Sistema de Animações** - Keyframes e aplicações
9. **Sistema de Responsividade** - Mobile-first approach
10. **Classes Utilitárias** - Helpers para desenvolvimento

### 🎯 Áreas da Academia

#### Cores por Área:
- **Cardio**: `#e74c3c` (vermelho)
- **Musculação**: `#2ecc71` (verde)
- **Fitness**: `#9b59b6` (roxo)

#### Equipamentos:
Cada área possui equipamentos com:
- Ícones interativos (80-90px)
- Labels permanentes
- Hover effects
- Click animations
- Cores específicas da área

### 🎨 Animações

#### Principais:
- `float` - Avatares flutuantes
- `shimmer` - Barra decorativa
- `pulse` - Feedback de clique
- `slideInUp/Down` - Entrada de elementos
- `glow` - Efeito de brilho
- `rotate` - Rotação contínua

### 📱 Responsividade

#### Breakpoints:
- **Desktop Large**: 1440px+
- **Desktop**: 1024px - 1439px
- **Tablet**: 768px - 1023px
- **Mobile**: 480px - 767px
- **Mobile Small**: até 479px

#### Sistema Mobile-First:
- Base para mobile
- Progressive enhancement
- Landscape considerations
- Touch-friendly sizes

### 🛠️ Classes Utilitárias

#### Disponíveis:
```css
/* Espaçamento */
.mb-{size}, .mt-{size}, .p-{size}

/* Tipografia */
.text-{size}, .font-{weight}, .text-{align}

/* Cores */
.text-{color}

/* Layout */
.flex, .grid, .items-{align}, .justify-{content}

/* Interação */
.hover-{effect}, .cursor-{type}

/* Estados */
.disabled, .loading, .hidden, .visible
```

### 🔧 Manutenção

#### Para adicionar nova área da academia:
1. Definir cores na seção de variáveis
2. Criar classe `.{nome}-area`
3. Adicionar estilos específicos seguindo o padrão existente

#### Para adicionar novo equipamento:
1. Adicionar no HTML dentro da área apropriada
2. Usar classes `.equipment-avatar`, `.equipment-icon`, `.equipment-label`
3. As cores serão herdadas automaticamente da área pai

#### Para modificar animações:
1. Verificar se existe keyframe apropriado
2. Aplicar via classe ou propriedade `animation`
3. Considerar performance em dispositivos móveis

### ⚡ Performance

#### Otimizações implementadas:
- CSS Variables para facilitar mudanças
- Seletores eficientes
- Transições suaves
- Animações com `transform` (GPU-accelerated)
- Media queries organizadas

#### Próximos passos:
- Critical CSS inline
- Lazy loading de estilos não críticos
- Purge CSS para remover estilos não utilizados

### 🎨 Paleta de Cores

#### Primárias:
- Azul: `#0984e3` / `#74b9ff`
- Laranja: `#ff6b35` / `#ff7f50`
- Amarelo: `#fff700`

#### Áreas:
- Cardio: `#e74c3c` (vermelho energia)
- Musculação: `#2ecc71` (verde força)
- Fitness: `#9b59b6` (roxo flexibilidade)

#### Neutros:
- Escala de cinzas de 100 a 900
- Branco e preto semânticos

### 📝 Convenções

#### Nomenclatura:
- BEM-like para componentes complexos
- Kebab-case para classes
- Semantic naming para utilities

#### Organização:
- Mobile-first media queries
- Logical property grouping
- Consistent spacing with variables
- Performance-conscious animations

### 🔮 Funcionalidades Futuras

#### Planejadas:
- Modo escuro
- Temas personalizáveis
- Mais animações interativas
- Sistema de notificações
- Modais de equipamentos
- Navegação entre áreas

#### Sistema de Temas:
```css
[data-theme="dark"] {
    --primary-blue: #4a90e2;
    --background: #1a1a1a;
    /* ... */
}
```

---

**Última atualização**: Dezembro 2024  
**Versão**: 2.0 (Refatorada)  
**Compatibilidade**: IE11+, Chrome 60+, Firefox 55+, Safari 12+

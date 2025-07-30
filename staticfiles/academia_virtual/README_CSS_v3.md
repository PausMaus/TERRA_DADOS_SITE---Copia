# Academia Virtual - CSS Documentation v3.0

Este documento descreve a arquitetura CSS da Academia Virtual, projetada para performance, manutenibilidade e experiência do usuário otimizada.

## 📋 Índice

1. [Arquitetura e Organização](#arquitetura-e-organização)
2. [Design Tokens](#design-tokens)
3. [Sistema de Componentes](#sistema-de-componentes)
4. [Performance e Otimizações](#performance-e-otimizações)
5. [Responsividade](#responsividade)
6. [Acessibilidade](#acessibilidade)
7. [Guia de Manutenção](#guia-de-manutenção)

## 🏗️ Arquitetura e Organização

### Estrutura do Arquivo
```
1. Design Tokens (Variáveis CSS)
2. Estilos Base e Reset
3. Layout Principal
4. Componentes Core
5. Componentes Específicos
6. Estados e Interações
7. Animações
8. Media Queries
9. Classes Utilitárias
10. Comentários de Funcionalidades Futuras
11. Otimizações de Performance
12. Debug Utilities
```

### Metodologia
- **Mobile-first**: Design responsivo começando pelos dispositivos móveis
- **Component-based**: Cada componente é independente e reutilizável
- **Performance-first**: Otimizado para GPU e carregamento rápido
- **Accessibility-first**: Suporte completo a tecnologias assistivas

## 🎨 Design Tokens

### Sistema de Cores
```css
/* Cores Primárias */
--color-primary: #0984e3        /* Azul principal */
--color-secondary: #ff6b35      /* Laranja complementar */
--color-accent: #fff700         /* Amarelo destaque */

/* Cores das Áreas do Ginásio */
--color-cardio: #e74c3c         /* Vermelho energético */
--color-musculacao: #2ecc71     /* Verde força */
--color-fitness: #9b59b6        /* Roxo bem-estar */

/* Escala de Neutros (50-900) */
--color-gray-[50-900]           /* Sistema completo de cinzas */
```

### Sistema Tipográfico
```css
/* Escala Modular (1.25) */
--font-size-xs: 0.75rem         /* 12px */
--font-size-base: 1rem          /* 16px */
--font-size-6xl: 3.75rem        /* 60px */

/* Pesos e Altura de Linha */
--font-weight-[light-extrabold]
--line-height-[tight-loose]
```

### Espaçamento
```css
/* Escala baseada em múltiplos de 4px */
--space-1: 0.25rem              /* 4px */
--space-24: 6rem                /* 96px */
```

## 🧩 Sistema de Componentes

### Componentes Core
- **Container System**: Layout responsivo centralizado
- **Card Components**: Cartões com sombras e bordas arredondadas
- **Button System**: Botões primários, secundários e estados
- **Navigation**: Cabeçalho e navegação principais

### Componentes Específicos
- **Gym Areas**: Áreas do ginásio com cores temáticas
- **Avatar System**: Instrutores e equipamentos flutuantes
- **Feature Cards**: Cartões de funcionalidades
- **Equipment Avatars**: Equipamentos interativos

## ⚡ Performance e Otimizações

### Otimizações Implementadas
```css
/* Aceleração GPU */
.will-change-transform { will-change: transform; }

/* Containment para performance de layout */
.contain-strict { contain: strict; }

/* Clamp para design responsivo */
.text-responsive { font-size: clamp(1rem, 2.5vw, 1.5rem); }
```

### Estratégias de Performance
- **Critical CSS**: Estilos essenciais carregados primeiro
- **GPU Acceleration**: Transform e opacity otimizados
- **Layout Containment**: Isolamento de recálculos de layout
- **Lazy Loading Ready**: Preparado para carregamento sob demanda

## 📱 Responsividade

### Breakpoints
```css
--bp-sm: 640px     /* Tablets pequenos */
--bp-md: 768px     /* Tablets */
--bp-lg: 1024px    /* Laptops */
--bp-xl: 1280px    /* Desktops */
--bp-2xl: 1536px   /* Telas grandes */
```

### Estratégia Mobile-First
1. Estilos base para mobile (320px+)
2. Progressivamente melhorados para telas maiores
3. Grid layouts adaptáveis
4. Tipografia responsiva com clamp()

## ♿ Acessibilidade

### Recursos Implementados
```css
/* Foco visível */
:focus-visible { outline: 2px solid var(--color-primary); }

/* Texto oculto para screen readers */
.visually-hidden { /* Implementação completa */ }

/* Skip links para navegação por teclado */
.skip-link { /* Para ir direto ao conteúdo */ }

/* Redução de movimento */
@media (prefers-reduced-motion: reduce) { /* Animações desabilitadas */ }

/* Alto contraste */
@media (prefers-contrast: high) { /* Cores ajustadas */ }
```

### Conformidade
- **WCAG 2.1 AA**: Contraste, navegação por teclado, screen readers
- **Semantic HTML**: Estrutura semântica correta
- **ARIA Labels**: Onde necessário para contexto adicional

## 🔧 Guia de Manutenção

### Adicionando Novos Componentes
1. **Defina tokens** primeiro nas variáveis CSS
2. **Crie o componente** na seção apropriada
3. **Adicione responsividade** se necessário
4. **Teste acessibilidade** com screen readers
5. **Documente** mudanças neste arquivo

### Modificando Cores
```css
/* ✅ Correto - Use tokens */
.new-component {
    background-color: var(--color-primary);
}

/* ❌ Incorreto - Valores hardcoded */
.new-component {
    background-color: #0984e3;
}
```

### Adicionando Animações
```css
/* ✅ Use as variáveis de duração e easing */
.animation {
    transition: transform var(--duration-300) var(--easing-out);
}

/* ✅ Sempre respeite prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
    .animation {
        transition: none;
    }
}
```

### Classes Utilitárias Disponíveis
```css
/* Layout */
.flex-center, .grid-center, .margin-inline-auto

/* Aspectos */
.aspect-square, .aspect-video, .aspect-photo

/* Interação */
.hover-scale, .hover-lift, .hover-glow

/* Performance */
.will-change-transform, .contain-layout

/* Acessibilidade */
.visually-hidden, .skip-link
```

## 🎯 Futuras Melhorias

### Planejadas
- [ ] **Modo Escuro**: Implementação completa do dark mode
- [ ] **CSS Container Queries**: Para componentes verdadeiramente responsivos
- [ ] **CSS Layers**: Melhor controle de cascata
- [ ] **Subgrid**: Layouts mais complexos
- [ ] **View Transitions**: Transições suaves entre páginas

### Experimentais
- [ ] **CSS Houdini**: Animações customizadas
- [ ] **Scroll Timeline**: Animações baseadas em scroll
- [ ] **Anchor Positioning**: Posicionamento relativo a elementos

## 📊 Métricas de Performance

### Tamanhos (Aproximados)
- **Arquivo original**: ~65KB
- **Minificado**: ~50KB  
- **Gzipped**: ~15KB
- **Critical CSS**: ~10KB

### Otimizações de Rendering
- **Layout Shifts**: Minimizados com containment
- **Paint Complexity**: Reduzida com will-change
- **Composite Layers**: Otimizadas para GPU

---

## 📝 Changelog

### v3.0 (Atual)
- ✅ Adicionadas otimizações de performance modernas
- ✅ Sistema completo de utilitários CSS
- ✅ Suporte aprimorado para acessibilidade
- ✅ Preparação para dark mode
- ✅ Classes de debug para desenvolvimento
- ✅ CSS Logical Properties para internacionalização
- ✅ Aspect ratio utilities
- ✅ Modern layout helpers

### v2.0
- ✅ Sistema de design tokens completo
- ✅ Refatoração da arquitetura CSS
- ✅ Implementação mobile-first
- ✅ Sistema de componentes modular

### v1.0
- ✅ Implementação inicial
- ✅ Layout básico responsivo
- ✅ Componentes principais

---

## 🛠️ Ferramentas Recomendadas

### Desenvolvimento
- **PostCSS**: Para autoprefixer e otimizações
- **PurgeCSS**: Para remover CSS não utilizado
- **Stylelint**: Para linting e consistência

### Performance
- **Lighthouse**: Auditoria de performance
- **WebPageTest**: Análise detalhada de carregamento
- **Chrome DevTools**: Profiling de rendering

### Acessibilidade
- **axe DevTools**: Auditoria de acessibilidade
- **WAVE**: Análise visual de acessibilidade
- **Screen Readers**: Teste com NVDA, JAWS, VoiceOver

---

**Mantenedores**: Equipe de Desenvolvimento Terra Dados  
**Última atualização**: 2024  
**Próxima revisão**: A definir

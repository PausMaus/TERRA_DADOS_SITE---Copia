# Sistema de Temas - Umbrella360

## Visão Geral

O sistema de temas do Umbrella360 permite alternar entre três temas visuais distintos:

1. **Tema Padrão: "Noite de Verão"** - Tons de azul e roxo com gradientes vibrantes
2. **Tema Alternativo: "Café"** - Tons de marrom inspirados no café, com cores quentes e aconchegantes
3. **Tema Empresarial: "Empresarial"** - Tons sóbrios e modernos, ideal para ambiente corporativo

## Funcionalidades

### 🎨 Alternância de Temas
- Botão flutuante no canto superior direito
- Ícones intuitivos: ☕ (Café), 🌙 (Noite de Verão), 💼 (Empresarial)
- Transição suave entre temas (0.5s)
- Animação de rotação no ícone ao passar o mouse
- Rotação cíclica: Noite de Verão → Café → Empresarial → Noite de Verão

### 💾 Persistência
- Preferência do tema salva no localStorage
- Tema aplicado automaticamente ao recarregar a página
- Mantém consistência entre todas as páginas

### 📱 Responsividade
- Botão adaptado para dispositivos móveis
- Funciona perfeitamente em telas pequenas
- Posicionamento otimizado para diferentes tamanhos

## Paleta de Cores

### Tema "Noite de Verão"
- **Primária**: #667eea (azul)
- **Secundária**: #764ba2 (roxo)
- **Accent**: #28e48c (verde)
- **Complementar**: #f41aff (magenta)

### Tema "Café"
- **Primária**: #8B4513 (marrom escuro)
- **Secundária**: #A0522D (marrom médio)
- **Accent**: #D2691E (laranja chocolate)
- **Complementar**: #F5DEB3 (bege claro)
- **Neutro**: #DEB887 (bege escuro)

### Tema "Empresarial"
- **Primária**: #007bff (azul corporativo)
- **Secundária**: #6c757d (cinza)
- **Accent**: #343a40 (cinza escuro)
- **Complementar**: #f8f9fa (branco suave)
- **Neutro**: #495057 (cinza médio)

## Estrutura dos Arquivos

### CSS (`style.css`)
- Estilos base (tema padrão)
- Estilos específicos para tema café (`.tema-cafe`)
- Transições e animações
- Responsividade

### JavaScript (`theme-toggle.js`)
- Controle de alternância de temas
- Gerenciamento do localStorage
- Aplicação dinâmica dos estilos
- Inicialização automática

### Templates
- `report.html`: Template base com o botão de tema
- `index.html`: Página inicial com o botão de tema
- Outros templates herdam automaticamente

## Como Usar

### Para o Usuário
1. Clique no botão flutuante no canto superior direito
2. O tema mudará instantaneamente
3. A preferência será salva automaticamente

### Para Desenvolvedores

#### Adicionar novos elementos ao tema café:
```css
body.tema-cafe .novo-elemento {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
    color: #F5DEB3;
    border: 2px solid #8B4513;
}
```

#### Adicionar novos elementos ao tema empresarial:
```css
body.tema-empresarial .novo-elemento {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #343a40;
    border: 1px solid #dee2e6;
}
```

#### Verificar tema atual em JavaScript:
```javascript
const currentTheme = getCurrentTheme();
// Retorna: 'noite-verao', 'cafe', ou 'empresarial'

const isCafeTheme = document.body.classList.contains('tema-cafe');
const isEmpresarialTheme = document.body.classList.contains('tema-empresarial');
```

#### Aplicar tema programaticamente:
```javascript
// Aplicar tema específico
setTheme('empresarial');

// Ou manualmente
document.body.classList.remove('tema-cafe', 'tema-empresarial');
document.body.classList.add('tema-empresarial');
```

## Componentes Estilizados

### Elementos Base
- Header e navegação
- Botões e links
- Cards e seções
- Tabelas e formulários
- Footer

### Dashboards
- KPIs principais
- Gráficos gauge
- Barras de comparação
- Métricas de performance

### Gráficos
- Cores adaptadas para cada tema
- Backgrounds transparentes
- Bordas consistentes

## Personalização

### Adicionar Nova Cor
1. Defina a cor no tema padrão
2. Crie o equivalente no tema café
3. Aplique a classe `.tema-cafe` apropriada

### Criar Novo Tema
1. Adicione uma nova classe (ex: `.tema-oceano`)
2. Defina todas as variações de cor
3. Modifique o JavaScript para incluir o novo tema

## Exemplo de Implementação

```html
<!-- No template HTML -->
<button id="theme-toggle" class="theme-toggle">
    <span class="theme-icon">☕</span> Café
</button>
```

```css
/* No CSS */
body.tema-cafe .meu-componente {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
    color: #F5DEB3;
    transition: all 0.5s ease;
}
```

```javascript
// No JavaScript
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
```

## Benefícios

### Para Usuários
- **Personalização**: Escolha entre dois estilos visuais
- **Conforto**: Tema café oferece tons mais quentes
- **Consistência**: Tema aplicado em todas as páginas

### Para Desenvolvedores
- **Manutenibilidade**: Código organizado e bem estruturado
- **Escalabilidade**: Fácil adicionar novos temas
- **Performance**: Transições suaves sem impacto na performance

## Troubleshooting

### Tema não está sendo aplicado
1. Verifique se o JavaScript está carregado
2. Confirme se as classes CSS existem
3. Limpe o cache do navegador

### Cores não estão mudando
1. Verifique a especificidade CSS
2. Use `!important` se necessário
3. Confirme se a classe `.tema-cafe` está sendo aplicada

### Botão não está funcionando
1. Verifique se o ID `theme-toggle` está correto
2. Confirme se o event listener está sendo adicionado
3. Verifique erros no console do navegador

## Roadmap Futuro

- [ ] Adicionar mais temas (Oceano, Floresta, etc.)
- [ ] Implementar detecção automática de preferência do sistema
- [ ] Adicionar animações mais elaboradas
- [ ] Criar modo de alto contraste
- [ ] Implementar temas sazonais

## Compatibilidade

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Dispositivos móveis

## Conclusão

O sistema de temas do Umbrella360 oferece uma experiência visual rica e personalizável, mantendo a funcionalidade e usabilidade em ambos os temas. O código é modular, fácil de manter e pode ser facilmente expandido para incluir novos temas no futuro.

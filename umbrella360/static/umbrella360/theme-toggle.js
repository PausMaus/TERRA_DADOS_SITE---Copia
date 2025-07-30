// Sistema de Alternância de Temas - Umbrella360
// Tema padrão: "Noite de Verão"
// Tema alternativo: "Café"
// Tema empresarial: "Empresarial"

const TEMAS = {
    'noite-verao': {
        nome: 'Noite de Verão',
        icone: '◐',
        proximoTema: 'cafe'
    },
    'cafe': {
        nome: 'Café',
        icone: '●',
        proximoTema: 'empresarial'
    },
    'empresarial': {
        nome: 'Empresarial',
        icone: '■',
        proximoTema: 'noite-verao'
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar o tema baseado no localStorage
    initializeTheme();
    
    // Adicionar event listener para o botão de alternância
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

function initializeTheme() {
    const currentTheme = localStorage.getItem('umbrella360-theme') || 'noite-verao';
    applyTheme(currentTheme);
}

function toggleTheme() {
    const currentTheme = getCurrentTheme();
    const newTheme = TEMAS[currentTheme].proximoTema;
    
    applyTheme(newTheme);
    localStorage.setItem('umbrella360-theme', newTheme);
    
    // Adicionar animação suave
    animateThemeChange();
}

function getCurrentTheme() {
    const body = document.body;
    if (body.classList.contains('tema-cafe')) {
        return 'cafe';
    } else if (body.classList.contains('tema-empresarial')) {
        return 'empresarial';
    }
    return 'noite-verao';
}

function applyTheme(theme) {
    const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');
    
    // Remover todas as classes de tema
    body.classList.remove('tema-cafe', 'tema-empresarial');
    
    // Aplicar o tema apropriado
    if (theme === 'cafe') {
        body.classList.add('tema-cafe');
    } else if (theme === 'empresarial') {
        body.classList.add('tema-empresarial');
    }
    
    // Atualizar o botão para mostrar o tema atual
    if (themeToggle && TEMAS[theme]) {
        const temaAtualInfo = TEMAS[theme];
        const proximoTema = TEMAS[theme].proximoTema;
        const proximoTemaInfo = TEMAS[proximoTema];
        
        themeToggle.innerHTML = `<span class="theme-icon">${temaAtualInfo.icone}</span> ${temaAtualInfo.nome}`;
        themeToggle.setAttribute('title', `Tema atual: ${temaAtualInfo.nome}. Clique para alternar para ${proximoTemaInfo.nome}`);
    }
}

// Função para detectar preferência do sistema (opcional)
function detectSystemTheme() {
    const hour = new Date().getHours();
    
    // Lógica baseada no horário
    if (hour >= 9 && hour <= 17) {
        return 'empresarial'; // Horário comercial
    } else if (hour >= 18 && hour <= 23) {
        return 'cafe'; // Noite
    }
    return 'noite-verao'; // Madrugada/manhã
}

// Aplicar animação suave na mudança de tema
function animateThemeChange() {
    const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');
    
    // Adicionar classe de transição
    body.style.transition = 'all 0.5s ease';
    
    // Animação no botão
    if (themeToggle) {
        themeToggle.style.transform = 'scale(0.95)';
        setTimeout(() => {
            themeToggle.style.transform = 'scale(1)';
        }, 150);
    }
    
    // Remover transição após a animação
    setTimeout(() => {
        body.style.transition = '';
    }, 500);
}

// Função para obter informações sobre todos os temas
function getTemaInfo() {
    return TEMAS;
}

// Função para aplicar tema específico (útil para debugging)
function setTheme(themeName) {
    if (TEMAS[themeName]) {
        applyTheme(themeName);
        localStorage.setItem('umbrella360-theme', themeName);
    }
}

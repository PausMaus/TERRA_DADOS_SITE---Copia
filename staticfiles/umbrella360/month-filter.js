// Sistema de Filtro de Meses - Umbrella360
// Filtro flutuante para seleção de mês

const MESES = {
    'todos': { nome: 'Todos os Meses', icone: '' },
    'janeiro': { nome: 'Janeiro', icone: '' },
    'fevereiro': { nome: 'Fevereiro', icone: '' },
    'março': { nome: 'Março', icone: '' },
    'abril': { nome: 'Abril', icone: '' },
    'maio': { nome: 'Maio', icone: '' },
    'junho': { nome: 'Junho', icone: '' },
    'julho': { nome: 'Julho', icone: '' },
    'agosto': { nome: 'Agosto', icone: '' },
    'setembro': { nome: 'Setembro', icone: '' },
    'outubro': { nome: 'Outubro', icone: '' },
    'novembro': { nome: 'Novembro', icone: '' },
    'dezembro': { nome: 'Dezembro', icone: '' }
};

let currentFilter = 'todos';
let filterDropdownVisible = false;

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar o filtro
    initializeFilter();
    
    // Adicionar event listeners
    const filterToggle = document.getElementById('month-filter-toggle');
    const filterDropdown = document.getElementById('month-filter-dropdown');
    
    if (filterToggle) {
        filterToggle.addEventListener('click', toggleFilterDropdown);
    }
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.month-filter-container')) {
            closeFilterDropdown();
        }
    });
    
    // Adicionar listeners para os itens do dropdown
    setupDropdownListeners();
});

function initializeFilter() {
    const savedFilter = localStorage.getItem('umbrella360-month-filter') || 'todos';
    applyFilter(savedFilter);
}

function toggleFilterDropdown() {
    const dropdown = document.getElementById('month-filter-dropdown');
    const toggle = document.getElementById('month-filter-toggle');
    
    if (filterDropdownVisible) {
        closeFilterDropdown();
    } else {
        openFilterDropdown();
    }
}

function openFilterDropdown() {
    const dropdown = document.getElementById('month-filter-dropdown');
    const toggle = document.getElementById('month-filter-toggle');
    
    if (dropdown) {
        dropdown.classList.add('visible');
        filterDropdownVisible = true;
        
        // Animar o toggle
        toggle.style.transform = 'rotate(180deg)';
        
        // Popular o dropdown
        populateDropdown();
    }
}

function closeFilterDropdown() {
    const dropdown = document.getElementById('month-filter-dropdown');
    const toggle = document.getElementById('month-filter-toggle');
    
    if (dropdown) {
        dropdown.classList.remove('visible');
        filterDropdownVisible = false;
        
        // Resetar animação
        if (toggle) {
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

function populateDropdown() {
    const dropdown = document.getElementById('month-filter-dropdown');
    if (!dropdown) return;
    
    let html = '';
    Object.keys(MESES).forEach(mesKey => {
        const mes = MESES[mesKey];
        const isActive = mesKey === currentFilter;
        
        html += `
            <div class="filter-item ${isActive ? 'active' : ''}" data-filter="${mesKey}">
                <span class="filter-name">${mes.nome}</span>
                ${isActive ? '<span class="filter-check">✓</span>' : ''}
            </div>
        `;
    });
    
    dropdown.innerHTML = html;
    setupDropdownListeners();
}

function setupDropdownListeners() {
    const filterItems = document.querySelectorAll('.filter-item');
    
    filterItems.forEach(item => {
        item.addEventListener('click', function() {
            const filterValue = this.getAttribute('data-filter');
            selectFilter(filterValue);
        });
    });
}

function selectFilter(filterValue) {
    applyFilter(filterValue);
    localStorage.setItem('umbrella360-month-filter', filterValue);
    closeFilterDropdown();
    
    // Aplicar animação
    animateFilterChange();
}

function applyFilter(filter) {
    currentFilter = filter;
    updateFilterButton();
    filterTableRows();
    updatePageTitle();
}

function updateFilterButton() {
    const toggle = document.getElementById('month-filter-toggle');
    if (toggle && MESES[currentFilter]) {
        const mes = MESES[currentFilter];
        toggle.innerHTML = `${mes.nome}`;
        toggle.setAttribute('title', `Filtro atual: ${mes.nome}`);
    }
}

function filterTableRows() {
    const tables = document.querySelectorAll('table');
    let totalVisible = 0;
    let totalRows = 0;
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            totalRows++;
            
            if (currentFilter === 'todos') {
                row.style.display = '';
                totalVisible++;
                return;
            }
            
            // Procurar por dados de mês nos atributos data-* ou no conteúdo
            let monthData = row.getAttribute('data-month') || '';
            
            // Se não encontrar data-month, procurar nas células
            if (!monthData) {
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {
                    const text = cell.textContent.toLowerCase().trim();
                    
                    // Verificar se a célula contém o nome do mês
                    const monthNames = {
                        'janeiro': 'janeiro', 'jan': 'janeiro',
                        'fevereiro': 'fevereiro', 'fev': 'fevereiro',
                        'março': 'março', 'mar': 'março',
                        'abril': 'abril', 'abr': 'abril',
                        'maio': 'maio', 'mai': 'maio',
                        'junho': 'junho', 'jun': 'junho',
                        'julho': 'julho', 'jul': 'julho',
                        'agosto': 'agosto', 'ago': 'agosto',
                        'setembro': 'setembro', 'set': 'setembro',
                        'outubro': 'outubro', 'out': 'outubro',
                        'novembro': 'novembro', 'nov': 'novembro',
                        'dezembro': 'dezembro', 'dez': 'dezembro'
                    };
                    
                    Object.keys(monthNames).forEach(key => {
                        if (text.includes(key)) {
                            monthData = monthNames[key];
                        }
                    });
                    
                    // Verificar formato de data (01/2024, 2024-01, etc.)
                    const dateRegex = /(\d{1,2})[\/\-](\d{4})/;
                    const match = text.match(dateRegex);
                    if (match) {
                        const month = parseInt(match[1]);
                        const monthsArray = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                                           'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
                        if (month >= 1 && month <= 12) {
                            monthData = monthsArray[month - 1];
                        }
                    }
                });
            }
            
            const shouldShow = monthData.toLowerCase() === currentFilter.toLowerCase();
            row.style.display = shouldShow ? '' : 'none';
            
            if (shouldShow) {
                totalVisible++;
            }
        });
    });
    
    // Atualizar contador se necessário
    updateFilterCount(totalVisible, totalRows);
}

function updateFilterCount(visible, total) {
    const toggle = document.getElementById('month-filter-toggle');
    const existingCount = toggle.querySelector('.filter-count');
    
    if (currentFilter !== 'todos') {
        if (!existingCount) {
            const countSpan = document.createElement('span');
            countSpan.className = 'filter-count';
            toggle.appendChild(countSpan);
        }
        
        const countElement = toggle.querySelector('.filter-count');
        countElement.textContent = visible;
        
        // Adicionar classe para indicar filtro ativo
        toggle.classList.add('filtered');
    } else {
        if (existingCount) {
            existingCount.remove();
        }
        toggle.classList.remove('filtered');
    }
}

// Função para detectar meses disponíveis nos dados (melhorada)
function getAvailableMonths() {
    const tables = document.querySelectorAll('table tbody tr');
    const months = new Set();
    
    tables.forEach(row => {
        // Primeiro, verificar se há atributo data-month
        const monthData = row.getAttribute('data-month');
        if (monthData && MESES[monthData.toLowerCase()]) {
            months.add(monthData.toLowerCase());
            return;
        }
        
        // Se não, procurar nas células
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            const text = cell.textContent.toLowerCase().trim();
            
            // Verificar nomes de meses
            Object.keys(MESES).forEach(mesKey => {
                if (mesKey !== 'todos' && text.includes(mesKey)) {
                    months.add(mesKey);
                }
            });
            
            // Verificar formatos de data
            const dateRegex = /(\d{1,2})[\/\-](\d{4})/;
            const match = text.match(dateRegex);
            if (match) {
                const month = parseInt(match[1]);
                const monthsArray = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                                   'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
                if (month >= 1 && month <= 12) {
                    months.add(monthsArray[month - 1]);
                }
            }
        });
    });
    
    return Array.from(months);
}

// Função melhorada para popular dropdown
function populateDropdown() {
    const dropdown = document.getElementById('month-filter-dropdown');
    if (!dropdown) return;
    
    const availableMonths = getAvailableMonths();
    
    let html = '';
    
    // Adicionar "Todos os Meses" sempre
    const isAllActive = currentFilter === 'todos';
    html += `
        <div class="filter-item ${isAllActive ? 'active' : ''}" data-filter="todos">
            <span class="filter-name">${MESES['todos'].nome}</span>
            ${isAllActive ? '<span class="filter-check">✓</span>' : ''}
        </div>
    `;
    
    if (availableMonths.length > 0) {
        html += '<div class="filter-separator"></div>';
        
        // Adicionar apenas os meses disponíveis
        const sortedMonths = availableMonths.sort((a, b) => {
            const monthOrder = Object.keys(MESES);
            return monthOrder.indexOf(a) - monthOrder.indexOf(b);
        });
        
        sortedMonths.forEach(mesKey => {
            if (MESES[mesKey]) {
                const mes = MESES[mesKey];
                const isActive = mesKey === currentFilter;
                
                html += `
                    <div class="filter-item ${isActive ? 'active' : ''}" data-filter="${mesKey}">
                        <span class="filter-name">${mes.nome}</span>
                        ${isActive ? '<span class="filter-check">✓</span>' : ''}
                    </div>
                `;
            }
        });
    }
    
    dropdown.innerHTML = html;
    setupDropdownListeners();
}

// Função para resetar filtro
function resetFilter() {
    selectFilter('todos');
}

// Função para aplicar filtro específico (útil para debugging)
function setMonthFilter(month) {
    if (MESES[month]) {
        selectFilter(month);
    }
}

// Função para obter informações do filtro atual
function getCurrentFilter() {
    return currentFilter;
}

// Função para obter todos os meses disponíveis
function getAllMonths() {
    return MESES;
}

function updatePageTitle() {
    const pageTitle = document.querySelector('h1, .h2');
    if (pageTitle && currentFilter !== 'todos') {
        const originalTitle = pageTitle.getAttribute('data-original-title') || pageTitle.textContent;
        pageTitle.setAttribute('data-original-title', originalTitle);
        pageTitle.textContent = `${originalTitle} - ${MESES[currentFilter].nome}`;
    } else if (pageTitle && currentFilter === 'todos') {
        const originalTitle = pageTitle.getAttribute('data-original-title');
        if (originalTitle) {
            pageTitle.textContent = originalTitle;
        }
    }
}

function animateFilterChange() {
    const toggle = document.getElementById('month-filter-toggle');
    if (toggle) {
        toggle.style.transform = 'scale(0.95)';
        setTimeout(() => {
            toggle.style.transform = 'scale(1)';
        }, 150);
    }
    
    // Animar tabelas
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.style.opacity = '0.7';
        setTimeout(() => {
            table.style.opacity = '1';
        }, 300);
    });
}

// Sistema de Ordenação Interativa de Tabelas - Umbrella360
// Permite ordenar tabelas clicando nos cabeçalhos

document.addEventListener('DOMContentLoaded', function() {
    initializeSortableTables();
});

function initializeSortableTables() {
    // Encontrar todas as tabelas com classe 'sortable' ou que tenham thead
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        const thead = table.querySelector('thead');
        if (thead) {
            makeSortable(table);
            addRecordCounter(table);
            
            // Adicionar pesquisa apenas para tabelas com mais de 5 linhas
            const tbody = table.querySelector('tbody');
            const rows = tbody ? tbody.querySelectorAll('tr') : [];
            if (rows.length > 5) {
                addTableSearch(table);
            }
        }
    });
}

function makeSortable(table) {
    const headers = table.querySelectorAll('thead th');
    
    headers.forEach((header, index) => {
        // Adicionar cursor pointer e estilos para indicar que é clicável
        header.style.cursor = 'pointer';
        header.style.userSelect = 'none';
        header.style.position = 'relative';
        
        // Adicionar indicador visual de ordenação
        const sortIndicator = document.createElement('span');
        sortIndicator.className = 'sort-indicator';
        sortIndicator.innerHTML = ' ↕';
        sortIndicator.style.marginLeft = '5px';
        sortIndicator.style.opacity = '0.5';
        header.appendChild(sortIndicator);
        
        // Adicionar evento de clique
        header.addEventListener('click', () => {
            sortTable(table, index, header);
        });
    });
}

function sortTable(table, columnIndex, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Adicionar indicador de carregamento
    table.classList.add('sorting');
    
    // Determinar direção da ordenação
    const currentSort = header.getAttribute('data-sort') || 'none';
    const newSort = currentSort === 'asc' ? 'desc' : 'asc';
    
    // Limpar indicadores de outros headers
    const allHeaders = table.querySelectorAll('thead th');
    allHeaders.forEach(h => {
        h.setAttribute('data-sort', 'none');
        const indicator = h.querySelector('.sort-indicator');
        if (indicator) {
            indicator.innerHTML = ' ↕';
            indicator.style.opacity = '0.5';
        }
    });
    
    // Definir novo estado de ordenação
    header.setAttribute('data-sort', newSort);
    const indicator = header.querySelector('.sort-indicator');
    if (indicator) {
        indicator.innerHTML = newSort === 'asc' ? ' ↑' : ' ↓';
        indicator.style.opacity = '1';
        indicator.style.color = newSort === 'asc' ? '#27ae60' : '#e74c3c';
    }
    
    // Simular delay para animação suave
    setTimeout(() => {
        // Ordenar linhas
        const sortedRows = rows.sort((a, b) => {
            const aCell = a.cells[columnIndex];
            const bCell = b.cells[columnIndex];
            
            if (!aCell || !bCell) return 0;
            
            const aValue = getCellValue(aCell);
            const bValue = getCellValue(bCell);
            
            let comparison = 0;
            
            // Tentar comparação numérica primeiro
            const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                comparison = aNum - bNum;
            } else {
                // Comparação alfabética
                comparison = aValue.localeCompare(bValue, 'pt-BR', {
                    numeric: true,
                    sensitivity: 'base'
                });
            }
            
            return newSort === 'asc' ? comparison : -comparison;
        });
        
        // Reorganizar a tabela
        tbody.innerHTML = '';
        sortedRows.forEach(row => tbody.appendChild(row));
        
        // Remover indicador de carregamento
        table.classList.remove('sorting');
        
        // Adicionar animação sutil
        animateTableSort(table);
        
        // Destacar a coluna ordenada temporariamente
        highlightSortedColumn(table, columnIndex);
        
    }, 150);
}

function getCellValue(cell) {
    // Extrair texto da célula, removendo espaços extras
    const text = cell.textContent || cell.innerText || '';
    return text.trim();
}

function animateTableSort(table) {
    // Adicionar classe de animação
    table.style.transition = 'opacity 0.2s ease';
    table.style.opacity = '0.8';
    
    setTimeout(() => {
        table.style.opacity = '1';
    }, 100);
    
    setTimeout(() => {
        table.style.transition = '';
    }, 200);
}

// Função para adicionar estilos CSS dinâmicos
function addSortableStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .sortable-table th {
            transition: background-color 0.2s ease;
        }
        
        .sortable-table th:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .sortable-table th[data-sort="asc"] {
            background-color: rgba(52, 152, 219, 0.1);
        }
        
        .sortable-table th[data-sort="desc"] {
            background-color: rgba(231, 76, 60, 0.1);
        }
        
        .sort-indicator {
            font-weight: bold;
            font-size: 0.9em;
        }
        
        /* Estilos para diferentes temas */
        .tema-cafe .sortable-table th:hover {
            background-color: rgba(139, 69, 19, 0.1);
        }
        
        .tema-empresarial .sortable-table th:hover {
            background-color: rgba(52, 73, 94, 0.1);
        }
        
        .sorted-column {
            background-color: rgba(255, 223, 186, 0.5) !important;
            transition: background-color 0.5s ease;
        }
        
        .record-counter {
            text-align: right;
            font-size: 0.9em;
            color: #666;
            margin-top: 0.5rem;
            font-style: italic;
        }
        
        .table-search-container {
            margin-bottom: 1rem;
            text-align: right;
        }
        
        .table-search {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-width: 200px;
            font-size: 0.9em;
        }
    `;
    document.head.appendChild(style);
}

// Inicializar estilos quando a página carrega
document.addEventListener('DOMContentLoaded', addSortableStyles);

// Função para resetar ordenação de uma tabela
function resetTableSort(table) {
    const headers = table.querySelectorAll('thead th');
    headers.forEach(header => {
        header.setAttribute('data-sort', 'none');
        const indicator = header.querySelector('.sort-indicator');
        if (indicator) {
            indicator.innerHTML = ' ↕';
            indicator.style.opacity = '0.5';
        }
    });
}

// Função para destacar coluna ordenada temporariamente
function highlightSortedColumn(table, columnIndex) {
    // Remover destaques anteriores
    const allCells = table.querySelectorAll('td, th');
    allCells.forEach(cell => cell.classList.remove('sorted-column'));
    
    // Destacar coluna atual
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cell = row.cells[columnIndex];
        if (cell) {
            cell.classList.add('sorted-column');
        }
    });
    
    // Remover destaque após 2 segundos
    setTimeout(() => {
        allCells.forEach(cell => cell.classList.remove('sorted-column'));
    }, 2000);
}

// Função para adicionar contador de registros
function addRecordCounter(table) {
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    // Criar elemento contador se não existir
    let counter = table.parentNode.querySelector('.record-counter');
    if (!counter) {
        counter = document.createElement('div');
        counter.className = 'record-counter';
        counter.style.cssText = `
            text-align: right;
            font-size: 0.9em;
            color: #666;
            margin-top: 0.5rem;
            font-style: italic;
        `;
        table.parentNode.appendChild(counter);
    }
    
    counter.textContent = `Total de registros: ${rows.length}`;
}

// Função para pesquisar nas tabelas
function addTableSearch(table) {
    // Criar campo de pesquisa
    const searchContainer = document.createElement('div');
    searchContainer.className = 'table-search-container';
    searchContainer.style.cssText = `
        margin-bottom: 1rem;
        text-align: right;
    `;
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Pesquisar na tabela...';
    searchInput.className = 'table-search';
    searchInput.style.cssText = `
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-width: 200px;
        font-size: 0.9em;
    `;
    
    searchContainer.appendChild(searchInput);
    table.parentNode.insertBefore(searchContainer, table);
    
    // Implementar pesquisa
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Atualizar contador
        const visibleRows = tbody.querySelectorAll('tr:not([style*="display: none"])');
        let counter = table.parentNode.querySelector('.record-counter');
        if (counter) {
            counter.textContent = `Mostrando: ${visibleRows.length} de ${rows.length} registros`;
        }
    });
}

// Função para efeito de carregamento (opcional)
function addLoadingEffect() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        // Adicionar classe de carregamento
        table.classList.add('loading');
        
        // Simular carregamento
        setTimeout(() => {
            table.classList.remove('loading');
        }, 1000);
    });
}

// Inicializar efeito hover nas linhas
document.addEventListener('DOMContentLoaded', addRowHoverEffect);

// Inicializar contador de registros e pesquisa
document.addEventListener('DOMContentLoaded', () => {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        addRecordCounter(table);
        addTableSearch(table);
    });
});

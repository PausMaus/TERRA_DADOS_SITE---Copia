from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg, Count
from django.urls import reverse
from functools import wraps
from .models import Regiao, GoogleTrendsData
import csv
import re
import json
from datetime import datetime
from collections import defaultdict

# Decorator customizado para verificar login
def usuario_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.warning(request, 'Você precisa fazer login para acessar esta página')
            return redirect(f"{reverse('lab_01:login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    """Página inicial do Laboratorium - Análise e Correlação de Dados"""
    context = {
        'titulo': 'Laboratorium',
        'subtitulo': 'Análise e Correlação de Dados',
    }
    return render(request, 'lab_01/index.html', context)

def login_view(request):
    """View para login de usuários usando model Usuario"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            from .models import Usuario
            usuario = Usuario.objects.get(username=username)
            
            if usuario.verificar_senha(password):
                # Salvar informações na sessão
                request.session['usuario_id'] = usuario.id
                request.session['usuario_username'] = usuario.username
                messages.success(request, f'Bem-vindo, {username}!')
                next_url = request.GET.get('next', 'lab_01:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuário ou senha inválidos')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário ou senha inválidos')
    
    return render(request, 'lab_01/login.html')

def logout_view(request):
    """View para logout de usuários"""
    # Limpar sessão
    request.session.flush()
    messages.success(request, 'Você saiu com sucesso!')
    return redirect('lab_01:index')

@usuario_requerido
def importar_csv(request):
    """Importa dados do CSV para o banco de dados"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Decodificar e ler CSV
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        
        # Pular linha de categoria
        next(reader, None)
        # Pular linha em branco
        next(reader, None)
        
        # Ler cabeçalho e extrair termo e datas (linha 3)
        header = next(reader)
        match = re.search(r'(.+?):\s*\((\d{2}/\d{2}/\d{4})\s*–\s*(\d{2}/\d{2}/\d{4})\)', header[1])
        
        if not match:
            messages.error(request, 'Formato de cabeçalho inválido')
            return redirect('lab_01:index')
        
        termo = match.group(1).strip()
        data_inicial = datetime.strptime(match.group(2), '%d/%m/%Y').date()
        data_final = datetime.strptime(match.group(3), '%d/%m/%Y').date()
        
        # Processar dados
        contador = 0
        for row in reader:
            if len(row) >= 2 and row[0].strip():
                regiao_nome = row[0].strip()
                interesse = int(row[1]) if row[1].isdigit() else 0
                
                # Criar/obter região
                regiao, _ = Regiao.objects.get_or_create(nome=regiao_nome)
                
                # Criar registro de trends
                GoogleTrendsData.objects.create(
                    termo=termo,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    interesse=interesse,
                    regiao=regiao
                )
                contador += 1
        
        messages.success(request, f'{contador} registros importados com sucesso!')
        return redirect('lab_01:index')
    
    return render(request, 'lab_01/importar.html')

def correlacao(request):
    """Análise de correlação entre termos e regiões"""
    # Obter todos os termos únicos
    termos = GoogleTrendsData.objects.values_list('termo', flat=True).distinct().order_by('termo')
    
    # Obter filtros
    termo1 = request.GET.get('termo1', '')
    termo2 = request.GET.get('termo2', '')
    
    context = {
        'termos': list(termos),
        'termo1': termo1,
        'termo2': termo2,
    }
    
    # Se dois termos foram selecionados, calcular correlação
    if termo1 and termo2:
        # Buscar dados dos dois termos
        dados1 = GoogleTrendsData.objects.filter(termo=termo1).select_related('regiao')
        dados2 = GoogleTrendsData.objects.filter(termo=termo2).select_related('regiao')
        
        # Organizar por região
        regioes_dict1 = {d.regiao.nome: d.interesse for d in dados1}
        regioes_dict2 = {d.regiao.nome: d.interesse for d in dados2}
        
        # Regiões em comum
        regioes_comuns = set(regioes_dict1.keys()) & set(regioes_dict2.keys())
        
        # Preparar dados para correlação
        comparacao = []
        x_values = []
        y_values = []
        
        for regiao in sorted(regioes_comuns):
            val1 = regioes_dict1[regiao]
            val2 = regioes_dict2[regiao]
            comparacao.append({
                'regiao': regiao,
                'termo1_interesse': val1,
                'termo2_interesse': val2,
                'diferenca': abs(val1 - val2)
            })
            x_values.append(val1)
            y_values.append(val2)
        
        # Calcular correlação de Pearson
        if len(x_values) > 1:
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x ** 2 for x in x_values)
            sum_y2 = sum(y ** 2 for y in y_values)
            
            numerador = n * sum_xy - sum_x * sum_y
            denominador = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            correlacao_pearson = numerador / denominador if denominador != 0 else 0
        else:
            correlacao_pearson = 0
        
        # Estatísticas
        stats = {
            'correlacao': round(correlacao_pearson, 4),
            'regioes_analisadas': len(regioes_comuns),
            'media_termo1': round(sum(x_values) / len(x_values), 2) if x_values else 0,
            'media_termo2': round(sum(y_values) / len(y_values), 2) if y_values else 0,
            'data_inicial': 
        }
        
        context.update({
            'comparacao': sorted(comparacao, key=lambda x: x['diferenca']),
            'stats': stats,
            'chart_data': json.dumps({
                'labels': list(regioes_comuns),
                'x_values': x_values,
                'y_values': y_values,
            })
        })
    
    return render(request, 'lab_01/correlacao.html', context)


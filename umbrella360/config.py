# -*- coding: utf-8 -*-
"""
Arquivo de configuração para valores de negócio da Umbrella360.
Este arquivo centraliza todos os valores que anteriormente estavam hardcoded,
permitindo fácil manutenção e ajuste dos parâmetros de negócio.
"""

from django.core.cache import cache


class ConfiguracaoManager:
    """
    Manager para facilitar o acesso às configurações com cache.
    """
    
    # Valores padrão para configurações críticas
    DEFAULTS = {
        # Preços e custos
        'custo_diesel': 5.96,
        'media_km_objetivo': 1.78,
        
        # Limites de validação
        'consumo_maximo_normal': 15000.0,
        'consumo_limite_erro': 50000.0,
        
        # Métricas de emissão (kg CO2 por litro de diesel)
        'fator_emissao_co2': 2.68,
        
        # Configurações de interface
        'registros_por_pagina': 50,
        'cache_timeout': 300,  # 5 minutos
    }
    
    @classmethod
    def get_valor(cls, chave, default=None):
        """
        Obtém um valor de configuração com cache.
        
        Args:
            chave (str): A chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            float: O valor da configuração
        """
        cache_key = f"config_{chave}"
        valor = cache.get(cache_key)
        
        if valor is None:
            try:
                from .models import ConfiguracaoSistema
                config = ConfiguracaoSistema.objects.get(chave=chave)
                valor = config.valor
                cache.set(cache_key, valor, cls.DEFAULTS.get('cache_timeout', 300))
            except:  # Captura qualquer erro (DoesNotExist, ImportError, etc.)
                valor = default if default is not None else cls.DEFAULTS.get(chave, 0.0)
        
        return valor
    
    @classmethod
    def set_valor(cls, chave, valor, descricao="", categoria="geral"):
        """
        Define um valor de configuração e limpa o cache.
        
        Args:
            chave (str): A chave da configuração
            valor (float): O novo valor
            descricao (str): Descrição da configuração
            categoria (str): Categoria da configuração
        """
        try:
            from .models import ConfiguracaoSistema
            config, created = ConfiguracaoSistema.objects.get_or_create(
                chave=chave,
                defaults={
                    'valor': valor,
                    'descricao': descricao,
                    'categoria': categoria
                }
            )
            
            if not created:
                config.valor = valor
                config.save()
            
            # Limpar cache
            cache_key = f"config_{chave}"
            cache.delete(cache_key)
        except:  # Captura qualquer erro durante operações no banco
            pass
    
    @classmethod
    def inicializar_configuracoes(cls):
        """
        Inicializa as configurações padrão se não existirem.
        """
        configuracoes_iniciais = [
            {
                'chave': 'custo_diesel',
                'valor': 5.96,
                'descricao': 'Custo por litro do diesel em reais',
                'categoria': 'financeiro'
            },
            {
                'chave': 'media_km_objetivo',
                'valor': 1.78,
                'descricao': 'Meta de quilômetros por litro estabelecida pela empresa',
                'categoria': 'performance'
            },
            {
                'chave': 'consumo_maximo_normal',
                'valor': 15000.0,
                'descricao': 'Limite máximo de consumo considerado normal (litros)',
                'categoria': 'validacao'
            },
            {
                'chave': 'consumo_limite_erro',
                'valor': 50000.0,
                'descricao': 'Limite de consumo acima do qual é considerado erro (litros)',
                'categoria': 'validacao'
            },
            {
                'chave': 'fator_emissao_co2',
                'valor': 2.68,
                'descricao': 'Fator de emissão de CO2 por litro de diesel (kg)',
                'categoria': 'ambiental'
            },
            {
                'chave': 'registros_por_pagina',
                'valor': 50,
                'descricao': 'Número de registros por página na interface',
                'categoria': 'interface'
            }
        ]
        
        for config_data in configuracoes_iniciais:
            cls.set_valor(**config_data)


# Função de conveniência para obter configurações
def get_config(chave, default=None):
    """
    Função de conveniência para obter uma configuração.
    
    Args:
        chave (str): A chave da configuração
        default: Valor padrão se não encontrado
        
    Returns:
        float: O valor da configuração
    """
    return ConfiguracaoManager.get_valor(chave, default)


# Constantes de configuração para facilitar o uso
class Config:
    """
    Classe com métodos estáticos para acessar configurações comuns.
    """
    
    @staticmethod
    def custo_diesel():
        return get_config('custo_diesel', 5.96)
    
    @staticmethod
    def media_km_objetivo():
        return get_config('media_km_objetivo', 1.78)
    
    @staticmethod
    def media_km_atual():
        """Retorna a média km/L atual calculada dinamicamente, ou um fallback"""
        # Primeiro tenta obter o valor calculado dinamicamente
        media_calculada = get_config('media_km_atual_calculada')
        if media_calculada and media_calculada > 0:
            return media_calculada
        
        # Se não há valor calculado, calcula em tempo real
        try:
            from django.db.models import Avg
            from .models import Viagem_CAM
            
            # Filtrar dados válidos
            consumo_max = Config.consumo_maximo_normal()
            resultado = Viagem_CAM.objects.filter(
                Consumido__gt=0, 
                Consumido__lte=consumo_max
            ).aggregate(media=Avg('Quilometragem_média'))
            
            if resultado['media']:
                return float(resultado['media'])
        except:
            pass
        
        # Fallback para valor padrão conservador
        return 1.78  # Mesmo valor do objetivo como fallback
    
    @staticmethod
    def consumo_maximo_normal():
        return get_config('consumo_maximo_normal', 15000.0)
    
    @staticmethod
    def consumo_limite_erro():
        return get_config('consumo_limite_erro', 50000.0)
    
    @staticmethod
    def fator_emissao_co2():
        return get_config('fator_emissao_co2', 2.68)
    
    @staticmethod
    def registros_por_pagina():
        return int(get_config('registros_por_pagina', 50))

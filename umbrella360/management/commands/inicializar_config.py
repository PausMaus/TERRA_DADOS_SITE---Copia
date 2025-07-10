# -*- coding: utf-8 -*-
"""
Command para inicializar as configurações padrão do sistema.
"""

from django.core.management.base import BaseCommand
from umbrella360.config import ConfiguracaoManager


class Command(BaseCommand):
    help = 'Inicializa as configurações padrão do sistema Umbrella360'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Inicializando configurações padrão...'))
        
        try:
            ConfiguracaoManager.inicializar_configuracoes()
            self.stdout.write(
                self.style.SUCCESS('Configurações inicializadas com sucesso!')
            )
            
            # Listar as configurações criadas
            from umbrella360.models import ConfiguracaoSistema
            configuracoes = ConfiguracaoSistema.objects.all().order_by('categoria', 'chave')
            
            self.stdout.write('\nConfigurações criadas:')
            categoria_atual = None
            for config in configuracoes:
                if config.categoria != categoria_atual:
                    categoria_atual = config.categoria
                    self.stdout.write(f'\n[{categoria_atual.upper()}]')
                
                self.stdout.write(f'  {config.chave}: {config.valor} - {config.descricao}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao inicializar configurações: {e}')
            )

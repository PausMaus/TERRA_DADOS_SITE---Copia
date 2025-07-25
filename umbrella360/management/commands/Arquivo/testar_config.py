# -*- coding: utf-8 -*-
"""
Command para testar as configurações dinâmicas.
"""

from django.core.management.base import BaseCommand
from umbrella360.config import Config


class Command(BaseCommand):
    help = 'Testa as configurações dinâmicas do sistema Umbrella360'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Testando configurações dinâmicas...'))
        
        # Testar configurações básicas
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('CONFIGURAÇÕES BÁSICAS'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'Custo diesel: R$ {Config.custo_diesel():.2f}/L')
        self.stdout.write(f'Média objetivo: {Config.media_km_objetivo():.2f} km/L')
        self.stdout.write(f'Consumo máx normal: {Config.consumo_maximo_normal():,.0f} L')
        self.stdout.write(f'Limite erro: {Config.consumo_limite_erro():,.0f} L')
        self.stdout.write(f'Fator emissão CO2: {Config.fator_emissao_co2():.2f} kg/L')
        
        # Testar configuração dinâmica
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('CONFIGURAÇÃO DINÂMICA'))
        self.stdout.write('='*50)
        
        try:
            media_atual = Config.media_km_atual()
            self.stdout.write(f'Média atual (dinâmica): {media_atual:.2f} km/L')
            
            # Comparar com objetivo
            objetivo = Config.media_km_objetivo()
            diferenca = media_atual - objetivo
            percentual = (diferenca / objetivo) * 100
            
            if diferenca > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Acima do objetivo em {diferenca:.2f} km/L ({percentual:+.1f}%)'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Abaixo do objetivo em {abs(diferenca):.2f} km/L ({percentual:+.1f}%)'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao calcular média atual: {e}'))
        
        # Teste de cache
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TESTE DE PERFORMANCE (CACHE)'))
        self.stdout.write('='*50)
        
        import time
        
        # Primeira chamada (sem cache)
        start = time.time()
        custo1 = Config.custo_diesel()
        time1 = time.time() - start
        
        # Segunda chamada (com cache)
        start = time.time()
        custo2 = Config.custo_diesel()
        time2 = time.time() - start
        
        self.stdout.write(f'1ª chamada: {time1*1000:.2f}ms')
        self.stdout.write(f'2ª chamada: {time2*1000:.2f}ms')
        
        if time2 < time1:
            speedup = time1 / time2
            self.stdout.write(self.style.SUCCESS(f'✓ Cache ativo! Speedup: {speedup:.1f}x'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Cache pode não estar funcionando'))
            
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Teste concluído!')

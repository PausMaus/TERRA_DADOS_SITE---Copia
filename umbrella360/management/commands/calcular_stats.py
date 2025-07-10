# -*- coding: utf-8 -*-
"""
Command para calcular e exibir estatísticas dinâmicas do sistema.
"""

from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum, Count
from umbrella360.models import Viagem_CAM, Viagem_MOT
from umbrella360.config import Config


class Command(BaseCommand):
    help = 'Calcula e exibe estatísticas dinâmicas do sistema Umbrella360'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes',
            type=str,
            help='Filtrar por mês específico (ex: janeiro, fevereiro, etc.)',
        )
        parser.add_argument(
            '--update-config',
            action='store_true',
            help='Atualizar configurações com valores calculados',
        )

    def handle(self, *args, **options):
        mes_filtro = options.get('mes')
        update_config = options.get('update_config', False)
        
        self.stdout.write(self.style.WARNING('Calculando estatísticas dinâmicas...'))
        
        # Filtros base
        viagens_cam = Viagem_CAM.objects.all()
        viagens_mot = Viagem_MOT.objects.all()
        
        if mes_filtro:
            viagens_cam = viagens_cam.filter(mês__iexact=mes_filtro)
            viagens_mot = viagens_mot.filter(mês__iexact=mes_filtro)
            self.stdout.write(f'Filtrando por mês: {mes_filtro}')
        
        # Filtrar dados válidos (excluir outliers)
        consumo_max = Config.consumo_maximo_normal()
        viagens_cam_validas = viagens_cam.filter(Consumido__gt=0, Consumido__lte=consumo_max)
        viagens_mot_validas = viagens_mot.filter(Consumido__gt=0, Consumido__lte=consumo_max)
        
        # Estatísticas de Caminhões
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ESTATÍSTICAS DE CAMINHÕES'))
        self.stdout.write('='*50)
        
        stats_cam = viagens_cam_validas.aggregate(
            media_km_l=Avg('Quilometragem_média'),
            media_velocidade=Avg('Velocidade_média'),
            media_rpm=Avg('RPM_médio'),
            total_km=Sum('quilometragem'),
            total_consumo=Sum('Consumido'),
            total_emissoes=Sum('Emissões_CO2'),
            count=Count('id')
        )
        
        self.stdout.write(f'Registros válidos: {stats_cam["count"]}')
        self.stdout.write(f'Média Km/L atual: {stats_cam["media_km_l"]:.2f}' if stats_cam["media_km_l"] else 'N/A')
        self.stdout.write(f'Velocidade média: {stats_cam["media_velocidade"]:.2f} km/h' if stats_cam["media_velocidade"] else 'N/A')
        self.stdout.write(f'RPM médio: {stats_cam["media_rpm"]:.2f}' if stats_cam["media_rpm"] else 'N/A')
        self.stdout.write(f'Total quilometragem: {stats_cam["total_km"]:,.2f} km' if stats_cam["total_km"] else 'N/A')
        self.stdout.write(f'Total consumo: {stats_cam["total_consumo"]:,.2f} L' if stats_cam["total_consumo"] else 'N/A')
        self.stdout.write(f'Total emissões CO2: {stats_cam["total_emissoes"]:,.2f} kg' if stats_cam["total_emissoes"] else 'N/A')
        
        # Eficiência real calculada
        if stats_cam["total_km"] and stats_cam["total_consumo"]:
            eficiencia_real = stats_cam["total_km"] / stats_cam["total_consumo"]
            self.stdout.write(f'Eficiência real total: {eficiencia_real:.2f} km/L')
        
        # Estatísticas de Motoristas
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ESTATÍSTICAS DE MOTORISTAS'))
        self.stdout.write('='*50)
        
        stats_mot = viagens_mot_validas.aggregate(
            media_km_l=Avg('Quilometragem_média'),
            media_velocidade=Avg('Velocidade_média'),
            total_km=Sum('quilometragem'),
            total_consumo=Sum('Consumido'),
            count=Count('id')
        )
        
        self.stdout.write(f'Registros válidos: {stats_mot["count"]}')
        self.stdout.write(f'Média Km/L atual: {stats_mot["media_km_l"]:.2f}' if stats_mot["media_km_l"] else 'N/A')
        self.stdout.write(f'Velocidade média: {stats_mot["media_velocidade"]:.2f} km/h' if stats_mot["media_velocidade"] else 'N/A')
        self.stdout.write(f'Total quilometragem: {stats_mot["total_km"]:,.2f} km' if stats_mot["total_km"] else 'N/A')
        self.stdout.write(f'Total consumo: {stats_mot["total_consumo"]:,.2f} L' if stats_mot["total_consumo"] else 'N/A')
        
        # Comparação com objetivos
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('COMPARAÇÃO COM OBJETIVOS'))
        self.stdout.write('='*50)
        
        objetivo_km_l = float(Config.media_km_objetivo())
        self.stdout.write(f'Objetivo da empresa: {objetivo_km_l} km/L')
        
        if stats_cam["media_km_l"]:
            media_atual = float(stats_cam["media_km_l"])
            diferenca = media_atual - objetivo_km_l
            percentual = (diferenca / objetivo_km_l) * 100
            
            if diferenca > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Superando objetivo em {diferenca:.2f} km/L ({percentual:+.1f}%)'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Abaixo do objetivo em {abs(diferenca):.2f} km/L ({percentual:+.1f}%)'))
        
        # Análise por marca
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ANÁLISE POR MARCA'))
        self.stdout.write('='*50)
        
        for marca in ['Scania', 'Volvo']:
            viagens_marca = viagens_cam_validas.filter(agrupamento__marca=marca)
            stats_marca = viagens_marca.aggregate(
                media_km_l=Avg('Quilometragem_média'),
                count=Count('id'),
                total_consumo=Sum('Consumido')
            )
            
            self.stdout.write(f'\n{marca}:')
            self.stdout.write(f'  Registros: {stats_marca["count"]}')
            if stats_marca["media_km_l"]:
                self.stdout.write(f'  Média Km/L: {float(stats_marca["media_km_l"]):.2f}')
            else:
                self.stdout.write('  Média Km/L: N/A')
            if stats_marca["total_consumo"]:
                self.stdout.write(f'  Total consumo: {float(stats_marca["total_consumo"]):,.2f} L')
            else:
                self.stdout.write('  Total consumo: N/A')
        
        # Atualizar configurações se solicitado
        if update_config and stats_cam["media_km_l"]:
            from umbrella360.config import ConfiguracaoManager
            
            # Atualizar média atual com base nos dados calculados
            ConfiguracaoManager.set_valor(
                'media_km_atual_calculada',
                float(stats_cam["media_km_l"]),
                f'Média km/L calculada dinamicamente dos dados {"do mês " + mes_filtro if mes_filtro else ""}',
                'performance'
            )
            
            self.stdout.write('\n' + self.style.SUCCESS('Configuração atualizada com média calculada!'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Análise concluída!')

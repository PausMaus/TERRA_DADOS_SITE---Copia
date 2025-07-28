from django.core.management.base import BaseCommand
from umbrella360.models import Unidade, Caminhao, Empresa
from termcolor import colored


class Command(BaseCommand):
    help = 'Transfere unidades da empresa CPBrascell para o modelo Caminhão'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== INICIANDO TRANSFERÊNCIA DE CAMINHÕES ==='))
        
        # Busca a empresa CPBrascell
        try:
            empresa_cpbrascell = Empresa.objects.get(nome='CPBRASCELL')
            self.stdout.write(self.style.SUCCESS(f'Empresa encontrada: {empresa_cpbrascell.nome}'))
        except Empresa.DoesNotExist:
            self.stdout.write(self.style.ERROR('Empresa CPBRASCELL não encontrada no banco de dados.'))
            return

        # Busca unidades da empresa CPBrascell que são veículos/caminhões
        unidades_cpbrascell = Unidade.objects.filter(
            empresa=empresa_cpbrascell,
            cls__icontains='Veículo'  # Filtra por classe que contém "Veículo"
        )

        if not unidades_cpbrascell.exists():
            self.stdout.write(self.style.WARNING('Nenhuma unidade/veículo encontrada para a empresa CPBRASCELL.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Encontradas {unidades_cpbrascell.count()} unidades/veículos da CPBRASCELL'))
        
        # Contadores para estatísticas
        criados = 0
        atualizados = 0
        erros = 0

        # Processa cada unidade
        for unidade in unidades_cpbrascell:
            try:
                # Determina a marca baseada na descrição ou marca da unidade
                marca = self.determinar_marca(unidade)
                
                # Usa o campo 'nm' como agrupamento
                agrupamento = unidade.nm if unidade.nm else unidade.id
                
                # Verifica se já existe um caminhão com esse agrupamento
                caminhao, created = Caminhao.objects.update_or_create(
                    agrupamento=agrupamento,
                    defaults={
                        'marca': marca
                    }
                )
                
                if created:
                    criados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Caminhão CRIADO: {agrupamento} - {marca}')
                    )
                else:
                    atualizados += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Caminhão ATUALIZADO: {agrupamento} - {marca}')
                    )
                    
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao processar unidade {unidade.nm or unidade.id}: {str(e)}')
                )

        # Relatório final
        self.stdout.write(self.style.SUCCESS('\n=== RELATÓRIO FINAL ==='))
        self.stdout.write(self.style.SUCCESS(f'Caminhões criados: {colored(criados, "green")}'))
        self.stdout.write(self.style.WARNING(f'Caminhões atualizados: {colored(atualizados, "yellow")}'))
        if erros > 0:
            self.stdout.write(self.style.ERROR(f'Erros encontrados: {colored(erros, "red")}'))
        
        total_processados = criados + atualizados
        self.stdout.write(self.style.SUCCESS(f'Total processado: {colored(total_processados, "cyan")}'))
        self.stdout.write(self.style.SUCCESS('=== TRANSFERÊNCIA CONCLUÍDA ==='))

    def determinar_marca(self, unidade):
        """
        Determina a marca do caminhão baseado nos dados da unidade
        """
        # Primeiro verifica se já tem marca definida
        if unidade.marca and unidade.marca.strip():
            return unidade.marca.strip()
        
        # Verifica na descrição se menciona alguma marca
        descricao = unidade.descricao or ''
        marca_unidade = unidade.marca or ''
        nome_unidade = unidade.nm or ''
        
        # Combina todos os campos para análise
        texto_completo = f"{descricao} {marca_unidade} {nome_unidade}".lower()
        
        # Lista de marcas conhecidas para detectar
        marcas_conhecidas = {
            'scania': 'Scania',
            'volvo': 'Volvo',
            'mercedes': 'Mercedes-Benz',
            'iveco': 'Iveco',
            'ford': 'Ford',
            'volkswagen': 'Volkswagen',
            'man': 'MAN',
            'daf': 'DAF'
        }
        
        # Procura por marcas conhecidas no texto
        for marca_key, marca_nome in marcas_conhecidas.items():
            if marca_key in texto_completo:
                return marca_nome
        
        # Marca padrão se não encontrar nenhuma
        return 'Volvo'  # Padrão baseado no código original

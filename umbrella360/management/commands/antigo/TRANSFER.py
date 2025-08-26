from django.core.management.base import BaseCommand
from umbrella360.models import Unidade, Caminhao, Empresa, Viagem_Base, Viagem_CAM
from termcolor import colored


class Command(BaseCommand):
    help = 'Transfere unidades da empresa CPBrascell para o modelo Caminhão e suas viagens'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== INICIANDO TRANSFERÊNCIA DE CAMINHÕES E VIAGENS ==='))
        
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
        self.stdout.write(self.style.SUCCESS('\n=== RELATÓRIO FINAL - CAMINHÕES ==='))
        self.stdout.write(self.style.SUCCESS(f'Caminhões criados: {colored(criados, "green")}'))
        self.stdout.write(self.style.WARNING(f'Caminhões atualizados: {colored(atualizados, "yellow")}'))
        if erros > 0:
            self.stdout.write(self.style.ERROR(f'Erros encontrados: {colored(erros, "red")}'))
        
        total_processados = criados + atualizados
        self.stdout.write(self.style.SUCCESS(f'Total processado: {colored(total_processados, "cyan")}'))
        
        # Agora transfere as viagens
        self.transferir_viagens()
        
        self.stdout.write(self.style.SUCCESS('=== TRANSFERÊNCIA CONCLUÍDA ==='))

    def transferir_viagens(self):
        """
        Transfere dados de Viagem_Base para Viagem_CAM
        """
        self.stdout.write(self.style.SUCCESS('\n=== INICIANDO TRANSFERÊNCIA DE VIAGENS ==='))
        
        # Busca todas as viagens base de unidades da CPBrascell
        viagens_base = Viagem_Base.objects.filter(
            unidade__empresa__nome='CPBRASCELL',
            unidade__cls__icontains='Veículo'
        ).select_related('unidade')
        
        if not viagens_base.exists():
            self.stdout.write(self.style.WARNING('Nenhuma viagem encontrada para transferir.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Encontradas {viagens_base.count()} viagens para transferir'))
        
        # Contadores para estatísticas
        viagens_criadas = 0
        viagens_atualizadas = 0
        viagens_erros = 0
        
        for viagem_base in viagens_base:
            try:
                # Busca o caminhão correspondente usando o nome da unidade
                nome_unidade = viagem_base.unidade.nm
                
                try:
                    caminhao = Caminhao.objects.get(agrupamento=nome_unidade)
                except Caminhao.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Caminhão não encontrado para a unidade: {nome_unidade}')
                    )
                    viagens_erros += 1
                    continue
                
                # Cria ou atualiza a viagem do caminhão
                viagem_cam, created = Viagem_CAM.objects.update_or_create(
                    agrupamento=caminhao,
                    mês=viagem_base.período or 'N/A',
                    defaults={
                        'quilometragem': viagem_base.quilometragem or 0.00,
                        'Consumido': viagem_base.Consumido or 0,
                        'Quilometragem_média': viagem_base.Quilometragem_média or 0.00,
                        'Horas_de_motor': viagem_base.Horas_de_motor or '0.00',
                        'Velocidade_média': viagem_base.Velocidade_média or 0.00,
                        'RPM_médio': viagem_base.RPM_médio or 0.00,
                        'Temperatura_média': viagem_base.Temperatura_média or 0.00,
                        'Emissões_CO2': viagem_base.Emissões_CO2 or 0.00,
                    }
                )
                
                if created:
                    viagens_criadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Viagem CRIADA: {caminhao.agrupamento} - {viagem_base.período}')
                    )
                else:
                    viagens_atualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Viagem ATUALIZADA: {caminhao.agrupamento} - {viagem_base.período}')
                    )
                    
            except Exception as e:
                viagens_erros += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao processar viagem de {viagem_base.unidade.nm}: {str(e)}')
                )
        
        # Relatório final das viagens
        self.stdout.write(self.style.SUCCESS('\n=== RELATÓRIO FINAL - VIAGENS ==='))
        self.stdout.write(self.style.SUCCESS(f'Viagens criadas: {colored(viagens_criadas, "green")}'))
        self.stdout.write(self.style.WARNING(f'Viagens atualizadas: {colored(viagens_atualizadas, "yellow")}'))
        if viagens_erros > 0:
            self.stdout.write(self.style.ERROR(f'Erros encontrados: {colored(viagens_erros, "red")}'))
        
        total_viagens_processadas = viagens_criadas + viagens_atualizadas
        self.stdout.write(self.style.SUCCESS(f'Total de viagens processadas: {colored(total_viagens_processadas, "cyan")}'))

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

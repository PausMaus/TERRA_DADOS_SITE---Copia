from django.db import models

#UMBRELLA 360: Logística Inteligente
# esse é um aplicativo voltado para o gerenciamento de motoristas e caminhões e seus consumos de combustível
# Create your models here.



class ConfiguracaoSistema(models.Model):
    """
    Model para armazenar configurações do sistema que podem ser alteradas
    pelo administrador através do Django Admin.
    """
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave de Configuração")
    valor = models.FloatField(verbose_name="Valor")
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.CharField(max_length=50, default="geral", verbose_name="Categoria")
    data_modificacao = models.DateTimeField(auto_now=True, verbose_name="Data de Modificação")

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
        ordering = ['categoria', 'chave']

    def __str__(self):
        return f"{self.chave}: {self.valor}"


class Motorista(models.Model):
    agrupamento = models.CharField(max_length=100)
    
    def __str__(self):
        return self.agrupamento
    
    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ['agrupamento']


class Viagem_MOT(models.Model):
    agrupamento = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name='viagens')
    quilometragem = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Quilometragem Atual (km)", blank=True, null=True
    )
    Consumido = models.PositiveIntegerField(
        default=0.00, verbose_name="Combustível Total (litros)", blank=True, null=True
    )
    Quilometragem_média = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Média de Consumo (km/l)", blank=True, null=True
    )
    Horas_de_motor = models.CharField(
    default=0.00, verbose_name="Horas de Motor", blank=True, null=True, max_length=100
    )
    Velocidade_média = models.FloatField(
    default=0.00, verbose_name="Velocidade Média (km/h)", blank=True, null=True
    )
    Emissões_CO2 = models.FloatField(
    default=0.00, verbose_name="Emissões de CO2 (g/km)", blank=True, null=True
    )
    mês = models.CharField(
        max_length=20, default="Maio", verbose_name="Mês de Referência", blank=True, null=True
    )

    def __str__(self):
        return f"{self.agrupamento.agrupamento} ({self.mês})"

    class Meta:
        verbose_name = "Viagem Motorista"
        verbose_name_plural = "Viagens Motoristas"



class Caminhao(models.Model):
    agrupamento = models.CharField(max_length=10, unique=True, verbose_name="Agrupamento do Caminhão")
    marca = models.CharField(max_length=50, verbose_name="Marca do Caminhão")

    def __str__(self):
        return f"{self.agrupamento} - {self.marca}"
    
    class Meta:
        verbose_name = "Caminhão"
        verbose_name_plural = "Caminhões"
        ordering = ['agrupamento']



class Viagem_CAM(models.Model):
    agrupamento = models.ForeignKey(Caminhao, on_delete=models.CASCADE, related_name='viagens')
    quilometragem = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Quilometragem Atual (km)", blank=True, null=True
    )
    Consumido = models.PositiveIntegerField(
        default=0.00, verbose_name="Combustível Total (litros)", blank=True, null=True
    )
    Quilometragem_média = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Média de Consumo (km/l)", blank=True, null=True
    )
    Horas_de_motor = models.CharField(
        default=0.00, verbose_name="Horas de Motor", blank=True, null=True, max_length=100
    )
    Velocidade_média = models.FloatField(
     default=0.00, verbose_name="Velocidade Média (km/h)", blank=True, null=True
    )
    RPM_médio = models.FloatField(
     default=0.00, verbose_name="RPM Médio do Motor", blank=True, null=True
    )
    Temperatura_média = models.FloatField(
     default=0.00, verbose_name="Temperatura Média (°C)", blank=True, null=True
    )
    Emissões_CO2 = models.FloatField(
     default=0.00, verbose_name="Emissões de CO2 (g/km)", blank=True, null=True
    )
    mês = models.CharField(
        max_length=20, default="Maio", verbose_name="Mês de Referência", blank=True, null=True
    )


    def __str__(self):
        return f"{self.agrupamento.agrupamento} - {self.agrupamento.marca} ({self.mês})"

    class Meta:
        verbose_name = "Viagem Caminhões"
        verbose_name_plural = "Viagens Caminhões"


##############################################################################
#novos modelos para o sistema UMBRELLA 360
##############################################################################


#empresa
class Empresa(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Empresa")
    token = models.CharField(max_length=100, unique=True, verbose_name="Token de Acesso Wialon", blank=True, null=True)
    senha = models.CharField(max_length=100, default='senha', verbose_name="Senha de Acesso", blank=True, null=True)
    id_recurso = models.CharField(max_length=50, unique=True, verbose_name="ID do Recurso Wialon", blank=True, null=True)
    #exemplo de ID de frota:401914599
    frota = models.CharField(max_length=50, verbose_name="ID da Frota Wialon", blank=True, null=True)
    id_criador = models.CharField(max_length=50, verbose_name="ID do Criador no Wialon", blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nome']



#unidades basicas
class Unidade(models.Model):
    nm = models.CharField(max_length=100, verbose_name="Nome da Unidade", blank=True, null=True)
    cls = models.CharField(max_length=50, verbose_name="Classe da Unidade", blank=True, null=True)
    id = models.CharField(max_length=50, primary_key=True, verbose_name="ID da Unidade")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa Associada")
    descricao = models.TextField(verbose_name="Descrição da Unidade", blank=True, null=True)
    marca = models.CharField(max_length=50, verbose_name="Marca da Unidade", blank=True, null=True)
    placa = models.CharField(max_length=20, verbose_name="Placa da Unidade", blank=True, null=True)
    id_wialon = models.CharField(max_length=50, unique=True, verbose_name="ID Wialon", blank=True, null=True)
    odometro = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Odômetro (km)", blank=True, null=True)
    id_criador = models.CharField(max_length=50, verbose_name="ID do Criador no Wialon", blank=True, null=True)
    def __str__(self):
        return f"{self.id} - {self.nm} ({self.cls})"
    
    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ['id']

#veículo, child de Unidade
class Veiculo(Unidade):
    ano = models.PositiveIntegerField(verbose_name="Ano do Veículo", blank=True, null=True)
    modelo = models.CharField(max_length=100, verbose_name="Modelo do Veículo", blank=True, null=True)
    cor = models.CharField(max_length=50, verbose_name="Cor do Veículo", blank=True, null=True)
    tipo_combustivel = models.CharField(max_length=50, verbose_name="Tipo de Combustível", blank=True, null=True)

    def __str__(self):
        return f"{self.modelo} ({self.ano}) - {self.cor} - {self.tipo_combustivel}"

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['modelo']

#driver, child de Unidade
class Driver(Unidade):
    codigo = models.IntegerField(verbose_name="Código", blank=True, null=True)
    avl_driver = models.PositiveIntegerField(verbose_name="avl_driver", blank=True, null=True)




class Viagem_Base(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='viagens')
    quilometragem = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Quilometragem", blank=True, null=True
    )
    Consumido = models.PositiveIntegerField(
        default=0.00, verbose_name="Combustível Total (litros)", blank=True, null=True
    )
    Quilometragem_média = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Média de Consumo (km/l)", blank=True, null=True
    )
    Horas_de_motor = models.CharField(
        default=0.00, verbose_name="Horas de Motor", blank=True, null=True, max_length=100
    )
    Velocidade_média = models.FloatField(
     default=0.00, verbose_name="Velocidade Média (km/h)", blank=True, null=True
    )
    RPM_médio = models.FloatField(
     default=0.00, verbose_name="RPM Médio do Motor", blank=True, null=True
    )
    Temperatura_média = models.FloatField(
     default=0.00, verbose_name="Temperatura Média (°C)", blank=True, null=True
    )
    Emissões_CO2 = models.FloatField(
     default=0.00, verbose_name="Emissões de CO2 (g/km)", blank=True, null=True
    )
    período = models.CharField(
        max_length=20, verbose_name="Período de Referência", blank=True, null=True
    )
    motor_ocioso = models.DurationField(
         verbose_name="Horas de Motor Ocioso", blank=True, null=True
    )
    class Meta:
        verbose_name = "Viagem Base"
        verbose_name_plural = "Viagens"
        ordering = ['-período']

#Viagem detalhada, herda de Viagem_Base
class Viagem_Detalhada(Viagem_Base):
    timestamp_inicial = models.PositiveIntegerField(verbose_name="Timestamp Inicial", blank=True, null=True)
    timestamp_final = models.PositiveIntegerField(verbose_name="Timestamp Final", blank=True, null=True)
    # relaciona com um Veículo
    veiculo = models.CharField(max_length=50, blank=True, null=True)


    #herda todos os campos de Viagem_Base
    class Meta:
        verbose_name = "Viagem Detalhada"
        verbose_name_plural = "Viagens Detalhadas"
        ordering = ['-período']

        


class Viagem_eco(models.Model):
    #várias viagens ecológicas por unidade

    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='viagens_eco')
    #timestamp em numérico
    timestamp = models.PositiveIntegerField(verbose_name="Timestamp", blank=True, null=True)
    rpm = models.PositiveIntegerField(verbose_name="RPM do Motor", blank=True, null=True)
    velocidade = models.FloatField(verbose_name="Velocidade (km/h)", blank=True, null=True)
    altitude = models.FloatField(verbose_name="Altitude (m)", blank=True, null=True)
    energia = models.PositiveIntegerField(verbose_name="Energia (V)", blank=True, null=True)
    avl_driver = models.IntegerField(verbose_name="Avl_Driver", blank=True, null=True )
    driver_code = models.IntegerField(verbose_name="Motorista", null=True, blank=True)
    nome_motorista = models.ForeignKey(Driver, on_delete=models.CASCADE, default=None, blank=True, null=True, related_name='viagens_motorista')
    faixa_azul = models.BooleanField(verbose_name="Faixa Azul", blank=True, null=True)
    faixa_verde = models.BooleanField(verbose_name="Faixa Verde", blank=True, null=True)
    faixa_amarela = models.BooleanField(verbose_name="Faixa Amarela", blank=True, null=True)
    faixa_vermelha = models.BooleanField(verbose_name="Faixa Vermelha", blank=True, null=True)
    ocioso = models.BooleanField(verbose_name="Ocioso", blank=True, null=True)
    
    def __str__(self):
        return f"{self.unidade.nm} - {self.timestamp}"

    class Meta:
        verbose_name = "Viagem Ecológica"
        verbose_name_plural = "Viagens Ecológicas"


class CheckPoint(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='checkpoints')
    cerca = models.CharField(max_length=100, verbose_name="Cerca Eletrônica", blank=True, null=True)
    data_entrada = models.DateTimeField(verbose_name="Data de Entrada", blank=True, null=True)
    data_saida = models.DateTimeField(verbose_name="Data de Saída", blank=True, null=True)
    duracao = models.DurationField(verbose_name="Duração", blank=True, null=True)
    período = models.CharField(
        max_length=20, verbose_name="Período de Referência", blank=True, null=True
    )

    def __str__(self):
        return f"{self.unidade.nm} - {self.cerca} ({self.período})"

    class Meta:
        verbose_name = "CheckPoint"
        verbose_name_plural = "CheckPoints"
        ordering = ['-data_entrada']



class Infrações(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='infracoes')
    data = models.DateTimeField(verbose_name="Data da Infração", blank=True, null=True)
    limite = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Limite de Velocidade (km/h)", blank=True, null=True)
    velocidade = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Velocidade (km/h)", blank=True, null=True)
    localizacao = models.URLField(max_length=100, verbose_name="Localização", blank=True, null=True)

    def __str__(self):
        return f"{self.unidade.nm} - {self.limite} ({self.data})"

    class Meta:
        verbose_name = "Infração"
        verbose_name_plural = "Infrações"
        ordering = ['-data']


class Estatistica_Diaria_Motorista(models.Model):
    """
    Modelo para armazenar estatísticas diárias pré-processadas dos motoristas.
    Calculado durante a coleta de dados das mensagens (MENSAGENS command).
    """
    # Chaves
    motorista = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='estatisticas_diarias')
    data = models.DateField(verbose_name="Data", db_index=True)
    
    # Estatísticas de RPM (baseadas nas faixas)
    total_pontos = models.IntegerField(default=0, verbose_name="Total de Pontos")
    pontos_ocioso = models.IntegerField(default=0, verbose_name="Pontos em Ocioso")
    pontos_faixa_azul = models.IntegerField(default=0, verbose_name="Pontos Faixa Azul")
    pontos_faixa_verde = models.IntegerField(default=0, verbose_name="Pontos Faixa Verde")
    pontos_faixa_amarela = models.IntegerField(default=0, verbose_name="Pontos Faixa Amarela")
    pontos_faixa_vermelha = models.IntegerField(default=0, verbose_name="Pontos Faixa Vermelha")
    
    # Percentuais (calculados)
    perc_ocioso = models.FloatField(default=0.0, verbose_name="% Ocioso")
    perc_faixa_azul = models.FloatField(default=0.0, verbose_name="% Faixa Azul")
    perc_faixa_verde = models.FloatField(default=0.0, verbose_name="% Faixa Verde")
    perc_faixa_amarela = models.FloatField(default=0.0, verbose_name="% Faixa Amarela")
    perc_faixa_vermelha = models.FloatField(default=0.0, verbose_name="% Faixa Vermelha")
    
    # Score de performance
    score_performance = models.FloatField(default=0.0, verbose_name="Score de Performance")
    
    # Médias de sensores
    rpm_medio = models.FloatField(default=0.0, verbose_name="RPM Médio")
    velocidade_media = models.FloatField(default=0.0, verbose_name="Velocidade Média")
    
    # Jornada de trabalho
    timestamp_inicio = models.IntegerField(verbose_name="Timestamp Início do Dia", blank=True, null=True)
    timestamp_fim = models.IntegerField(verbose_name="Timestamp Fim do Dia", blank=True, null=True)
    horas_trabalhadas = models.FloatField(default=0.0, verbose_name="Horas Trabalhadas")
    
    # Veículos utilizados
    total_veiculos = models.IntegerField(default=0, verbose_name="Total de Veículos Diferentes")
    veiculos_ids = models.TextField(blank=True, null=True, verbose_name="IDs dos Veículos (JSON)")
    
    # Metadados
    data_processamento = models.DateTimeField(auto_now=True, verbose_name="Data de Processamento")
    
    class Meta:
        verbose_name = "Estatística Diária do Motorista"
        verbose_name_plural = "Estatísticas Diárias dos Motoristas"
        ordering = ['-data', 'motorista']
        unique_together = ['motorista', 'data']  # Um registro por motorista por dia
        indexes = [
            models.Index(fields=['motorista', 'data']),
            models.Index(fields=['data']),
            models.Index(fields=['score_performance']),
        ]
    
    def __str__(self):
        return f"{self.motorista.nm} - {self.data.strftime('%d/%m/%Y')} - Score: {self.score_performance:.2f}"
    
    def calcular_percentuais(self):
        """Calcula os percentuais baseados nos pontos"""
        if self.total_pontos > 0:
            self.perc_ocioso = (self.pontos_ocioso / self.total_pontos) * 100
            self.perc_faixa_azul = (self.pontos_faixa_azul / self.total_pontos) * 100
            self.perc_faixa_verde = (self.pontos_faixa_verde / self.total_pontos) * 100
            self.perc_faixa_amarela = (self.pontos_faixa_amarela / self.total_pontos) * 100
            self.perc_faixa_vermelha = (self.pontos_faixa_vermelha / self.total_pontos) * 100
        else:
            self.perc_ocioso = 0.0
            self.perc_faixa_azul = 0.0
            self.perc_faixa_verde = 0.0
            self.perc_faixa_amarela = 0.0
            self.perc_faixa_vermelha = 0.0
    
    def calcular_score(self):
        """Calcula o score de performance"""
        self.score_performance = (
            (self.perc_faixa_verde * 1.0) + 
            (self.perc_faixa_azul * 0.8) - 
            (self.perc_faixa_amarela * 0.5) - 
            (self.perc_faixa_vermelha * 1.0) - 
            (self.perc_ocioso * 0.3)
        )
    
    def calcular_horas_trabalhadas(self):
        """Calcula horas trabalhadas baseado nos timestamps"""
        if self.timestamp_inicio and self.timestamp_fim:
            diferenca_segundos = self.timestamp_fim - self.timestamp_inicio
            self.horas_trabalhadas = diferenca_segundos / 3600
        else:
            self.horas_trabalhadas = 0.0
    
    def save(self, *args, **kwargs):
        """Override save para calcular métricas automaticamente"""
        self.calcular_percentuais()
        self.calcular_score()
        self.calcular_horas_trabalhadas()
        super().save(*args, **kwargs)


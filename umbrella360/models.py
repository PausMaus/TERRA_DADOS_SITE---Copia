from django.db import models

#UMBRELLA 360: Logística Inteligente
# esse é um aplicativo voltado para o gerenciamento de motoristas e caminhões e seus consumos de combustível
# Create your models here.



class Motorista(models.Model):
    agrupamento = models.CharField(max_length=100)
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

    def __str__(self):
        return self.agrupamento

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"



class Caminhao(models.Model):
    agrupamento = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50, default="Volvo")
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

    def __str__(self):
        return f"{self.agrupamento} - {self.marca}"

    class Meta:
        verbose_name = "Caminhão"
        verbose_name_plural = "Caminhões"






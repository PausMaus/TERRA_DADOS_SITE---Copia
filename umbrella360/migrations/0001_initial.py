# Generated by Django 5.2.3 on 2025-07-08 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Motorista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agrupamento', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Caminhao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agrupamento', models.CharField(max_length=10, unique=True, verbose_name='Agrupamento do Caminhão')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='umbrella360.marca')),
            ],
        ),
        migrations.CreateModel(
            name='Viagem_CAM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quilometragem', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Quilometragem Atual (km)')),
                ('Consumido', models.PositiveIntegerField(blank=True, default=0.0, null=True, verbose_name='Combustível Total (litros)')),
                ('Quilometragem_média', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True, verbose_name='Média de Consumo (km/l)')),
                ('Horas_de_motor', models.CharField(blank=True, default=0.0, max_length=100, null=True, verbose_name='Horas de Motor')),
                ('Velocidade_média', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Velocidade Média (km/h)')),
                ('RPM_médio', models.FloatField(blank=True, default=0.0, null=True, verbose_name='RPM Médio do Motor')),
                ('Temperatura_média', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Temperatura Média (°C)')),
                ('Emissões_CO2', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Emissões de CO2 (g/km)')),
                ('mês', models.CharField(blank=True, default='Maio', max_length=20, null=True, verbose_name='Mês de Referência')),
                ('agrupamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viagens', to='umbrella360.caminhao')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='umbrella360.marca')),
            ],
            options={
                'verbose_name': 'Caminhão',
                'verbose_name_plural': 'Caminhões',
            },
        ),
        migrations.CreateModel(
            name='Viagem_MOT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quilometragem', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Quilometragem Atual (km)')),
                ('Consumido', models.PositiveIntegerField(blank=True, default=0.0, null=True, verbose_name='Combustível Total (litros)')),
                ('Quilometragem_média', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True, verbose_name='Média de Consumo (km/l)')),
                ('Horas_de_motor', models.CharField(blank=True, default=0.0, max_length=100, null=True, verbose_name='Horas de Motor')),
                ('Velocidade_média', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Velocidade Média (km/h)')),
                ('Emissões_CO2', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Emissões de CO2 (g/km)')),
                ('Mês', models.CharField(blank=True, default='Maio', max_length=20, null=True, verbose_name='Mês de Referência')),
                ('agrupamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viagens', to='umbrella360.motorista')),
            ],
            options={
                'verbose_name': 'Motorista',
                'verbose_name_plural': 'Motoristas',
            },
        ),
    ]

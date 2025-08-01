# Generated by Django 5.2.3 on 2025-07-29 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academia_virtual', '0006_remove_treino_exercicios_delete_exercicio_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do Exercício')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição do Exercício')),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='academia_virtual/exercicios/', verbose_name='Imagem do Exercício')),
                ('duracao', models.IntegerField(blank=True, null=True, verbose_name='Duração do Exercício (em minutos)')),
                ('repeticoes', models.IntegerField(blank=True, null=True, verbose_name='Número de Repetições')),
                ('series', models.IntegerField(blank=True, null=True, verbose_name='Número de Séries')),
                ('dificuldade', models.CharField(blank=True, max_length=50, null=True, verbose_name='Dificuldade do Exercício')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academia_virtual.area', verbose_name='Área Associada')),
                ('equipamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academia_virtual.equipamento', verbose_name='Equipamento Associado')),
                ('professor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academia_virtual.professor', verbose_name='Professor Associado')),
            ],
            options={
                'verbose_name': 'Exercício',
                'verbose_name_plural': 'Exercícios',
            },
        ),
        migrations.CreateModel(
            name='Treino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do Treino')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição do Treino')),
                ('dificuldade', models.CharField(blank=True, max_length=50, null=True, verbose_name='Dificuldade do Treino')),
                ('exercicios', models.ManyToManyField(blank=True, to='academia_virtual.exercicio', verbose_name='Exercícios do Treino')),
            ],
            options={
                'verbose_name': 'Treino',
                'verbose_name_plural': 'Treinos',
            },
        ),
    ]

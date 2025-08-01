# Generated by Django 5.2.3 on 2025-07-29 15:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academia_virtual', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipamento',
            fields=[
                ('itemacademia_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='academia_virtual.itemacademia')),
                ('tipo', models.CharField(blank=True, max_length=50, null=True, verbose_name='Tipo de Equipamento')),
            ],
            options={
                'verbose_name': 'Equipamento de Academia',
                'verbose_name_plural': 'Equipamentos de Academia',
            },
            bases=('academia_virtual.itemacademia',),
        ),
    ]

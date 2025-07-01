# Generated manually on 2025-07-01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('umbrella360', '0013_calculo_scania_calculo_volvo_delete_calculo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Calculo_Scania',
        ),
        migrations.DeleteModel(
            name='Calculo_Volvo',
        ),
    ]

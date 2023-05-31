# Generated by Django 4.2.1 on 2023-05-26 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_sakon', '0005_alter_configuration_name_alter_schedule_weekday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='interval',
            field=models.CharField(choices=[('DAILY', 'DAILY'), ('WEEKLY', 'WEEKLY'), ('MONTHLY', 'MONTHLY')], max_length=10),
        ),
    ]
# Generated by Django 3.2.15 on 2022-08-25 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rack', '0004_auto_20220804_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='connection',
            field=models.TextField(blank=True, null=True, verbose_name='Подключён к'),
        ),
        migrations.AlterField(
            model_name='server',
            name='base_material',
            field=models.CharField(choices=[('Медь', 'Медь'), ('Оптика', 'Оптика')], max_length=20, verbose_name='Тип порта по умолчанию'),
        ),
        migrations.AlterField(
            model_name='server',
            name='base_speed',
            field=models.CharField(choices=[('10Mbit', '10Mbit'), ('100Mbit', '100Mbit'), ('1Gbit', '1Gbit'), ('10Gbit', '10Gbit')], max_length=20, verbose_name='Скорость порта по умолчанию'),
        ),
        migrations.AlterField(
            model_name='server',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Название'),
        ),
    ]

# Generated by Django 3.2.14 on 2022-08-04 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rack', '0003_alter_rack_options_server_color_alter_rack_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='base_material',
            field=models.CharField(choices=[('Медь', 'Медь'), ('Оптика', 'Оптика')], default=1, max_length=20, verbose_name='Тип порта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='server',
            name='base_speed',
            field=models.CharField(choices=[('10Mbit', '10Mbit'), ('100Mbit', '100Mbit'), ('1Gbit', '1Gbit'), ('10Gbit', '10Gbit')], default=1, max_length=20, verbose_name='Скорость порта'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('color', models.CharField(max_length=20, verbose_name='Цвет')),
                ('speed', models.CharField(choices=[('10Mbit', '10Mbit'), ('100Mbit', '100Mbit'), ('1Gbit', '1Gbit'), ('10Gbit', '10Gbit')], max_length=20, verbose_name='Скорость порта')),
                ('material', models.CharField(choices=[('Медь', 'Медь'), ('Оптика', 'Оптика')], max_length=20, verbose_name='Тип порта')),
                ('connection', models.TextField(blank=True, null=True, verbose_name='Объект на том конце')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rack.server')),
            ],
            options={
                'verbose_name': 'Порт',
                'verbose_name_plural': 'Порты',
            },
        ),
    ]

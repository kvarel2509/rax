# Generated by Django 3.2.15 on 2022-11-11 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rack', '0011_alter_rack_space'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='Название')),
                ('color', models.CharField(max_length=30, verbose_name='Цвет')),
            ],
        ),
        migrations.AlterField(
            model_name='port',
            name='connection',
            field=models.TextField(blank=True, help_text='Для создания связи используйте формат #id#номер_порта или #id#номер_порта#скорость, например: #123#1 или #123#1#1000', null=True, verbose_name='Подключён к'),
        ),
    ]

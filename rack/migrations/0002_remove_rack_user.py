# Generated by Django 4.0.4 on 2022-04-27 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rack', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rack',
            name='user',
        ),
    ]

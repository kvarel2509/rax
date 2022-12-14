# Generated by Django 3.2.15 on 2022-09-02 08:20

from django.db import migrations, models


def forward_func(apps, schema_editor):
    Server = apps.get_model("rack", "Server")
    servers = Server.objects.all()

    for server in servers:
        ports = server.port_set.all().order_by('pk')

        for ind, port in enumerate(ports, start=1):
            port.number = ind

        ports.bulk_update(ports, ['number'])


class Migration(migrations.Migration):

    dependencies = [
        ('rack', '0008_auto_20220901_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='number',
            field=models.PositiveIntegerField(default=1, verbose_name='Порядковый номер порта'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='linkport',
            name='speed',
            field=models.CharField(blank=True, choices=[('10Mbit', '10Mbit'), ('100Mbit', '100Mbit'), ('1Gbit', '1Gbit'), ('10Gbit', '10Gbit')], max_length=20, null=True, verbose_name='Скорость связи'),
        ),
        migrations.RunPython(forward_func, migrations.RunPython.noop)
    ]

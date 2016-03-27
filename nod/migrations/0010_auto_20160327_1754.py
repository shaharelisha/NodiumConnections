# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0009_auto_20160327_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('uuid', models.CharField(blank=True, max_length=32, default='', editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('bay_type', models.CharField(max_length=1, choices=[('1', 'MOT Bay'), ('2', 'Repair Bay')])),
                ('total_spots', models.PositiveSmallIntegerField()),
                ('free_spots', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='job',
            name='bay',
            field=models.ForeignKey(to='nod.Bay', default=1),
            preserve_default=False,
        ),
    ]

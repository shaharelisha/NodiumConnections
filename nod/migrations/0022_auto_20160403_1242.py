# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0021_jobpart_sufficient_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='part',
            name='year',
        ),
        migrations.AddField(
            model_name='part',
            name='years',
            field=models.CharField(default=1, max_length=9),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='part',
            name='code',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='manufacturer',
            field=models.CharField(max_length=100),
        ),
    ]

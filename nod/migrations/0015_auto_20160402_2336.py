# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0014_auto_20160402_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountholder',
            name='suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='type',
            field=models.CharField(choices=[('1', 'Van/Light Vehicle'), ('2', 'Car')], max_length=1),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0024_auto_20160403_1329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='parts',
        ),
        migrations.AddField(
            model_name='invoice',
            name='part_order',
            field=models.OneToOneField(to='nod.CustomerPartsOrder', null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='parts_for_job',
            field=models.ManyToManyField(to='nod.JobPart'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='parts_sold',
            field=models.ManyToManyField(to='nod.SellPart'),
        ),
    ]

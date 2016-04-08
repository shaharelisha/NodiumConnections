# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0037_auto_20160407_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='sparepart',
            name='new_stock_level',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sparepart',
            name='delivery',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sparepart',
            name='initial_stock_level',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sparepart',
            name='used',
            field=models.IntegerField(default=0),
        ),
    ]

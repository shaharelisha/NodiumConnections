# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0041_auto_20160408_0543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountholder',
            name='month',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='accountholder',
            name='spent_this_month',
            field=models.DecimalField(max_digits=4, decimal_places=2, null=True),
        ),
    ]

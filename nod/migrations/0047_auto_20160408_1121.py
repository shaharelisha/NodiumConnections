# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0046_auto_20160408_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountholder',
            name='spent_this_month',
            field=models.FloatField(default=0),
        ),
    ]

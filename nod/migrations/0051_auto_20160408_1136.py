# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0050_auto_20160408_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timereport',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 8, 11, 36, 52, 557511)),
        ),
    ]

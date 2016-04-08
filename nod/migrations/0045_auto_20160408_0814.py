# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0044_auto_20160408_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timereport',
            name='date',
            field=models.DateField(default=datetime.date(2016, 4, 8)),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0038_auto_20160407_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='timereport',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2016, 4, 8, 1, 20, 26, 993452, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timereport',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2016, 4, 8, 1, 20, 30, 625369, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

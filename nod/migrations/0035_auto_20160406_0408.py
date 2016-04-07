# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0034_auto_20160406_0306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sparepartsreport',
            name='reporting_period',
        ),
        migrations.AddField(
            model_name='sparepartsreport',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2016, 4, 6, 4, 8, 49, 821937, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sparepartsreport',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2016, 4, 6, 4, 8, 53, 909393, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

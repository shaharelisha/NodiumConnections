# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0012_auto_20160327_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffmember',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 27, 20, 34, 3, 166022, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffmember',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 27, 20, 34, 8, 702282, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffmember',
            name='uuid',
            field=models.CharField(max_length=32, default='', editable=False, blank=True),
        ),
    ]

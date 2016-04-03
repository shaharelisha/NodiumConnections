# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0017_auto_20160403_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 3, 2, 27, 17, 586978, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 3, 2, 27, 25, 762590, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='uuid',
            field=models.CharField(blank=True, max_length=32, default='', editable=False),
        ),
    ]

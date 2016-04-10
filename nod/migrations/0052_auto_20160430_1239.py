# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0051_auto_20160408_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motreminder',
            name='issue_date',
            field=models.DateField(default=datetime.date(2016, 4, 30)),
        ),
        migrations.AlterField(
            model_name='motreminder',
            name='renewal_test_date',
            field=models.DateField(default=datetime.date(2016, 4, 30)),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='timereport',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 30, 12, 39, 3, 87131)),
        ),
    ]

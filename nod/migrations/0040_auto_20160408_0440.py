# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0039_auto_20160408_0120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motreminder',
            name='issue_date',
            field=models.DateField(default=datetime.date(2016, 4, 8)),
        ),
        migrations.AlterField(
            model_name='motreminder',
            name='renewal_test_date',
            field=models.DateField(default=datetime.date(2016, 4, 8)),
        ),
    ]

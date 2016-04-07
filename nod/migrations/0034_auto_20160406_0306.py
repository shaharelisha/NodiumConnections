# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0033_auto_20160405_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparepartsreport',
            name='reporting_period',
            field=models.CharField(max_length=21),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0048_auto_20160408_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timereport',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='timereport',
            name='start_date',
            field=models.DateField(),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0047_auto_20160408_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timereport',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='timereport',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]

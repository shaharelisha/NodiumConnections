# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0043_auto_20160408_0716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexiblediscount',
            name='discount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='flexiblediscount',
            name='lower_range',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='flexiblediscount',
            name='upper_range',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='mechanic',
            name='hourly_pay',
            field=models.FloatField(),
        ),
    ]

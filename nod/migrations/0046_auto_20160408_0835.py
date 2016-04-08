# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0045_auto_20160408_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='price',
            field=models.FloatField(),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0020_auto_20160403_0448'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpart',
            name='sufficient_quantity',
            field=models.BooleanField(default=True),
        ),
    ]

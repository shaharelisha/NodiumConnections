# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0032_auto_20160405_1503'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='job',
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(default=1, to='nod.Invoice'),
            preserve_default=False,
        ),
    ]

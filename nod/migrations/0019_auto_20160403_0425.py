# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0018_auto_20160403_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='job_done',
            field=models.OneToOneField(to='nod.Job', null=True),
        ),
    ]

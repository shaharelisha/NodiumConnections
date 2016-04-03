# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('nod', '0023_auto_20160403_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerpartsorder',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='customerpartsorder',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]

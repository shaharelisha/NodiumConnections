# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0025_auto_20160403_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceControl',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(blank=True, editable=False, default='', max_length=32)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('vat', models.FloatField()),
                ('marked_up', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

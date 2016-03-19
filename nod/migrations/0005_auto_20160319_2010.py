# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0004_auto_20160319_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleReport',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(blank=True, editable=False, default='', max_length=32)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('month', models.IntegerField(default=3)),
                ('dropin_mot', models.PositiveIntegerField()),
                ('dropin_annual', models.PositiveIntegerField()),
                ('dropin_repair', models.PositiveIntegerField()),
                ('account_holders_mot', models.PositiveIntegerField()),
                ('account_holders_annual', models.PositiveIntegerField()),
                ('account_holders_repair', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 20, 10, 25, 109031, tzinfo=utc)),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0008_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResponseRateReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, editable=False, max_length=32, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('mot_reminders_sent', models.PositiveIntegerField()),
                ('mot_jobs', models.PositiveIntegerField()),
                ('mot_response_rate', models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='vehiclereport',
            name='month',
        ),
        migrations.AddField(
            model_name='vehiclereport',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]

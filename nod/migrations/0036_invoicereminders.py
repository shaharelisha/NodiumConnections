# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0035_auto_20160406_0408'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceReminders',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(max_length=32, blank=True, editable=False, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('reminder_phase', models.CharField(max_length=1, choices=[('1', 'Invoice Sent'), ('2', 'Reminder 1 Sent'), ('3', 'Reminder 2 Sent'), ('4', 'Reminder 3 Sent + Warning')], default='1')),
                ('issue_date', models.DateField(default=datetime.datetime.now)),
                ('invoice', models.ForeignKey(to='nod.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

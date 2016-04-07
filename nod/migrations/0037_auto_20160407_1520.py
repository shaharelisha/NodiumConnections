# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0036_invoicereminders'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceReminder',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(max_length=32, default='', blank=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('reminder_phase', models.CharField(choices=[('1', 'Invoice Sent'), ('2', 'Reminder 1 Sent'), ('3', 'Reminder 2 Sent'), ('4', 'Reminder 3 Sent + Warning')], default='1', max_length=1)),
                ('issue_date', models.DateField(default=datetime.datetime.now)),
                ('invoice', models.ForeignKey(to='nod.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='invoicereminders',
            name='invoice',
        ),
        migrations.DeleteModel(
            name='InvoiceReminders',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0005_auto_20160319_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='MOTReminder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, default='', editable=False, max_length=32)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('issue_date', models.DateTimeField(default=datetime.datetime.now)),
                ('renewal_test_date', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='card',
            name='payment_ptr',
        ),
        migrations.RenameField(
            model_name='vehicle',
            old_name='mot_date',
            new_name='mot_base_date',
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.DeleteModel(
            name='Card',
        ),
        migrations.AddField(
            model_name='motreminder',
            name='vehicle',
            field=models.ForeignKey(to='nod.Vehicle'),
        ),
    ]

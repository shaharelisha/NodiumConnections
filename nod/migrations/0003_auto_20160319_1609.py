# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0002_auto_20160319_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='SparePart',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(default='', editable=False, blank=True, max_length=32)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('initial_stock_level', models.IntegerField()),
                ('used', models.IntegerField()),
                ('delivery', models.IntegerField()),
                ('part', models.ForeignKey(to='nod.Part')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SparePartsReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(default='', editable=False, blank=True, max_length=32)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('reporting_period', models.IntegerField(default=3)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('parts', models.ManyToManyField(through='nod.SparePart', to='nod.Part')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 16, 9, 34, 554144, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='sparepart',
            name='report',
            field=models.ForeignKey(to='nod.SparePartsReport'),
        ),
    ]

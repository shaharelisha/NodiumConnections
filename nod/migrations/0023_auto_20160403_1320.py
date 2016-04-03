# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0022_auto_20160403_1242'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPartsOrder',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(blank=True, default='', max_length=32, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SellPart',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(blank=True, default='', max_length=32, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField()),
                ('sufficient_quantity', models.BooleanField(default=True)),
                ('order', models.ForeignKey(to='nod.CustomerPartsOrder')),
                ('part', models.ForeignKey(to='nod.Part')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='customerpartsorder',
            name='parts',
            field=models.ManyToManyField(through='nod.SellPart', to='nod.Part'),
        ),
    ]

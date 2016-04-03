# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0016_auto_20160403_0202'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderPartRelationship',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(default='', max_length=32, editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(to='nod.PartOrder')),
                ('part', models.ForeignKey(to='nod.Part')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='partorder',
            name='parts',
            field=models.ManyToManyField(through='nod.OrderPartRelationship', to='nod.Part'),
        ),
    ]

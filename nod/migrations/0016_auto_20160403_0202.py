# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0015_auto_20160402_2336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partorder',
            name='parts',
        ),
        migrations.AddField(
            model_name='invoice',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='parts',
            field=models.ManyToManyField(to='nod.Part'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='address',
            field=models.CharField(max_length=80, blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='phone_numbers',
            field=models.ManyToManyField(to='nod.PhoneModel', related_name='nod_supplier_phonenumber'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='postcode',
            field=models.CharField(max_length=8, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='job_done',
            field=models.ForeignKey(to='nod.Job', null=True),
        ),
    ]

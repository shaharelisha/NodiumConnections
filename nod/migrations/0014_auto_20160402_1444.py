# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0013_auto_20160327_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountholder',
            name='address',
            field=models.CharField(max_length=80, blank=True),
        ),
        migrations.AlterField(
            model_name='accountholder',
            name='discount_plan',
            field=models.ForeignKey(to='nod.DiscountPlan', null=True),
        ),
        migrations.AlterField(
            model_name='accountholder',
            name='postcode',
            field=models.CharField(max_length=8, blank=True),
        ),
        migrations.AlterField(
            model_name='businesscustomer',
            name='company_name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='businesscustomer',
            name='rep_role',
            field=models.CharField(max_length=80, blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='forename',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='surname',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_number',
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='sparepartsreport',
            name='reporting_period',
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='reg_number',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

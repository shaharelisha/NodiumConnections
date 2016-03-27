# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0011_auto_20160327_2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountHolder',
            fields=[
                ('customer_ptr', models.OneToOneField(parent_link=True, to='nod.Customer', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=80)),
                ('postcode', models.CharField(max_length=8)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.customer',),
        ),
        migrations.CreateModel(
            name='BusinessCustomer',
            fields=[
                ('accountholder_ptr', models.OneToOneField(parent_link=True, to='nod.AccountHolder', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=100)),
                ('rep_role', models.CharField(max_length=80)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.accountholder',),
        ),
        migrations.AddField(
            model_name='accountholder',
            name='discount_plan',
            field=models.ForeignKey(to='nod.DiscountPlan'),
        ),
    ]

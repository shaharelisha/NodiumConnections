# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0010_auto_20160327_1754'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountholders',
            name='customer_ptr',
        ),
        migrations.RemoveField(
            model_name='accountholders',
            name='discount_plan',
        ),
        migrations.RemoveField(
            model_name='businesscustomer',
            name='accountholders_ptr',
        ),
        migrations.AlterField(
            model_name='job',
            name='mechanic',
            field=models.ForeignKey(to='nod.Mechanic', null=True),
        ),
        migrations.DeleteModel(
            name='AccountHolders',
        ),
        migrations.DeleteModel(
            name='BusinessCustomer',
        ),
    ]

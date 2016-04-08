# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0042_auto_20160408_0543'),
    ]

    operations = [
        migrations.AddField(
            model_name='bay',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='customer',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='customerpartsorder',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='fixeddiscount',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='flexiblediscount',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='invoice',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='invoicereminder',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='job',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='jobpart',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='jobtask',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='motreminder',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='orderpartrelationship',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='part',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='partorder',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='payment',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='pricecontrol',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='pricereport',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='responseratereport',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='sellpart',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='sparepart',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='sparepartsreport',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='supplier',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='task',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='timereport',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='variablediscount',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
        migrations.AddField(
            model_name='vehiclereport',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
        ),
    ]

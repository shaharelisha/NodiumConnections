# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0007_auto_20160327_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('payment_ptr', models.OneToOneField(parent_link=True, to='nod.Payment', serialize=False, primary_key=True, auto_created=True)),
                ('last_4_digits', models.PositiveIntegerField()),
                ('cvv', models.PositiveSmallIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.payment',),
        ),
    ]

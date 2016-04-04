# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('nod', '0026_pricecontrol'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixedDiscount',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('uuid', models.CharField(editable=False, default='', max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('1', 'Fixed'), ('2', 'Flexible'), ('3', 'Variable')], max_length=1)),
                ('discount', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FlexibleDiscount',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('uuid', models.CharField(editable=False, default='', max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('1', 'Fixed'), ('2', 'Flexible'), ('3', 'Variable')], max_length=1)),
                ('lower_range', models.FloatField()),
                ('upper_range', models.FloatField()),
                ('discount', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VariableDiscount',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('uuid', models.CharField(editable=False, default='', max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('1', 'Fixed'), ('2', 'Flexible'), ('3', 'Variable')], max_length=1)),
                ('mot_discount', models.FloatField()),
                ('annual_discount', models.FloatField()),
                ('repair_discount', models.FloatField()),
                ('parts_discount', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='accountholder',
            name='discount_plan',
        ),
        migrations.AddField(
            model_name='accountholder',
            name='content_type',
            field=models.ForeignKey(null=True, blank=True, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='accountholder',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='DiscountPlan',
        ),
    ]

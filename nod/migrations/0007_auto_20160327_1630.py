# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0006_auto_20160319_2031'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dropin',
            fields=[
                ('customer_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='nod.Customer', parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.customer',),
        ),
        migrations.CreateModel(
            name='EmailModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=1, default='1', choices=[('1', 'Work'), ('2', 'Home'), ('3', 'Other')])),
                ('address', models.EmailField(max_length=120)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=1, default='1', choices=[('1', 'Work'), ('2', 'Home'), ('3', 'Fax'), ('4', 'Other')])),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '0xxxxxxxxxx'. NSN length of up to 10 digits.", regex='^0\\d{7,10}$')], unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('company_name', models.CharField(max_length=100)),
                ('emails', models.ManyToManyField(to='nod.EmailModel', related_name='nod_supplier_emailaddress')),
            ],
        ),
        migrations.RemoveField(
            model_name='businesscustomer',
            name='fax_number',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='email',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='partorder',
            name='company',
        ),
        migrations.AddField(
            model_name='job',
            name='type',
            field=models.CharField(max_length=1, default=1, choices=[('1', 'MOT'), ('2', 'Repair'), ('3', 'Annual')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='work_carried_out',
            field=models.CharField(max_length=1000, blank=True),
        ),
        migrations.AlterField(
            model_name='jobtask',
            name='duration',
            field=models.DurationField(null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='emails',
            field=models.ManyToManyField(to='nod.EmailModel', related_name='nod_customer_emailaddress'),
        ),
        migrations.AddField(
            model_name='customer',
            name='phone_numbers',
            field=models.ManyToManyField(to='nod.PhoneModel', related_name='nod_customer_phonenumber'),
        ),
        migrations.AddField(
            model_name='partorder',
            name='supplier',
            field=models.ForeignKey(to='nod.Supplier', default=1),
            preserve_default=False,
        ),
    ]

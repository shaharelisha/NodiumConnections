# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('personal_id', models.CharField(unique=True, max_length=15)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bay',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('bay_type', models.CharField(choices=[('1', 'MOT Bay'), ('2', 'Repair Bay')], max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('personal_id', models.CharField(unique=True, max_length=15)),
                ('forename', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=120)),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '0xxxxxxxxxx'. NSN length of up to 10 digits.", regex='^0\\d{7,10}$')], max_length=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Franchisee',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('personal_id', models.CharField(unique=True, max_length=15)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('invoice_number', models.PositiveIntegerField(unique=True)),
                ('service_price', models.FloatField()),
                ('issue_date', models.DateField()),
                ('status', models.CharField(choices=[('1', 'Not Paid'), ('2', 'Paid'), ('3', 'Late'), ('4', 'Super Late')], max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('job_number', models.PositiveIntegerField()),
                ('work_carried_out', models.CharField(max_length=1000)),
                ('time_spent', models.DurationField()),
                ('estimated_job_time', models.DurationField()),
                ('actual_time', models.DurationField()),
                ('status', models.CharField(default='3', choices=[('1', 'Complete'), ('2', 'Started'), ('3', 'Pending')], max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mechanic',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('personal_id', models.CharField(unique=True, max_length=15)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('part_number', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('manufacturer', models.CharField(max_length=200)),
                ('vehicle_type', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
                ('price', models.FloatField()),
                ('code', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('low_level_threshold', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('amount', models.FloatField()),
                ('type', models.CharField(choices=[('1', 'Cash'), ('2', 'Card'), ('3', 'Cheque')], max_length=1)),
                ('time_paid', models.TimeField()),
                ('date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Receptionist',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('personal_id', models.CharField(unique=True, max_length=15)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('work_request', models.CharField(max_length=100)),
                ('status', models.CharField(default='3', choices=[('1', 'Complete'), ('2', 'Started'), ('3', 'Pending')], max_length=1)),
                ('job', models.ForeignKey(to='nod.Job')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('uuid', models.CharField(default='', editable=False, max_length=32, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('reg_number', models.CharField(max_length=100)),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('engine_serial', models.CharField(max_length=100)),
                ('chassis_number', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('mot_date', models.DateField()),
                ('type', models.CharField(choices=[('1', 'Vans/Light Vehicles'), ('2', 'Cars')], max_length=1)),
                ('bay', models.ForeignKey(to='nod.Bay')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('payment_ptr', models.OneToOneField(serialize=False, primary_key=True, to='nod.Payment', auto_created=True, parent_link=True)),
                ('card_16_digit', models.BigIntegerField()),
                ('transaction_id', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.payment',),
        ),
        migrations.CreateModel(
            name='ExistingCustomer',
            fields=[
                ('customer_ptr', models.OneToOneField(serialize=False, primary_key=True, to='nod.Customer', auto_created=True, parent_link=True)),
                ('address', models.CharField(max_length=80)),
                ('postcode', models.CharField(max_length=8)),
                ('fax_number', models.CharField(validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '0xxxxxxxxxx'. NSN length of up to 10 digits.", regex='^0\\d{7,10}$')], max_length=15)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.customer',),
        ),
        migrations.AddField(
            model_name='payment',
            name='customer',
            field=models.ForeignKey(to='nod.Customer'),
        ),
        migrations.AddField(
            model_name='job',
            name='vehicle',
            field=models.ForeignKey(to='nod.Vehicle'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='job_done',
            field=models.ForeignKey(to='nod.Job'),
        ),
    ]

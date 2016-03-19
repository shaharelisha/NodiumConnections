# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nod', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountHolders',
            fields=[
                ('customer_ptr', models.OneToOneField(primary_key=True, to='nod.Customer', parent_link=True, auto_created=True, serialize=False)),
                ('address', models.CharField(max_length=80)),
                ('postcode', models.CharField(max_length=8)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.customer',),
        ),
        migrations.CreateModel(
            name='DiscountPlan',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=32, editable=False, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=1, choices=[('1', 'Fixed'), ('2', 'Flexible'), ('3', 'Variable')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JobPart',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=32, editable=False, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JobTask',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=32, editable=False, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('status', models.CharField(default='3', max_length=1, choices=[('1', 'Complete'), ('2', 'Started'), ('3', 'Pending')])),
                ('duration', models.DurationField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffMember',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('role', models.CharField(max_length=1, choices=[('1', 'Mechanic'), ('2', 'Foreperson'), ('3', 'Franchisee'), ('4', 'Receptionist'), ('5', 'Admin')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='admin',
            name='user',
        ),
        migrations.RemoveField(
            model_name='existingcustomer',
            name='customer_ptr',
        ),
        migrations.RemoveField(
            model_name='franchisee',
            name='user',
        ),
        migrations.RemoveField(
            model_name='receptionist',
            name='user',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='type',
            new_name='payment_type',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='personal_id',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='service_price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='status',
        ),
        migrations.RemoveField(
            model_name='job',
            name='actual_time',
        ),
        migrations.RemoveField(
            model_name='job',
            name='estimated_job_time',
        ),
        migrations.RemoveField(
            model_name='job',
            name='time_spent',
        ),
        migrations.RemoveField(
            model_name='mechanic',
            name='id',
        ),
        migrations.RemoveField(
            model_name='mechanic',
            name='personal_id',
        ),
        migrations.RemoveField(
            model_name='mechanic',
            name='user',
        ),
        migrations.RemoveField(
            model_name='part',
            name='part_number',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='time_paid',
        ),
        migrations.RemoveField(
            model_name='task',
            name='job',
        ),
        migrations.RemoveField(
            model_name='task',
            name='status',
        ),
        migrations.RemoveField(
            model_name='task',
            name='work_request',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='bay',
        ),
        migrations.AddField(
            model_name='customer',
            name='date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='invoice',
            name='reminder_phase',
            field=models.CharField(default='1', max_length=1, choices=[('1', 'Invoice Sent'), ('2', 'Reminder 1 Sent'), ('3', 'Reminder 2 Sent'), ('4', 'Reminder 3 Sent + Warning')]),
        ),
        migrations.AddField(
            model_name='job',
            name='booking_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='job',
            name='mechanic',
            field=models.ForeignKey(default=1, to='nod.Mechanic'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mechanic',
            name='hourly_pay',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='job',
            field=models.ForeignKey(default=1, to='nod.Job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='estimated_time',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='task',
            name='task_number',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='customer',
            field=models.ForeignKey(default=1, to='nod.Customer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='issue_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 15, 21, 15, 299075, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='mot_date',
            field=models.DateField(null=True),
        ),
        migrations.CreateModel(
            name='BusinessCustomer',
            fields=[
                ('accountholders_ptr', models.OneToOneField(primary_key=True, to='nod.AccountHolders', parent_link=True, auto_created=True, serialize=False)),
                ('company_name', models.CharField(max_length=100)),
                ('rep_role', models.CharField(max_length=80)),
                ('fax_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^0\\d{7,10}$', message="Phone number must be entered in the format: '0xxxxxxxxxx'. NSN length of up to 10 digits.")], max_length=15)),
            ],
            options={
                'abstract': False,
            },
            bases=('nod.accountholders',),
        ),
        migrations.DeleteModel(
            name='Admin',
        ),
        migrations.DeleteModel(
            name='Bay',
        ),
        migrations.DeleteModel(
            name='ExistingCustomer',
        ),
        migrations.DeleteModel(
            name='Franchisee',
        ),
        migrations.DeleteModel(
            name='Receptionist',
        ),
        migrations.AddField(
            model_name='jobtask',
            name='job',
            field=models.ForeignKey(to='nod.Job'),
        ),
        migrations.AddField(
            model_name='jobtask',
            name='task',
            field=models.ForeignKey(to='nod.Task'),
        ),
        migrations.AddField(
            model_name='jobpart',
            name='job',
            field=models.ForeignKey(to='nod.Job'),
        ),
        migrations.AddField(
            model_name='jobpart',
            name='part',
            field=models.ForeignKey(to='nod.Part'),
        ),
        migrations.AddField(
            model_name='accountholders',
            name='discount_plan',
            field=models.ForeignKey(to='nod.DiscountPlan'),
        ),
        migrations.AddField(
            model_name='job',
            name='parts',
            field=models.ManyToManyField(through='nod.JobPart', to='nod.Part'),
        ),
        migrations.AddField(
            model_name='job',
            name='tasks',
            field=models.ManyToManyField(through='nod.JobTask', to='nod.Task'),
        ),
        migrations.AddField(
            model_name='mechanic',
            name='staffmember_ptr',
            field=models.OneToOneField(primary_key=True, parent_link=True, to='nod.StaffMember', default=1, auto_created=True, serialize=False),
            preserve_default=False,
        ),
    ]

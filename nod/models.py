from django.db import models

import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class RandomUUIDModel(models.Model):
    uuid = models.CharField(max_length=32, editable=False, blank=True, null=False, default='')

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        return super(RandomUUIDModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Customer(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    # personal_id = models.CharField(max_length=15, unique=True) #check ID string length
    forename = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=120)
    date = models.DateField(default=timezone.now())
    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15)

    def __str__(self):
        return self.forename + " " + self.surname


class AccountHolders(Customer):
    address = models.CharField(max_length=80)
    postcode = models.CharField(max_length=8)
    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    fax_number = models.CharField(validators=[phone_regex], max_length=15)

    def __str__(self):
        return self.forename + ' ' + self.surname


class BusinessCustomer(AccountHolders):
    company_name = models.CharField(max_length=100)
    rep_role = models.CharField(max_length=80)

    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    fax_number = models.CharField(validators=[phone_regex], max_length=15)

    def __str__(self):
        return self.company_name



class StaffMember(models.Model):
    # personal_id = models.CharField(max_length=15, unique=True) #TODO: check this.
    user = models.OneToOneField(User)
    ROLES = [
        ("1", "Mechanic"),
        ("2", "Foreperson"),
        ("3", "Franchisee"),
        ("4", "Receptionist"),
        ("5", "Admin"),
    ]
    role = models.CharField(max_length=1, choices=ROLES)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Mechanic(StaffMember):
    hourly_pay = models.FloatField()
    role = '1'

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    #TODO: generate report data methods


class Payment(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    amount = models.FloatField()
    PAYMENT_TYPES = (
        ('1', 'Cash'),
        ('2', 'Card'),
        ('3', 'Cheque'),
    )
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPES)

    #not the same as the timestamp ones
    time_paid = models.TimeField()
    date = models.DateField()
    customer = models.ForeignKey(Customer)


#TODO: possible to automatically set to payment type = card?
class Card(Payment):
    card_16_digit = models.BigIntegerField()
    payment_type = '2'
    transaction_id = models.CharField(max_length=100)


# class Bay(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
#     BAYS = [
#         ('1', 'MOT Bay'),
#         ('2', 'Repair Bay'),
#     ]
#     bay_type = models.CharField(choices=BAYS, max_length=1)


class Vehicle(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    reg_number = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    engine_serial = models.CharField(max_length=100)
    chassis_number = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    mot_date = models.DateField()
    VEHICLE_TYPE = (
        ('1', 'Vans/Light Vehicles'),
        ('2', 'Cars'),
    )
    type = models.CharField(max_length=1, choices=VEHICLE_TYPE)
    #TODO: customer okay? or does it need to be a generic relationship to all its children?
    customer = models.ForeignKey(Customer)
    # bay = models.ForeignKey(Bay) #?????????


class Task(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    # job = models.ForeignKey(Job)
    task_number = models.PositiveIntegerField()
    description = models.CharField(max_length=300) #from choice list??
    estimated_time = models.DurationField()


class JobTask(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    tasks = models.ManyToManyField(Task, through="Job")
    TASK_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending')
    ]
    status = models.CharField(max_length=1, choices=TASK_STATUS, default='3')


class Part(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    # part_number = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=100) #? choices?
    year = models.PositiveIntegerField() #CHECK YEAR IN EVALUCOM DB
    price = models.FloatField() #CHANGE DESIGN CLASS TO FLOAT
    code = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    low_level_threshold = models.PositiveIntegerField()

    def increase_quantity_by_one(self):
        q = self.quantity
        q += 1
        self.quantity = q
        return q

    def decrease_quantity_by_one(self):
        q = self.quantity
        q -= 1
        self.quantity = q
        return q

    def set_new_quantity(self, quantity):
        self.quantity = quantity
        return quantity


class JobPart(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    parts = models.ManyToManyField(Part, through="Job")
    quantity = models.PositiveIntegerField()
    cost = models.FloatField()

    #RETHINK. THIS IS WRONG.

class Job(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    # task = models.ForeignKey(Task)
    job_tasks = models.ForeignKey(JobTask)
    # part = models.ForeignKey(Part)
    job_parts = models.ForeignKey(JobPart)
    job_number = models.PositiveIntegerField()
    vehicle = models.ForeignKey(Vehicle)
    real_duration = models.DurationField()
    parts = models.ManyToManyField(Part)
    JOB_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending')
    ]
    status = models.CharField(max_length=1, choices=JOB_STATUS, default='3')
    booking_date = models.DateTimeField()
    # work_request = models.CharField(max_length=1000)
    #TODO: make it a list?
    work_carried_out = models.CharField(max_length=1000)
    tasks = models.ManyToManyField(Task)

    # iterates through all the assigned tasks to the job, and adds the estimated
    # time per task to get the overall estimated time for the job.
    def calculate_estimated_time(self):
        estimated_time = 0
        for t in self.jobtask.task_set:
            estimated_time += t.estimated_time

        return estimated_time

    # generates invoice assigned to the given job object
    def create_invoice(self):
        return Invoice.objects.create(job=self)

    #TODO: this doesn't go here
    def update_status(self):
        complete = True
        for t in self.jobtask_set:
            if t.status != '1':
                complete = False
                break
        if complete:
            self.status = "1"
        return self.status
    #TODO: anything regarding 'started' vs 'pending' statuses?


class Invoice(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    invoice_number = models.PositiveIntegerField(unique=True)
    job_done = models.ForeignKey(Job)
    service_price = models.FloatField()
    issue_date = models.DateField()
    INVOICE_STATUS = [
        ('1', 'Not Paid'),
        ('2', 'Paid'),
        ('3', 'Late'),
        ('4', 'Super Late')
    ]
    status = models.CharField(choices=INVOICE_STATUS, max_length=1)



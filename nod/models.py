from django.db import models

import uuid

from django.db import models
# from django.utils import timezone
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


# class EmailModel(TimestampedModel, SoftDeleteModel):
#     EMAIL_TYPES = (
#         ('1', 'Work'),
#         ('2', 'Home'),
#         ('3', 'Other'),
#     )
#
#     type = models.CharField(max_length=1, choices=EMAIL_TYPES, default='1')
#     address = models.EmailField(max_length=120)
#
#     def __str__(self):
#         return self.address
#
#
# class PhoneModel(TimestampedModel, SoftDeleteModel):
#     PHONE_TYPES = (
#         ('1', 'Work'),
#         ('2', 'Home'),
#         ('3', 'Other'),
#     )
#
#     type = models.CharField(max_length=1, choices=PHONE_TYPES, default='1')
#     phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
#                                  message="Phone number must be entered in the format:"
#                                          " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
#     phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)                # unique = True
#
#     def save(self, *args, **kwargs):
#         clean = self.full_clean()
#         if clean is None:
#             super(PhoneModel, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return self.phone_number


class Customer(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    personal_id = models.CharField(max_length=15, unique=True) #check ID string length
    forename = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=120)

    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    # emails = models.ManyToManyField(EmailModel, related_name='%(app_label)s_%(class)s_emailaddress')
    # phone_numbers = models.ManyToManyField(PhoneModel, related_name='%(app_label)s_%(class)s_phonenumber')

    def __str__(self):
        return self.forename + " " + self.surname

    # def get_emails(self):
    #         emails = self.emails.filter(is_deleted=False)
    #         return emails
    #
    # def get_emails(self):
    #     return "; ".join([s.address for s in self.emails.filter(is_deleted=False)])

    # def get_phones(self):
    #     phone_numbers = self.phone_numbers.filter(is_deleted=False)
    #     return phone_numbers
    #
    # def get_phones(self):
    #     return ", ".join([s.phone_number for s in self.phone_numbers.filter(is_deleted=False)])


class ExistingCustomer(Customer):
    address = models.CharField(max_length=80)
    postcode = models.CharField(max_length=8)
    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    fax_number = models.CharField(validators=[phone_regex], max_length=15)

    def __str__(self):
        return self.forename + ' ' + self.surname


class StaffMember(models.Model):
    personal_id = models.CharField(max_length=15, unique=True) #TODO: check this.
    user = models.OneToOneField(User, null=True)

    # def __str__(self):
    #     return self.forename + ' ' + self.surname

    class Meta:
        abstract = True


class Franchisee(StaffMember):
    def __str__(self):
        return self.forename + ' ' + self.surname


class Admin(StaffMember):
    def __str__(self):
        return self.forename + ' ' + self.surname


class Mechanic(StaffMember):
    def __str__(self):
        return self.forename + ' ' + self.surname


class Receptionist(StaffMember):
    def __str__(self):
        return self.forename + ' ' + self.surname


# class Foreperson(Receptionist, Mechanic):
#     def __str__(self):
#         return self.forename + ' ' + self.surname


class Payment(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    amount = models.FloatField()
    PAYMENT_TYPES = (
        ('1', 'Cash'),
        ('2', 'Card'),
        ('3', 'Cheque'),
    )
    type = models.CharField(max_length=1, choices=PAYMENT_TYPES)

    #not the same as the timestamp ones
    time_paid = models.TimeField()
    date = models.DateField()
    customer = models.ForeignKey(Customer)


#TODO: possible to automatically set to payment type = card?
class Card(Payment):
    card_16_digit = models.BigIntegerField()
    transaction_id = models.CharField(max_length=100)


class Bay(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    BAYS = [
        ('1', 'MOT Bay'),
        ('2', 'Repair Bay'),
    ]
    bay_type = models.CharField(choices=BAYS, max_length=1)


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
    bay = models.ForeignKey(Bay) #?????????



class Job(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    job_number = models.PositiveIntegerField()
    # work_request = models.CharField(max_length=1000)
    work_carried_out = models.CharField(max_length=1000)
    time_spent = models.DurationField()
    estimated_job_time = models.DurationField()
    actual_time = models.DurationField()
    JOB_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending')
    ]
    status = models.CharField(max_length=1, choices=JOB_STATUS, default='3')
    vehicle = models.ForeignKey(Vehicle)


# class JobSheet(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
#     job = models.ForeignKey(Job)
#     owner = job.customer #maybe don't automate it here, keep it open and flexible?
#     #vehicle
#     #model


class Task(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    job = models.ForeignKey(Job)
    # description = models.CharField(max_length=1000) #from choice list??
    work_request = models.CharField(max_length=100) #from choice list??
    TASK_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending')
    ]
    status = models.CharField(max_length=1, choices=TASK_STATUS, default='3')


class Part(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    part_number = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=100) #? choices?
    year = models.PositiveIntegerField() #CHECK YEAR IN EVALUCOM DB
    price = models.FloatField() #CHANGE DESIGN CLASS TO FLOAT
    code = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    low_level_threshold = models.PositiveIntegerField()


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



from django.db import models

import uuid

from django.utils import timezone
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned


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


class EmailModel(TimestampedModel, SoftDeleteModel):
    EMAIL_TYPES = (
        ('1', 'Work'),
        ('2', 'Home'),
        ('3', 'Other'),
    )

    type = models.CharField(max_length=1, choices=EMAIL_TYPES, default='1')
    address = models.EmailField(max_length=120)

    def __str__(self):
        return self.address


class PhoneModel(TimestampedModel, SoftDeleteModel):
    PHONE_TYPES = (
        ('1', 'Work'),
        ('2', 'Home'),
        ('3', 'Fax'),
        ('4', 'Other'),
    )

    type = models.CharField(max_length=1, choices=PHONE_TYPES, default='1')
    phone_regex = RegexValidator(regex=r'^0\d{7,10}$',
                                 message="Phone number must be entered in the format:"
                                         " '0xxxxxxxxxx'. NSN length of up to 10 digits.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)                # unique = True

    def save(self, *args, **kwargs):
        # try:
        clean = self.full_clean()
        if clean is None:
            # print("yay")
            super(PhoneModel, self).save(*args, **kwargs)
        # except ValidationError:
        #     # print("Invalid")
        #     pass

    def __str__(self):
        return self.phone_number


class PriceControl(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    vat = models.DecimalField(max_digits=4, decimal_places=2)
    marked_up = models.DecimalField(max_digits=4, decimal_places=2)


class Part(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    # part_number = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100)
    years = models.CharField(max_length=9)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    code = models.CharField(max_length=20, unique=True)
    quantity = models.PositiveIntegerField()
    low_level_threshold = models.PositiveIntegerField()

    def __str__(self):
        return self.name

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

    def get_markedup_price(self):
        markup = PriceControl.objects.get().marked_up/100
        price = self.price + (self.price * markup)
        return price

    def delivered_parts(self, start_date, end_date):
        quantity = 0
        for p in self.partorder_set.filter(is_deleted=False, order__date__lte=end_date, order__date__gte=start_date):
            quantity += p.quantity

        return quantity

    # def sold_parts(self, start_date, end_date):
    #     quantity = 0
    #     for order in self.customerpartsorder_set.filter(is_deleted=False, date__lte=end_date, date__gte=start_date):
    #         for p in order.parts.all():
    #             if p.part == self:
    #                 quantity += p.quantity
    #
    #
    #     return quantity

    def sold_parts(self, start_date, end_date):
        quantity = 0
        for part in self.sellpart_set.filter(is_deleted=False, order__date__lte=end_date, order__date__gte=start_date):
            quantity += part.quantity
            print(part.quantity)

        return quantity

    def used_parts(self, start_date, end_date):
        quantity = 0
        for p in self.jobpart_set.filter(is_deleted=False, job__booking_date__lte=end_date, job__booking_date__gte=start_date):
            quantity += p.quantity

        return quantity

    def total_used_parts(self, start_date, end_date):
        quantity = self.used_parts(start_date=start_date, end_date=end_date) + \
                   self.sold_parts(start_date=start_date, end_date=end_date)

        return quantity


class CustomerPartsOrder(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    # generic relationship limited to the different types of customers
    limit = Q(app_label="nod", model="dropin") | \
        Q(app_label="nod", model="accountholder") | \
        Q(app_label="nod", model="businesscustomer")
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(default=timezone.datetime.now)
    parts = models.ManyToManyField(Part, through="SellPart")

    def get_parts_price(self):
        price = 0
        for part in self.sellpart_set.all(): #not self.parts
            unit_price = part.get_markedup_price()
            quantity = part.quantity
            price += unit_price*quantity
        return price

    def get_price(self):
        return self.get_parts_price()

    def get_vat(self):
        vat = float(PriceControl.objects.get().vat/100)
        total_vat = float(self.get_price()) * vat
        return total_vat

    def get_grand_total(self):
        return float(self.get_price()) + self.get_vat()


class Customer(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    # personal_id = models.CharField(max_length=15, unique=True) #check ID string length
    forename = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=100, blank=True)
    emails = models.ManyToManyField(EmailModel, related_name='%(app_label)s_%(class)s_emailaddress')
    phone_numbers = models.ManyToManyField(PhoneModel, related_name='%(app_label)s_%(class)s_phonenumber')
    date = models.DateField(default=timezone.datetime.now, null=True)
    part_orders = GenericRelation(CustomerPartsOrder)

    def __str__(self):
        return self.forename + " " + self.surname

    def full_name(self):
        return self.forename + " " + self.surname

    def list_emails(self):
        return "; ".join([s.address for s in self.emails.filter(is_deleted=False)])

    def get_phones(self):
        return ", ".join([s.phone_number for s in self.phone_numbers.filter(is_deleted=False)])

    def get_unpaid_invoices(self):
        invoices = []
        for v in self.vehicle_set.filter(is_deleted=False):
            for j in v.job_set.filter(is_deleted=False, status='1'):
                if j.invoice.paid is False:
                    invoices.append(j.invoice)
        for o in self.part_orders.filter(is_deleted=False):
            if o.invoice.paid is False:
                invoices.append(o.invoice)
        return invoices


class Dropin(Customer):
    def __str__(self):
        return self.forename + " " + self.surname

    # TODO: needs to be checked between dates.
    def get_number_mot_jobs(self):
        mot = 0
        for v in self.vehicle_set:
            for job in v.job_set:
                if job.type is '1':
                    mot += 1
        return mot

    def get_number_repair_jobs(self):
        repair = 0
        for v in self.vehicle_set:
            for job in v.job_set:
                if job.type is '2':
                    repair += 1
        return repair

    def get_number_annual_jobs(self):
        annual = 0
        for v in self.vehicle_set:
            for job in v.job_set:
                if job.type is '1':
                    annual += 1
        return annual


class AccountHolder(Customer):
    address = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    suspended = models.BooleanField(default=False)

    limit = Q(app_label="nod", model="fixeddiscount") | \
        Q(app_label="nod", model="flexiblediscount") | \
        Q(app_label="nod", model="variablediscount")
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.forename + ' ' + self.surname

    def full_address(self):
        return u"%s, %s" % (self.address, self.postcode)

class BusinessCustomer(AccountHolder):
    company_name = models.CharField(max_length=100, blank=True)
    rep_role = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.company_name

    def rep(self):
        return self.forename + ' ' + self.surname + ", " + self.rep_role


class Supplier(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    company_name = models.CharField(max_length=100)
    emails = models.ManyToManyField(EmailModel, related_name='%(app_label)s_%(class)s_emailaddress')
    phone_numbers = models.ManyToManyField(PhoneModel, related_name='%(app_label)s_%(class)s_phonenumber')
    address = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return self.company_name

    def full_address(self):
        return u"%s, %s" % (self.address, self.postcode)

    def get_emails(self):
        return "; ".join([s.address for s in self.emails.filter(is_deleted=False)])

    def get_phones(self):
        return ", ".join([s.phone_number for s in self.phone_numbers.filter(is_deleted=False)])


class DiscountPlan(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
    PLAN = [
        ('1', 'Fixed'),
        ('2', 'Flexible'),
        ('3', 'Variable'),
    ]
    type = models.CharField(choices=PLAN, max_length=1)
    customer = GenericRelation(AccountHolder)

    def __str__(self):
        type = next(name for value, name in DiscountPlan.PLAN if value==self.type)
        return type

    class Meta:
        abstract = True

# one object of this type
class FixedDiscount(DiscountPlan):
    discount = models.DecimalField(max_digits=4, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(FixedDiscount, self).__init__(*args, **kwargs)
        self.type = '1'


class FlexibleDiscount(DiscountPlan):
    lower_range = models.DecimalField(max_digits=4, decimal_places=2)
    upper_range = models.DecimalField(max_digits=4, decimal_places=2)
    discount = models.DecimalField(max_digits=4, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(FlexibleDiscount, self).__init__(*args, **kwargs)
        self.type = '2'


# there will be one object of this type
class VariableDiscount(DiscountPlan):
    mot_discount = models.DecimalField(max_digits=4, decimal_places=2)
    annual_discount = models.DecimalField(max_digits=4, decimal_places=2)
    repair_discount = models.DecimalField(max_digits=4, decimal_places=2)
    parts_discount = models.DecimalField(max_digits=4, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(VariableDiscount, self).__init__(*args, **kwargs)
        self.type = '3'


class StaffMember(SoftDeleteModel, TimestampedModel, RandomUUIDModel):
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

    def full_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def user_name(self):
        return self.user.username

class Mechanic(StaffMember):
    hourly_pay = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

# TODO:
    #TODO: generate report data methods


class Bay(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    BAYS = [
        ('1', 'MOT Bay'),
        ('2', 'Repair Bay'),
    ]
    bay_type = models.CharField(choices=BAYS, max_length=1)
    total_spots = models.PositiveSmallIntegerField()
    free_spots = models.PositiveIntegerField()

    def __str__(self):
        bay_name = next(name for value, name in Bay.BAYS if value==self.bay_type)
        return bay_name


class Vehicle(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    reg_number = models.CharField(max_length=100, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    engine_serial = models.CharField(max_length=100)
    chassis_number = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    mot_base_date = models.DateField(null=True) # required?
    VEHICLE_TYPE = (
        ('1', 'Van/Light Vehicle'),
        ('2', 'Car'),
    )
    type = models.CharField(max_length=1, choices=VEHICLE_TYPE)
    #TODO: customer okay? or does it need to be a generic relationship to all its children?
    customer = models.ForeignKey(Customer)
    # bay = models.ForeignKey(Bay) #?????????

    def __str__(self):
        return self.reg_number

    def get_customer(self):
        return self.customer


class Task(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    task_number = models.PositiveIntegerField()
    description = models.CharField(max_length=300) #from choice list??
    estimated_time = models.DurationField(default=timedelta())

    def __str__(self):
        return self.description


class Job(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    tasks = models.ManyToManyField(Task, through="JobTask")
    parts = models.ManyToManyField(Part, through="JobPart")
    job_number = models.PositiveIntegerField(unique=True)
    vehicle = models.ForeignKey(Vehicle)
    JOB_TYPE = [
        ('1', 'MOT'),
        ('2', 'Repair'),
        ('3', 'Annual')
    ]
    type = models.CharField(max_length=1, choices=JOB_TYPE)
    bay = models.ForeignKey(Bay)
    JOB_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending')
    ]
    status = models.CharField(max_length=1, choices=JOB_STATUS, default='3')
    booking_date = models.DateTimeField(default=timezone.datetime.now)
    #TODO: make it a list?
    work_carried_out = models.CharField(max_length=1000, blank=True)
    mechanic = models.ForeignKey(Mechanic, null=True)

    # iterates through all the assigned tasks to the job, and adds the estimated
    # time per task to get the overall estimated time for the job.
    def calculate_estimated_time(self):
        estimated_time = 0
        for t in self.tasks: #or self.jobtask_set
            estimated_time += t.estimated_time

        return estimated_time

    def get_duration(self):
        time = 0
        for t in self.jobtask_set.all(): #not self.tasks?
            time += t.duration.seconds / 3600
        # time = float(time)
        # time / 3600
        return time

    def get_labour_price(self):
        time = self.get_duration()
        rate = self.mechanic.hourly_pay
        return float(time)*float(rate)

    def get_parts_price(self):
        price = 0
        for part in self.jobpart_set.all(): #not self.parts
            unit_price = part.part.price
            quantity = part.quantity
            price += unit_price*quantity
        return price

    def get_price(self):
        return float(self.get_labour_price()) + float(self.get_parts_price())

    def get_vat(self):
        vat = float(PriceControl.objects.get().vat/100)
        total_vat = float(self.get_price()) * vat
        return total_vat

    def get_grand_total(self):
        return self.get_price() + self.get_vat()

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

    def get_customer(self):
        return self.vehicle.get_customer()


class JobTask(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    task = models.ForeignKey(Task)
    job = models.ForeignKey(Job)
    TASK_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending'),
    ]
    status = models.CharField(max_length=1, choices=TASK_STATUS, default='3')
    duration = models.DurationField(null=True)


class JobPart(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    part = models.ForeignKey(Part)
    job = models.ForeignKey(Job)
    quantity = models.PositiveIntegerField()
    sufficient_quantity = models.BooleanField(default=True)

    def get_cost(self):
        return self.part.get_markedup_price() * self.quantity


class SellPart(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    part = models.ForeignKey(Part)
    order = models.ForeignKey(CustomerPartsOrder)
    quantity = models.PositiveIntegerField()
    sufficient_quantity = models.BooleanField(default=True)

    def get_markedup_price(self):
        markup = PriceControl.objects.get().marked_up/100
        price = self.part.price + (self.part.price * markup)
        return price

    def get_cost(self):
        return self.part.get_markedup_price() * self.quantity


class Invoice(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    invoice_number = models.PositiveIntegerField(unique=True)
    job_done = models.OneToOneField(Job, null=True)
    part_order = models.OneToOneField(CustomerPartsOrder, null=True)
    parts_for_job = models.ManyToManyField(JobPart)
    parts_sold = models.ManyToManyField(SellPart)
    issue_date = models.DateField(default=timezone.datetime.now)
    INVOICE_STATUS = [
        ('1', 'Invoice Sent'),
        ('2', 'Reminder 1 Sent'),
        ('3', 'Reminder 2 Sent'),
        ('4', 'Reminder 3 Sent + Warning'),

    ]
    reminder_phase = models.CharField(choices=INVOICE_STATUS, max_length=1, default='1')
    paid = models.BooleanField(default=False)

    def get_price(self):
        if self.job_done:
            return self.job_done.get_grand_total()
        else:
            if self.part_order:
                return self.part_order.get_grand_total()
            else:
                pass
                # TODO: wtf

    def get_parts(self):
        parts = []
        for p in self.job_done.jobpart_set:
            parts.append(p.part)
        return parts

    def get_customer(self):
        if self.job_done:
            customer = self.job_done.get_customer()
            uuid = customer.uuid
            try:
                customer = BusinessCustomer.objects.get(uuid=uuid)
            except ObjectDoesNotExist:
                try:
                    customer = AccountHolder.objects.get(uuid=uuid)
                except ObjectDoesNotExist:
                    pass
            return customer
        else:
            if self.part_order:
                return self.part_order.content_object
            else:
                pass
                # TODO: wtf.

    def type(self):
        if self.job_done:
            return "Job"
        else:
            if self.part_order:
                return "Parts"

    # def get_VAT(self):
    #     vat = PriceControl.objects.get().vat/100
    #     total_vat = self.get_price() * vat
    #     return total_vat

    # def total_price(self):
    #     price = self.get_price() + self.get_VAT()
    #     return price


class InvoiceReminder(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    invoice = models.ForeignKey(Invoice)
    INVOICE_STATUS = [
        ('1', 'Invoice Sent'),
        ('2', 'Reminder 1 Sent'),
        ('3', 'Reminder 2 Sent'),
        ('4', 'Reminder 3 Sent + Warning'),

    ]
    reminder_phase = models.CharField(choices=INVOICE_STATUS, max_length=1, default='1')
    issue_date = models.DateField(default=timezone.datetime.now)



class Payment(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    PAYMENT_TYPES = (
        ('1', 'Cash'),
        ('2', 'Card'),
        ('3', 'Cheque'),
    )
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPES)
    date = models.DateField(default=timezone.datetime.now)
    # customer = models.ForeignKey(Customer)
    invoice = models.ForeignKey(Invoice)


class Card(Payment):
    last_4_digits = models.PositiveIntegerField()
    cvv = models.PositiveSmallIntegerField()

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self.payment_type = '2'


class SparePartsReport(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    parts = models.ManyToManyField(Part, through="SparePart")
    start_date = models.DateField()
    end_date = models.DateField()
    date = models.DateTimeField(default=timezone.datetime.now)

    def get_total_initial_cost(self):
        cost = 0
        for p in SparePart.objects.filter(report=self, is_deleted=False):
            cost += p.get_initial_cost()
        return cost

    def get_total_stock_cost(self):
        cost = 0
        for p in SparePart.objects.filter(report=self, is_deleted=False):
            cost += p.get_stock_cost()
        return cost

    def reporting_period(self):
        return str(self.start_date.strftime('%d/%m/%Y')) + "-" + str(self.end_date.strftime('%d/%m/%Y'))


class SparePart(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    report = models.ForeignKey(SparePartsReport)
    part = models.ForeignKey(Part)
    initial_stock_level = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    delivery = models.IntegerField(default=0)
    new_stock_level = models.IntegerField()

    def get_new_stock_level(self):
        return self.initial_stock_level - self.used + self.delivery

    def get_initial_cost(self):
        return self.part.price * self.initial_stock_level

    def get_stock_cost(self):
        return self.part.price * self.get_new_stock_level()


class PartOrder(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    date = models.DateTimeField(default=timezone.datetime.now)
    supplier = models.ForeignKey(Supplier)
    parts = models.ManyToManyField(Part, through="OrderPartRelationship")
    # arrived = models.BooleanField(default=False)

    def get_total_price(self):
        cost = 0
        for p in self.parts:
            cost += p.price
        return cost


class OrderPartRelationship(TimestampedModel, SoftDeleteModel, RandomUUIDModel):
    part = models.ForeignKey(Part)
    order = models.ForeignKey(PartOrder)
    quantity = models.PositiveIntegerField()


class PriceReport(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    date = models.DateTimeField(default=timezone.datetime.now)
    # mechanic = models.ForeignKey(Mechanic)

    def get_average_labour_price_per_mechanic(self, mechanic):
        total_price = 0
        for j in mechanic.job_set:
            total_price += j.get_labour_price()
        total_jobs = mechanic.job_set.count()
        average_price = total_price/total_jobs
        return average_price

    def get_average_price_per_mechanic(self, mechanic):
        total_price = 0
        for j in mechanic.job_set:
            total_price += j.get_price()
        total_jobs = mechanic.job_set.count()
        average_price = total_price/total_jobs
        return average_price

    def get_average_labour_price(self):
        jobs = Job.objects.filter(is_deleted=False)
        total_price = 0
        job_count = jobs.count()
        for j in jobs:
            total_price += j.get_labour_price()
        average_price = total_price/job_count
        return average_price

    def get_average_price(self):
        jobs = Job.objects.filter(is_deleted=False)
        total_price = 0
        job_count = jobs.count()
        for j in jobs:
            total_price += j.get_price() #not j.get_labour_price()?
        average_price = total_price/job_count
        return average_price


class TimeReport(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    date = models.DateTimeField(default=timezone.datetime.now)
    start_date = models.DateField()
    end_date = models.DateField()

    def get_average_time_per_mechanic(self, mechanic):
        start_date = self.start_date
        end_date = self.end_date
        total_time = 0
        for j in mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1'):
            total_time += j.get_duration() #not j.get_price()?
        total_jobs = mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1').count()
        if total_jobs == 0:
            average_time = 0.0
        else:
            average_time = total_time/total_jobs
        return round(average_time, 2)

    def get_average_time(self):
        start_date = self.start_date
        end_date = self.end_date
        jobs = Job.objects.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1')
        total_time = 0
        job_count = jobs.count()
        for j in jobs:
            total_time += j.get_duration() #not j.get_price()?
        average_time = total_time/job_count
        return round(average_time, 2)

    def get_average_time_for_mot_per_mechanic(self, mechanic):
        start_date = self.start_date
        end_date = self.end_date
        total_time = 0
        for j in mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='1'):
            total_time += j.get_duration()
        total_jobs = mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='1').count()
        if total_jobs == 0:
            average_time = 0.0
        else:
            average_time = total_time/total_jobs
        return round(average_time, 2)

    def get_average_time_for_repair_per_mechanic(self, mechanic):
        start_date = self.start_date
        end_date = self.end_date
        total_time = 0
        for j in mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='2'):
            total_time += j.get_duration()
        total_jobs = mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='2').count()
        if total_jobs == 0:
            average_time = 0.0
        else:
            average_time = total_time/total_jobs
        return round(average_time, 2)

    def get_average_time_for_annual_per_mechanic(self, mechanic):
        start_date = self.start_date
        end_date = self.end_date
        total_time = 0
        for j in mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='3'):
                total_time += j.get_duration()
        total_jobs = mechanic.job_set.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='3').count()
        if total_jobs == 0:
            average_time = 0.0
        else:
            average_time = total_time/total_jobs
        return round(average_time,2)

    def get_average_time_for_mot(self):
        start_date = self.start_date
        end_date = self.end_date
        jobs = Job.objects.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='1')
        total_time = 0
        job_count = jobs.count()
        for j in jobs:
            total_time += j.get_duration()
        if job_count == 0:
            average_time = 0.0
        else:
            average_time = total_time/job_count
        return round(average_time, 2)

    def get_average_time_for_repair(self):
        start_date = self.start_date
        end_date = self.end_date
        jobs = Job.objects.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='2')
        total_time = 0
        job_count = jobs.count()
        for j in jobs:
            total_time += j.get_duration()
        if job_count == 0:
            average_time = 0.0
        else:
            average_time = total_time/job_count
        return round(average_time, 2)

    def get_average_time_for_annual(self):
        start_date = self.start_date
        end_date = self.end_date
        jobs = Job.objects.filter(is_deleted=False, booking_date__gte=start_date, booking_date__lte=end_date, status='1', type='3')
        total_time = 0
        job_count = jobs.count()
        for j in jobs:
            total_time += j.get_duration()
        if job_count == 0:
            average_time = 0.0
        else:
            average_time = total_time/job_count
        return round(average_time, 2)

    def reporting_period(self):
        return str(self.start_date.strftime('%d/%m/%Y')) + "-" + str(self.end_date.strftime('%d/%m/%Y'))

    # TODO: good test: check that average time/per type == average time overall.

    # TODO: per task requested?!

# number of vehicles booked in on a monthly basis, overall and per service requested
# (MoT, annual service, repair, etc.), and type of customer (casual or account holder)
class VehicleReport(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    # month = models.IntegerField(default=timezone.now().month)
    date = models.DateTimeField(default=timezone.datetime.now)
    dropin_mot = models.PositiveIntegerField()
    dropin_annual = models.PositiveIntegerField()
    dropin_repair = models.PositiveIntegerField()
    account_holders_mot = models.PositiveIntegerField()
    account_holders_annual = models.PositiveIntegerField()
    account_holders_repair = models.PositiveIntegerField()

    def overall_mot(self):
        return self.dropin_mot + self.account_holders_mot

    def overall_annual(self):
        return self.dropin_annual + self.account_holders_annual

    def overall_repair(self):
        return self.dropin_repair + self.account_holders_repair

    def dropin_overall(self):
        return self.dropin_annual + self.dropin_repair + self.dropin_mot

    def account_holders_overall(self):
        return self.account_holders_annual + self.account_holders_repair + self.account_holders_mot

    def overall(self):
        return self.dropin_overall() + self.account_holders_overall()

    # TODO: calculate automatically amount of how many of each per view.


class ResponseRateReport(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    date = models.DateTimeField(default=timezone.datetime.now)
    # TODO: other (annual) reminders as well
    mot_reminders_sent = models.PositiveIntegerField()
    # annual_reminders_sent = models.PositiveIntegerField()
    mot_jobs = models.PositiveIntegerField()
    # annual_jobs = models.PositiveIntegerField()

    mot_response_rate = models.PositiveSmallIntegerField(null=True)
    # annual_response_rate = models.PositiveSmallIntegerField(null=True)

    def get_mot_response_rate(self):
        self.mot_response_rate = 100*self.mot_jobs/self.mot_reminders_sent
        return self.mot_response_rate


class MOTReminder(TimestampedModel, RandomUUIDModel, SoftDeleteModel):
    vehicle = models.ForeignKey(Vehicle)
    issue_date = models.DateTimeField(default=timezone.datetime.now)
    renewal_test_date = models.DateTimeField()

    def get_customer(self):
        return self.vehicle.customer

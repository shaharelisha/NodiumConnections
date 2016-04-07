import calendar
import datetime

from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldDoesNotExist
from django.utils import timezone

from nod.models import *

register = template.Library()


@register.filter(name="role")
def get_role(user):
    role_name = next(name for value, name in StaffMember.ROLES if value==user.staffmember.role)
    return role_name


@register.filter(name='address')
def get_full_address(customer):
    return customer.full_address()


@register.filter(name='phones')
def get_all_phones(customer):
    return customer.get_phones()


@register.filter(name='emails')
def get_all_email(customer):
    return customer.list_emails()


@register.filter(name='is_business')
def is_business(customer):
    if customer.__class__.__name__ == "BusinessCustomer":
        return True
    else:
        return False


@register.filter(name='job_tasks')
def get_tasks(invoice):
    return invoice.job_done.tasks.filter(is_deleted=False)


@register.filter(name='job_parts')
def get_job_parts(invoice):
    return invoice.job_done.parts.filter(is_deleted=False)


@register.filter(name="actual_job_part")
def actual_job_parts(part, job):
    return JobPart.objects.get(part=part, job=job, is_deleted=False)


@register.filter(name='parts_sold')
def get_parts_sold(invoice):
    return invoice.part_order.parts.filter(is_deleted=False)


@register.filter(name="actual_parts_sold")
def actual_parts_sold(part, order):
    return SellPart.objects.get(part=part, order=order, is_deleted=False)

# @register.filter(name='price')
# def get_markedup_price(part):
#     return part.get_markedup_price()


@register.filter(name='unit_price')
def get_unit_price(part):
    return part.get_markedup_price()


@register.filter(name='total_cost')
def get_cost(part):
    return part.get_cost()


@register.filter(name='labour_duration')
def get_duration(job):
    return job.get_duration()


@register.filter(name='labour_price')
def get_labour_price(job):
    return job.get_labour_price()


@register.filter(name='total')
def get_total_price(job):
    return job.get_price()


@register.filter(name='vat')
def get_vat(job):
    return job.get_vat()


@register.filter(name='grand_total')
def get_grand_total(job):
    return job.get_grand_total()


@register.filter(name='copy2')
def copy2_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='2'):
        return True
    else:
        return False


@register.filter(name='copy3')
def copy3_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='3'):
        return True
    else:
        return False


@register.filter(name='copy4')
def copy4_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='4'):
        return True
    else:
        return False


@register.filter(name='parts')
def get_parts(report):
    return report.parts.filter(is_deleted=False)


@register.filter(name="actual_parts")
def actual_parts_for_report(part, report):
    return SparePart.objects.get(part=part, report=report, is_deleted=False)


@register.filter(name='cost')
def get_stock_cost(part):
    return part.quantity * part.price


@register.filter(name='initial_cost')
def get_stock_cost(part):
    return part.initial_stock * part.part.price


@register.filter(name='total_initial_cost')
def get_total_initial_cost(report):
    return report.get_total_initial_cost()


@register.filter(name='total_stock_cost')
def get_total_initial_cost(report):
    return report.get_total_stock_cost()
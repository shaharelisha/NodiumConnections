import calendar
import datetime

from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldDoesNotExist
from django.utils import timezone

from nod.models import *

register = template.Library()


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

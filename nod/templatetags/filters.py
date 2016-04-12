from django import template

from nod.models import *

register = template.Library()


# returns role name (corresponding to role value) for user
@register.filter(name="role")
def get_role(user):
    role_name = next(name for value, name in StaffMember.ROLES if value == user.staffmember.role)
    return role_name


# returns customer's full address
@register.filter(name='address')
def get_full_address(customer):
    return customer.full_address()


# returns a customer's list of phones
@register.filter(name='phones')
def get_all_phones(customer):
    return customer.get_phones()


# returns a customer's list of emails
@register.filter(name='emails')
def get_all_email(customer):
    return customer.list_emails()


# returns whether or not a customer is of type BusinessCustomer
@register.filter(name='is_business')
def is_business(customer):
    if customer.__class__.__name__ == "BusinessCustomer":
        return True
    else:
        return False


# returns whether or not a customer has unpaid invoices
@register.filter(name='has_unpaid_invoices')
def has_unpaid_invoices(customer):
    if len(customer.get_unpaid_invoices()) > 0:
        return True
    else:
        return False


# returns the list of tasks assigned to a job (invoice)
@register.filter(name='job_tasks')
def get_tasks(invoice):
    return invoice.job_done.tasks.filter(is_deleted=False)


# returns a list of parts used in a job for an invoice
@register.filter(name='job_parts')
def get_job_parts(invoice):
    return invoice.job_done.parts.filter(is_deleted=False)


# returns the object of the association class JobParts assigned to the specified part and job
@register.filter(name="actual_job_part")
def actual_job_parts(part, job):
    return JobPart.objects.get(part=part, job=job, is_deleted=False)


# returns a list of parts sold to a customer for an invoice
@register.filter(name='parts_sold')
def get_parts_sold(invoice):
    return invoice.part_order.parts.filter(is_deleted=False)


# returns the objects of the association class SellPart assigned to the specified part and order
@register.filter(name="actual_parts_sold")
def actual_parts_sold(part, order):
    return SellPart.objects.get(part=part, order=order, is_deleted=False)


# returns marked up price for a given part
@register.filter(name='unit_price')
def get_unit_price(part):
    return part.get_markedup_price()


# returns the cost of a given part
@register.filter(name='total_cost')
def get_cost(part):
    return part.get_cost()


# returns duration of a given job
@register.filter(name='labour_duration')
def get_duration(job):
    return job.get_duration()


# returns the labour price of a given job
@register.filter(name='labour_price')
def get_labour_price(job):
    return job.get_labour_price()


# returns the total price of a given job
@register.filter(name='total')
def get_total_price(job):
    return job.get_price()


# returns the VAT value for a given job
@register.filter(name='vat')
def get_vat(job):
    return job.get_vat()


# returns the grand total for a given job (for an invoice)
@register.filter(name='grand_total')
def get_grand_total(invoice):
    return invoice.get_price()


# returns whether or not the first invoice reminder was generated
@register.filter(name='copy2')
def copy2_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='2'):
        return True
    else:
        return False


# returns whether or not the second invoice reminder was generated
@register.filter(name='copy3')
def copy3_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='3'):
        return True
    else:
        return False


# returns whether or not the third, and final, invoice reminder was generated
@register.filter(name='copy4')
def copy4_exists(invoice):
    if InvoiceReminder.objects.get(invoice=invoice, reminder_phase='4'):
        return True
    else:
        return False


# returns the discount type for a given invoice
@register.filter(name='get_discount')
def get_discount(invoice):
    return invoice.get_discount()


# returns the value of the discount for a given invoice, rounded to two decimal points
@register.filter(name='get_discount_value')
def get_discount_value(invoice):
    return round(invoice.discount_value(), 2)


# returns a list of parts for a given (spare parts) report
@register.filter(name='parts')
def get_parts(report):
    return report.parts.filter(is_deleted=False)


# returns the object of the association class between the specified part and job
@register.filter(name="actual_parts")
def actual_parts_for_report(part, report):
    return SparePart.objects.get(part=part, report=report, is_deleted=False)


# return the stock price for a given part by multiplying the quantity by unit price
@register.filter(name='cost')
def get_stock_cost(part):
    return part.quantity * part.price


# return the initial stock price for a given part by multiplying the initial stock quantity by the unit price
@register.filter(name='initial_cost')
def get_stock_cost(part):
    return part.initial_stock_level * part.part.price


# return the total initial cost for a given report (given time period)
@register.filter(name='total_initial_cost')
def get_total_initial_cost(report):
    return report.get_total_initial_cost()


# return total current stock cost for a given report (given time period)
@register.filter(name='total_stock_cost')
def get_total_stock_cost(report):
    return report.get_total_stock_cost()


# return the average job time for a given time report
@register.filter(name='average_time')
def get_average_time(report):
    return report.get_average_time()


# return the average time for mot jobs for a given time report
@register.filter(name='average_time_for_mot')
def get_average_time_for_mot(report):
    return report.get_average_time_for_mot()


# return the average time for repair jobs for a given time report
@register.filter(name='average_time_for_repair')
def get_average_time_for_repair(report):
    return report.get_average_time_for_repair()


# return the average time for annual jobs for a given time report
@register.filter(name='average_time_for_annual')
def get_average_time_for_annual(report):
    return report.get_average_time_for_annual()


# return the average time for all jobs per given mechanic for a given time report
@register.filter(name='average_time_per_mechanic')
def get_average_time_per_mechanic(report, mechanic):
        return report.get_average_time_per_mechanic(mechanic)


# return the average time for mot jobs per given mechanic for a given time report
@register.filter(name='average_time_for_mot_per_mechanic')
def get_average_time_for_mot_per_mechanic(report, mechanic):
    return report.get_average_time_for_mot_per_mechanic(mechanic)


# return the average time for repair jobs per given mechanic for a given time report
@register.filter(name='average_time_for_repair_per_mechanic')
def get_average_time_for_repair_per_mechanic(report, mechanic):
    return report.get_average_time_for_repair_per_mechanic(mechanic)


# return the average time for annual jobs per given mechanic for a given time report
@register.filter(name='average_time_for_annual_per_mechanic')
def get_average_time_for_annual_per_mechanic(report, mechanic):
    return report.get_average_time_for_annual_per_mechanic(mechanic)


# returns whether or not a customer owes money by seeing if they have any unpaid invoices
@register.filter(name='owes_money')
def owes_money(customer):
    if len(customer.get_unpaid_invoices()) > 0:
        return True
    else:
        return False


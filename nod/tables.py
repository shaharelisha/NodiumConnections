# class ParentTable(tables.Table):
#     name = tables.LinkColumn('parent_single', args=[A('uuid')], order_by="name", verbose_name='Name')
#     full_contact = tables.Column(verbose_name='Contact Information')
#     full_address = tables.Column(order_by=("address", "postcode"), verbose_name='Address')
#     count_homes = tables.Column(order_by="count_homes", verbose_name='Number of Care Homes')
#     count_service_locations = tables.Column(order_by="count_service_locations", verbose_name='Number of Service Locations')
#     website = tables.Column(order_by="website", verbose_name='Website')
#     comments = tables.Column(order_by="comments", orderable=False, verbose_name='Comments')

#     class Meta:
#         attrs = {"class": 'paleblue'}

import django_tables2 as tables
from django_tables2.utils import A
from .models import *


# TODO: highlight suspended customers
class AccountHolderTable(tables.Table):
    full_name = tables.LinkColumn('view-customer', args=[A('uuid')], order_by="surname", verbose_name="Name")
    get_emails = tables.Column(verbose_name="Emails", orderable=False)
    get_phones = tables.Column(verbose_name="Phones", orderable=False)
    full_address = tables.Column(verbose_name="Address", orderable=False)
    # discount_plan = tables.Column(verbose_name="Discount Plan")
    # suspended = tables.BooleanColumn(verbose_name="Suspended")

    # def render_source(self, value):
    #     if value == 'some_value':
    #         return mark_safe("<span class='highlight_this_row'>%s</span>" % (escape(value)))
    #     else:
    #         return value
    #
    class Meta:
        attrs = {"class": "table table-striped table-hover "}


# TODO: highlight suspended customers
class BusinessCustomerTable(tables.Table):
    company_name = tables.LinkColumn('view-customer', args=[A('uuid')], order_by="company_name",
                                     verbose_name="Company Name")
    rep = tables.Column(verbose_name="Representative")
    get_emails = tables.Column(verbose_name="Emails", orderable=False)
    get_phones = tables.Column(verbose_name="Phones", orderable=False)
    full_address = tables.Column(verbose_name="Address", orderable=False)
    # discount_plan = tables.Column(verbose_name="Discount Plan")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}

# class JobTable(tables.Table): # Not sure about this table...
# 	job.vehicle.make = tables.Column(verbose_name="Make")
# 	job.vehicle.model = tables.Column(verbose_name="Model")
# 	job.vehicle.reg_number = tables.Column(verbose_name="Registration Number")
# 	job.vehicle.customer = tables.Column(verbose_name="Owner")
# 	job.booking_date = tables.Column(verbose_name="Date Added")


class UserTable(tables.Table):
    full_name = tables.LinkColumn('edit-user', args=[A('uuid')], order_by="full_name",
                                     verbose_name="Name")
    user_name = tables.Column(verbose_name="Username", order_by="user_name")
    role = tables.Column(verbose_name="Role", order_by="role")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}


# TODO: highlight parts where quantities are below thresholds
class PartTable(tables.Table):
    name = tables.LinkColumn('edit-part', args=[A('uuid')], order_by="name",
                                     verbose_name="Name")
    code = tables.Column(verbose_name="Code", order_by="code")
    manufacturer = tables.Column(verbose_name="Manufacturer", order_by="manufacturer")
    vehicle_type = tables.Column(verbose_name="Vehicle Type", order_by="vehicle_type")
    years = tables.Column(verbose_name="Year(s)", order_by="years")
    price = tables.Column(verbose_name="Price (£)", order_by="price")
    quantity = tables.Column(verbose_name="Quantity", order_by="quantity")
    low_level_threshold = tables.Column(verbose_name="Low Level Threshold", order_by="low_level_threshold")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}


# TODO: highlight jobs which are pending, started, complete
class ActiveJobsTable(tables.Table):
    job_number = tables.LinkColumn('edit-job', args=[A('uuid')], order_by="job_number",
                                   verbose_name="Job")
    type = tables.Column(verbose_name="Type", order_by="type")
    bay = tables.Column(verbose_name="Bay", order_by="bay")
    vehicle = tables.Column(verbose_name="Vehicle", order_by="vehicle")
    get_customer = tables.Column(verbose_name="Customer", order_by="get_customer")
    # get_customer = tables.LinkColumn('edit-customer', args=[A('get_customer.uuid')], verbose_name="Customer", order_by="get_customer")
    booking_date = tables.Column(verbose_name="Booking Date", order_by="booking_date")
    mechanic = tables.Column(verbose_name="Mechanic", order_by="mechanic")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}


class VehicleTable(tables.Table):
    reg_number = tables.LinkColumn('edit-vehicle', args=[A('get_customer.uuid'), A('uuid')], order_by="reg_number",
                                   verbose_name="Registration No.")
    # reg_number = tables.Column(order_by="reg_number", verbose_name="Registration No.")
    make = tables.Column(verbose_name="Make", order_by="make")
    model = tables.Column(verbose_name="Model", order_by="model")
    type = tables.Column(verbose_name="Type", order_by="type")
    engine_serial = tables.Column(verbose_name="Engine Serial", order_by="engine_serial")
    chassis_number = tables.Column(verbose_name="Chassis Number", order_by="chassis_number")
    color = tables.Column(verbose_name="Colour", order_by="color")
    mot_base_date = tables.Column(verbose_name="MoT Base Date", order_by="mot_base_date")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}


class UnpaidInvoiceTable(tables.Table):
    invoice_number = tables.LinkColumn('view-invoice', args=[A('uuid')], order_by="invoice_number",
                                   verbose_name="Invoice No.")
    issue_date = tables.Column(verbose_name="Date Issued", order_by="issue_date")
    reminder_phase = tables.Column(verbose_name="Reminder Phase", order_by="reminder_phase")
    type = tables.Column(verbose_name="Type", order_by="type")

    class Meta:
        attrs = {"class": "table table-striped table-hover "}
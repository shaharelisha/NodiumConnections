import calendar

from django import forms
from django.forms.formsets import BaseFormSet
from collections import OrderedDict
from datetime import timedelta

from crispy_forms_foundation.forms import *
from crispy_forms_foundation.layout import *

from crispy_forms_foundation.forms import FoundationModelForm

from nod.models import *

class EmailForm(forms.Form):
    CONTACT_TYPE = [
        ('1', 'Work'),
        ('2', 'Home'),
        ('3', 'Other'),
    ]

    email_type = forms.ChoiceField(label="Email Type", required=False, choices=CONTACT_TYPE)
    email_address = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={'placeholder': "Email",'rows': '1'}))


class BaseEmailFormSet(BaseFormSet):
         def clean(self):
             """
             Adds validation to check that no two emails have the same type or address
             and that all emails have both a type and address.
             """
             if any(self.errors):
                 return

             # email_types = []
             email_addresses = []
             duplicates = False

             for form in self.forms:
                 if form.cleaned_data:
                     email_type = form.cleaned_data['email_type']
                     email_address = form.cleaned_data['email_address']

                     # Check that no two emails have the same address
                     if email_address and email_type:
                         if email_address in email_addresses:
                             duplicates = True
                         email_addresses.append(email_address)

                         # if email_type in email_types:
                         #     duplicates = True
                         # email_types.append(email_type)

                     if duplicates:
                         raise forms.ValidationError(
                             'This email already exists.',
                             code='duplicate_emails'
                         )

                     # Check that all emails have both a type and address
                     # if email_type and not email_address:
                     #     raise forms.ValidationError(
                     #         'All emails must have an address.',
                     #         code='missing_email_address'
                     #     )
                     elif email_address and not email_type:
                         raise forms.ValidationError(
                             'All emails must have a type.',
                             code='missing_email_atype'
                         )


class EmailFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(EmailFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        # self.label_class = 'col-lg-8'
        # self.field_class = 'col-lg-5'
        self.form_tag = False
        self.layout = Layout(
            'email_type',
            'email_address',
        )
        self.render_required_fields = True


class PhoneForm(forms.Form):
    CONTACT_TYPE = [
        ('1', 'Work'),
        ('2', 'Home'),
        ('3', 'Fax'),
        ('4', 'Other'),
    ]
    phone_type = forms.ChoiceField(label="Phone Type", required=False, choices=CONTACT_TYPE)
    phone_number = forms.CharField(label="Phone Number", required=False, widget=forms.TextInput(
        attrs={'placeholder': "Phone Number",'rows': '1'}))


class BasePhoneFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        if any(self.errors):
            return

        phone_numbers = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                phone_type = form.cleaned_data['phone_type']
                phone_number = form.cleaned_data['phone_number']

                # Check that no two phone numbers have the same number
                if phone_number and phone_type:
                    if phone_number in phone_numbers:
                        duplicates = True
                    phone_numbers.append(phone_number)

                if duplicates:
                    raise forms.ValidationError(
                        'This number already exists.',
                        code="duplicate_phone_numbers"
                    )

                elif phone_number and not phone_type:
                    raise forms.ValidationError(
                        "All phone numbers must have a type.",
                        code="missing_phone_type"
                    )



class PhoneFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PhoneFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        # self.label_class = 'col-lg-8'
        # self.field_class = 'col-lg-5'
        self.form_tag = False
        self.layout = Layout(
            'phone_type',
            'phone_number',
        )
        self.render_required_fields = True


# class BaseTrackerForm(FoundationModelForm):
#     def __init__(self, user=None, title=None, *args, **kwargs):
#         self.title = title
#         self.user = user
#
#         super(BaseTrackerForm, self).__init__(*args, **kwargs)
#
#         for field in self.fields.values():
#             field.widget.attrs['placeholder'] = field.label
#
#     def save(self, *args, **kwargs):
#         commit = kwargs.pop('commit', True)
#         instance = super(BaseTrackerForm, self).save(
#             commit=False, *args, **kwargs)
#
#         self.pre_save(instance)
#
#         if commit:
#             instance.save()
#
#         return instance
#
#     def pre_save(self, instance):
#         pass
#
#
# class JobForm(BaseTrackerForm):
#     class Meta:
#         model = Job
#         fields =


# class TaskForm(forms.Form):
#     task_name = forms.ModelChoiceField(queryset=Task.objects.filter(is_deleted=False))


class JobCreateTaskForm(forms.Form):
    task_name = forms.ModelChoiceField(queryset=Task.objects.filter(is_deleted=False), required=False,
                                       empty_label="Select Task")


class BaseJobTaskCreateForm(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two tasks are the same, and that each
        task object has a status and a duration.
        """

        if any(self.errors):
            return


class TaskCreateFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(TaskCreateFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        # self.label_class = 'col-lg-8'
        # self.field_class = 'col-lg-5'
        self.form_tag = False
        self.layout = Layout(
            'task_name',
        )
        self.render_required_fields = True


class JobTaskForm(forms.Form):
    task_name = forms.ModelChoiceField(queryset=Task.objects.filter(is_deleted=False), required=False,
                                       empty_label="Select Task")
    TASK_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending'),
    ]
    status = forms.ChoiceField(choices=TASK_STATUS, initial='3', required=False)
    duration = forms.DurationField(required=False)


class BaseJobTaskForm(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two tasks are the same, and that each
        task object has a status and a duration.
        """

        if any(self.errors):
            return

        task_names = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                task_name = form.cleaned_data['task_name']
                status = form.cleaned_data['status']
                duration = form.cleaned_data['duration']

                # Checks that no two task objects have the same name
                if task_name:
                    if task_name in task_names:
                        duplicates = True
                    task_names.append(task_name)

                if duplicates:
                    raise form.ValidationError(
                        'This task was already assigned.',
                        code='duplicate_tasks'
                    )

                # Check that all tasks have a status
                if task_name and not status:
                    raise forms.ValidationError(
                        'All tasks must have a status.',
                        code='missing_task_status'
                    )

                # Check that all tasks have a duration
                if task_name and not duration:
                    raise forms.ValidationError(
                        'All tasks must have a duration.',
                        code='missing_task_duration'
                    )


class TaskFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(TaskFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        # self.label_class = 'col-lg-8'
        # self.field_class = 'col-lg-5'
        self.form_tag = False
        self.layout = Layout(
            'task_name',
            'status',
            'duration'
        )
        self.render_required_fields = True


class JobPartForm(forms.Form):
    part_name = forms.ModelChoiceField(queryset=Part.objects.filter(is_deleted=False), required=False,
                                       empty_label="Select Part")
    quantity = forms.IntegerField(min_value=0, initial=1, required=False)


class BaseJobPartForm(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two parts are the same, and that each
        task object has a status and a duration.
        """

        if any(self.errors):
            return

        part_names = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                part_name = form.cleaned_data['part_name']
                quantity = form.cleaned_data['quantity']

                # Checks that no two task objects have the same name
                if part_name:
                    if part_name in part_names:
                        duplicates = True
                    part_names.append(part_name)

                if duplicates:
                    raise form.ValidationError(
                        'This part was already added.',
                        code='duplicate_parts'
                    )

                # Check that all parts have a quantity
                if part_name and not quantity:
                    raise forms.ValidationError(
                        'All parts must have a quantity.',
                        code='missing_part_quantity'
                    )


class PartFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PartFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        # self.label_class = 'col-lg-8'
        # self.field_class = 'col-lg-5'
        self.form_tag = False
        self.layout = Layout(
            'part_name',
            'quantity',
        )
        self.render_required_fields = True


class JobCreateForm(forms.Form):
    job_number = forms.IntegerField(min_value=0, widget=forms.TextInput(attrs={'readonly': True}))
    vehicle = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Vehicle Registration No.",'rows': '1', "id": "vehicles"}))
    JOB_TYPE = [
        ('1', 'MOT'),
        ('2', 'Repair'),
        ('3', 'Annual')
    ]
    type = forms.ChoiceField(choices=JOB_TYPE)

    # define today's date in order to autofill the 'booking date' attribute to today's date.
    today = timezone.now().date()
    booking_date = forms.DateField(label="Booking Date", input_formats=['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'], initial=today,
                                   widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))
    # mechanic = forms.ModelChoiceField(queryset=Mechanic.objects.filter(is_deleted=False))
    bay = forms.ModelChoiceField(queryset=Bay.objects.filter(is_deleted=False), empty_label="Select Bay")

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-5'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'job_number',
            'vehicle',
            'type',
            'booking_date',
            'bay',
        )
        super(JobCreateForm, self).__init__(*args, **kwargs)
        self.fields['job_number'].label = "Job Number"
        self.fields['vehicle'].label = "Vehicle Registration No."
        self.fields['type'].label = "Service Type"
        self.fields['booking_date'].label = "Booking Date"
        self.fields['bay'].label = "Bay"


class JobEditForm(forms.Form):
    job_number = forms.IntegerField(min_value=0, widget=forms.TextInput(attrs={'readonly': True}))
    vehicle = forms.CharField(max_length=300, widget=forms.TextInput(
        attrs={'placeholder': "Vehicle Registration No.",'rows': '1', 'readonly': True}))
    booking_date = forms.DateField(label="Booking Date", input_formats=['%d/%m/%Y', '%Y-%m-%d'],
                                   widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))
    work_carried_out = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={'placeholder': "Work Carried Out",'rows': '3'}))
    bay = forms.ModelChoiceField(queryset=Bay.objects.filter(is_deleted=False), empty_label="Select Bay")


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'job_number',
            'vehicle',
            'booking_date',
            'bay',
            'work_carried_out',
        )
        super(JobEditForm, self).__init__(*args, **kwargs)
        self.fields['job_number'].label = "Job Number"
        self.fields['bay'].label = "Bay"
        self.fields['vehicle'].label = "Vehicle"
        self.fields['booking_date'].label = "Booking Date"
        self.fields['work_carried_out'].label = "Work Carried Out"


class CustomerForm(forms.Form):
    customer_uuid = forms.CharField(widget=forms.HiddenInput())
    forename = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'placeholder': "Forename",'rows': '1'}))
    surname = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Surname",'rows': '1'}))

    # define today's date in order to autofill the 'joining date' attribute to today's date.
    today = timezone.now().date().strftime('%d/%m/%Y')
    date = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], initial=today,
                           widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))


class DropinForm(CustomerForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'forename',
            'surname',
            'date',
        )
        super(DropinForm, self).__init__(*args, **kwargs)
        self.fields['forename'].label = "Forename"
        self.fields['surname'].label = "Surname"
        self.fields['date'].label = "Date Arrived"


class AccountHolderForm(CustomerForm):
    address = forms.CharField(max_length=80, widget=forms.Textarea(
        attrs={'placeholder': "Address",'rows': '1'}))
    postcode = forms.CharField(max_length=8, widget=forms.TextInput(
        attrs={'placeholder': "Postcode",'rows': '1'}))
    discount_plan = forms.ModelChoiceField(queryset=DiscountPlan.objects.filter(is_deleted=False))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'forename',
            'surname',
            'date',
            'address',
            'postcode',
            'discount_plan',
        )
        super(AccountHolderForm, self).__init__(*args, **kwargs)
        self.fields['forename'].label = "Forename"
        self.fields['surname'].label = "Surname"
        self.fields['date'].label = "Date Joined"
        self.fields['address'].label = "Address"
        self.fields['postcode'].label = "Postcode"
        self.fields['discount_plan'].label = "Discount Plan"


class BusinessCustomerForm(CustomerForm):
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Company Name",'rows': '1'}))
    rep_role = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Representative Role", 'rows': '1'}))
    address = forms.CharField(max_length=80, widget=forms.Textarea(
        attrs={'placeholder': "Address",'rows': '1'}))
    postcode = forms.CharField(max_length=8, widget=forms.TextInput(
        attrs={'placeholder': "Postcode",'rows': '1'}))
    discount_plan = forms.ModelChoiceField(queryset=DiscountPlan.objects.filter(is_deleted=False))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'company_name',
            'date',
            'forename',
            'surname',
            'rep_role',
            'address',
            'postcode',
            'discount_plan',
        )
        super(BusinessCustomerForm, self).__init__(*args, **kwargs)
        self.fields['forename'].label = "Representative Forename"
        self.fields['surname'].label = "Representative Surname"
        self.fields['date'].label = "Date Joined"
        self.fields['address'].label = "Address"
        self.fields['postcode'].label = "Postcode"
        self.fields['discount_plan'].label = "Discount Plan"
        self.fields['company_name'].label = "Company Name"
        self.fields['rep_role'].label = "Representative Role"
        self.fields['discount_plan'].label = "Discount Plan"


class VehicleForm(forms.Form):
    reg_number = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Registration No.",'rows': '1'}))
    make = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Make",'rows': '1'}))
    model = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Model",'rows': '1'}))
    engine_serial = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Engine Serial",'rows': '1'}))
    chassis_number = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Chassis No.",'rows': '1'}))
    color = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Colour",'rows': '1'}))
    mot_base_date = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], required=False,
                                    widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))

    VEHICLE_TYPE = (
        ('1', 'Van/Light Vehicle'),
        ('2', 'Car'),
    )
    type = forms.ChoiceField(choices=VEHICLE_TYPE, initial='2')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'reg_number',
            'make',
            'model',
            'engine_serial',
            'chassis_number',
            'color',
            'mot_base_date',
            'type',
        )
        super(VehicleForm, self).__init__(*args, **kwargs)
        self.fields['reg_number'].label = "Registration Number"
        self.fields['make'].label = "Make"
        self.fields['model'].label = "Model"
        self.fields['engine_serial'].label = "Engine Serial"
        self.fields['chassis_number'].label = "Chassis Number"
        self.fields['color'].label = "Colour"
        self.fields['mot_base_date'].label = "MoT Base Date"
        self.fields['type'].label = "Type"


class PartForm(forms.Form):
    low_level_threshold = forms.IntegerField(min_value=0, initial=10)
    price = forms.FloatField(min_value=0)
    quantity = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'quantity',
            'price',
            'low_level_threshold',
        )
        super(PartForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].label = "Quantity"
        self.fields['price'].label = "Price (£)"
        self.fields['low_level_threshold'].label = "Low Level Threshold"


class ReplenishmentOrderForm(forms.Form):
    today = timezone.now().date()
    date = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'], initial=today,
                           widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Supplier Company Name",'rows': '1', "id": 'suppliers'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'company_name',
            'date',
        )
        super(ReplenishmentOrderForm, self).__init__(*args, **kwargs)
        self.fields['company_name'].label = "Supplier Name"
        self.fields['date'].label = "Date"


class SupplierForm(forms.Form):
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': "Company Name",'rows': '1'}))
    address = forms.CharField(max_length=80, widget=forms.Textarea(
        attrs={'placeholder': "Address",'rows': '1'}))
    postcode = forms.CharField(max_length=8, widget=forms.TextInput(
        attrs={'placeholder': "Postcode",'rows': '1'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'company_name',
            'address',
            'postcode',
        )
        super(SupplierForm, self).__init__(*args, **kwargs)
        self.fields['address'].label = "Address"
        self.fields['postcode'].label = "Postcode"
        self.fields['company_name'].label = "Company Name"


class PaymentForm(forms.Form):
    amount = forms.FloatField(min_value=0)
    PAYMENT_TYPES = (
        ('1', 'Cash'),
        ('2', 'Card'),
        ('3', 'Cheque'),
    )
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPES)
    today = timezone.now().date()
    date = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'], initial=today,
                           widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))
    last_4_digits = forms.IntegerField(min_value=0, max_value=9999, required=False)
    cvv = forms.IntegerField(min_value=0, required=False, max_value=999)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'amount',
            'date',
            'payment_type',
            'last_4_digits',
            'cvv',
        )
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['amount'].label = "Amount (£)"
        self.fields['payment_type'].label = "Payment Type"
        self.fields['date'].label = "Date"
        self.fields['last_4_digits'].label = "Last 4 Digits"
        self.fields['cvv'].label = "CVV"


class ProfileForm(forms.Form):
    user_name = forms.CharField(max_length=40, required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'user_name',
        )
        super(ProfileForm, self).__init__(*args, **kwargs)
        # self.fields['forename'].label = "Forename"
        # self.fields['surname'].label = "Surname"
        self.fields['user_name'].label = "Username"


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': ("Your old password was entered incorrectly. "
                               "Please enter it again."),
    })
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password) and old_password != "":
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-8'
        # self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
        )
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = "Old Password"
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "New Password Confirmation"


PasswordChangeForm.base_fields = OrderedDict(
    (k, PasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
)

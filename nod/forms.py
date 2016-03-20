from django import forms
from django.forms.formsets import BaseFormSet
# from collections import OrderedDict
# from datetime import timedelta

from crispy_forms_foundation.forms import *
from crispy_forms_foundation.layout import *

from crispy_forms_foundation.forms import FoundationModelForm

from nod.models import *

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

class TaskForm(forms.Form):
    task_name = forms.ModelChoiceField(queryset=Task.objects.filter(is_deleted=False))


class JobTaskForm(forms.Form):
    task_name = forms.ModelChoiceField(queryset=Task.objects.filter(is_deleted=False))
    TASK_STATUS = [
        ('1', 'Complete'),
        ('2', 'Started'),
        ('3', 'Pending'),
    ]
    status = forms.ChoiceField(choices=TASK_STATUS, initial='3')
    duration = forms.DurationField()


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


class JobPartForm(forms.Form):
    part_name = forms.ModelChoiceField(queryset=Part.objects.filter(is_deleted=False))
    quantity = forms.IntegerField(min_value=0, initial=1)


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


class JobCreateForm(forms.Form):
    # tasks = forms.ModelMultipleChoiceField(queryset=Task.objects.filter(is_deleted=False),
    #                                        widget=forms.CheckboxSelectMultiple)
    # parts = forms.ModelMultipleChoiceField(queryset=Part.objects.filter(is_deleted=False),
    #                                        widget=forms.CheckboxSelectMultiple)
    job_number = forms.IntegerField(min_value=0)
    vehicle = forms.CharField(max_length=300, widget=forms.Textarea(
        attrs={'placeholder': "Vehicle Registration No.",'rows': '1'}))
    booking_date = forms.DateField(label="Booking Date", input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=forms.DateInput())
    mechanic = forms.ModelChoiceField(queryset=Mechanic.objects.filter(is_deleted=False))

    def __init__(self, *args, *kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'job_number',
            'vehicle',
            'booking_date',
            'mechanic',
        )
        super(JobCreateForm, self).__init__(*args, **kwargs)
        self.field['job_number'].label = "Job Number"
        self.field['vehicle'].label = "Vehicle Registration No."
        self.field['booking_date'].label = "Booking Date"
        self.field['mechanic'].label = "Mechanic"


class JobEditForm(forms.Form):
    # tasks = forms.ModelMultipleChoiceField(queryset=Task.objects.filter(is_deleted=False),
    #                                        widget=forms.CheckboxSelectMultiple)
    # parts = forms.ModelMultipleChoiceField(queryset=Part.objects.filter(is_deleted=False),
    #                                        widget=forms.CheckboxSelectMultiple)
    job_number = forms.IntegerField(min_value=0)
    vehicle = forms.CharField(max_length=300, widget=forms.Textarea(
        attrs={'placeholder': "Vehicle Registration No.",'rows': '1'}))
    booking_date = forms.DateField(label="Booking Date", input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=forms.DateInput())
    mechanic = forms.ModelChoiceField(queryset=Mechanic.objects.filter(is_deleted=False))
    work_carried_out = forms.CharField(max_length=1000, widget=forms.Textarea(
        attrs={'placeholder': "Work Carried Out",'rows': '1'}))

    def __init__(self, *args, *kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'job_number',
            'vehicle',
            'booking_date',
            'mechanic',
            'work_carried_out',
        )
        super(JobCreateForm, self).__init__(*args, **kwargs)
        self.field['job_number'].label = "Job Number"
        self.field['vehicle'].label = "Vehicle"
        self.field['booking_date'].label = "Booking Date"
        self.field['mechanic'].label = "Mechanic"
        self.field['work_carried_out'].label = "Work Carried Out"
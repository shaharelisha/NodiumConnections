from django.http import HttpResponse
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction
from django.contrib import messages
from django_tables2 import RequestConfig
from django.forms.formsets import formset_factory
from django.contrib.auth import update_session_auth_hash
import json
from django.template import RequestContext, loader

# london_tz = pytz.timezone("Europe/London")

from .forms import *
from .models import *


def index(request):
    return render(request, "nod/base.html")

# @login_required
def create_job(request):
    TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm)
    tasks_data = []

    PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
    parts_data = []

    task_helper = TaskFormSetHelper()
    part_helper = PartFormSetHelper()
    print("a")

    if request.method == 'POST':
        print("b")
        form = JobCreateForm(request.POST)
        task_formset = TaskFormSet(request.POST, prefix='fs1')
        part_formset = PartFormSet(request.POST, prefix='fs2')

        if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
            print("c")
            job_number = form.cleaned_data['job_number']
            vehicle = form.cleaned_data['vehicle']
            booking_date = form.cleaned_data['booking_date']
            bay = form.cleaned_data['bay']


            vehicle = get_object_or_404(Vehicle, reg_number=vehicle)
            # bay = get_object_or_404(Bay, bay_type=bay)
            job = Job.objects.create(job_number=job_number, vehicle=vehicle, status='3', booking_date=booking_date,
                                     bay=bay)
            # job.job_number = job.id?
            try:
                with transaction.atomic():
                    for task_form in task_formset:
                        task_name = task_form.cleaned_data['task_name']
                        # status = task_form.cleaned_data['status']
                        # duration = task_form.cleaned_data['duration']

                        if task_name:
                            task = get_object_or_404(Task, description=task_name)
                            jobtask = JobTask.objects.create(task=task, job=job, status='3')
                            jobtask.duration = task.estimated_time
                            jobtask.save()


                    for part_form in part_formset:
                        part_name = part_form.cleaned_data['part_name']
                        quantity = part_form.cleaned_data['quantity']

                        if part_name and quantity:
                            part = get_object_or_404(Part, name=part_name)

                            # checks that the quantity required is not more than the total quantity in stock.
                            # if it is, it removes the quantity used for a job from the total quantity and,
                            # creates a job part object, otherwise, it throws an error.
                            if part.quantity >= quantity:
                                part.quantity -= quantity
                                JobPart.objects.create(part=part, job=job, quantity=quantity)

                            else:
                                raise forms.ValidationError(
                                    'Not enough parts in stock.',
                                    code='insufficient_parts'
                                )

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        print("d")
        data = {}

        form = JobCreateForm(initial=data)
        task_formset = TaskFormSet(initial=tasks_data, prefix='fs1')
        part_formset = PartFormSet(initial=parts_data, prefix='fs2')

    context = {
        'form': form,
        'task_formset': task_formset,
        'part_formset': part_formset,
        'task_helper': task_helper,
        'part_helper': part_helper,
    }

    return render(request, 'nod/create_jobsheet.html', context)


# @login_required
def edit_job(request, uuid):
    job = get_object_or_404(Job, uuid=uuid)

    TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm, extra=0)
    task_set = job.jobtask_set.all()
    tasks_data = [{'task_name': t.task, 'status': t.status, 'duration': t.duration}
                  for t in task_set]

    PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm, extra=0)
    part_set = job.jobpart_set.all()
    parts_data = [{'part_name': p.part, 'quantity': p.quantity}
                  for p in part_set]

    task_helper = TaskFormSetHelper()
    part_helper = PartFormSetHelper()

    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        task_formset = TaskFormSet(request.POST, prefix='fs1')
        part_formset = PartFormSet(request.POST, prefix='fs2')

        if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
            # job_number = form.cleaned_data['job_number']
            vehicle = form.cleaned_data['vehicle']
            booking_date = form.cleaned_data['booking_date']
            bay = form.cleaned_data['bay']


            vehicle = get_object_or_404(Vehicle, reg_number=vehicle)
            # bay = get_object_or_404(Bay, bay_type=bay)
            job.booking_date = booking_date
            job.bay = bay
            # job.job_number = job.id?
            try:
                with transaction.atomic():
                    for task_form in task_formset:
                        task_name = task_form.cleaned_data.get('task_name')
                        status = task_form.cleaned_data.get('status')
                        duration = task_form.cleaned_data.get('duration')

                        if task_name:
                            task = get_object_or_404(Task, description=task_name)
                            # jobtask = JobTask.objects.get_or_create(task=task, job=job, is_deleted=False)
                            jobtask = job.jobtask_set.filter(task=task, is_deleted=False)

                            # get_or_create returns tuple {object returned, whether it was created or just retrieved}
                            # jobtask = jobtask[0]
                            if status:
                                jobtask.status = status
                            else:
                                jobtask.status = '3'
                            if duration:
                                jobtask.duration = duration
                            else:
                                jobtask.duration = task.estimated_time
                            jobtask.save()

                    for part_form in part_formset:
                        part_name = part_form.cleaned_data.get('part_name')
                        quantity = part_form.cleaned_data.get('quantity')

                        if part_name and quantity:
                            part = get_object_or_404(Part, name=part_name)
                            # jobpart = JobPart.objects.get_or_create(part=part, job=job, is_deleted=False)
                            jobpart = job.jobpart_set.filter(part=part, is_deleted=False)

                            # jobpart = jobpart[0]

                            # checks that the quantity required is not more than the total quantity in stock.
                            # if it is, it removes the quantity used for a job from the total quantity and assigns,
                            # the quantity to the job part object, otherwise, it throws an error.
                            if part.quantity >= quantity:
                                part.quantity -= quantity
                                jobpart.quantity = quantity
                            else:
                                raise forms.ValidationError(
                                    'Not enough parts in stock.',
                                    code='insufficient_parts'
                                )
                            jobpart.save()

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        data = {}
        data['job_number'] = job.job_number
        data['vehicle'] = job.vehicle.reg_number
        data['type'] = job.type
        data['bay'] = job.bay
        data['status'] = job.status
        data['booking_date'] = job.booking_date
        data['work_carried_out'] = job.work_carried_out
        data['mechanic'] = job.mechanic

        form = JobCreateForm(initial=data)
        task_formset = TaskFormSet(initial=tasks_data, prefix='fs1')
        part_formset = PartFormSet(initial=parts_data, prefix='fs2')

    context = {
        'form': form,
        'task_formset': task_formset,
        'part_formset': part_formset,
        'task_helper': task_helper,
        'part_helper': part_helper,
        'job': job,
    }

    return render(request, 'nod/edit_jobsheet.html', context)
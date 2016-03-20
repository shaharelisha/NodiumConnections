from django.http import HttpResponse
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction
from django.contrib import messages

# london_tz = pytz.timezone("Europe/London")

from nod.forms import *
from nod.models import *


def index(request):
    return render(request, "nod/base.html")

@login_required
def create_job(request):
    TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm)
    tasks_data = []

    PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
    parts_data = []

    if request.POST == 'POST':
        form = JobCreateForm(request.POST)
        task_formset = TaskFormSet(request.POST, prefix='fs1')
        part_formset = PartFormSet(request.POST, prefix='fs2')

        if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
            job_number = form.cleaned_data['job_number']
            vehicle = form.cleaned_data['vehicle']
            booking_date = form.cleaned_data['booking_date']
            mechanic = form.cleaned_data['mechanic']


            vehicle = get_object_or_404(Vehicle, reg_number=vehicle)

            # TODO: split mechanic name into two parts
            mechanic = get_object_or_404(Mechanic, first_name=mechanic, last_name=mechanic)
            job = Job.objects.create(job_number=job_number, vehicle=vehicle, status='3', booking_date=booking_date,
                                     mechanic=mechanic)
            # job.job_number = job.id?
            try:
                with transaction.atomic():
                    for task_form in task_formset:
                        task_name = task_form.cleaned_data['task_name']
                        # status = task_form.cleaned_data['status']
                        # duration = task_form.cleaned_data['duration']

                        if task_name:
                            task = get_object_or_404(Task, description=task_name)
                            job = JobTask.objects.create(task=task, job=job, status='3')
                            job.duration = task.estimated_time
                            job.save()


                    for part_form in part_formset:
                        part_name = part_form.cleaned_data['part_name']
                        quantity = part_form.cleaned_data['quantity']

                        if part_name and quantity:
                            part = get_object_or_404(Part, name=part_name)
                            JobPart.objects.create(part=part, job=job, quantity=quantity)

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        data = {}

        form = JobCreateForm(initial=data)
        task_formset = TaskFormSet(initial=tasks_data, prefix='fs1')
        part_formset = PartFormSet(initial=parts_data, prefix='fs2')

    context = {
        'form': form,
        'task_formset': task_formset,
        'part_formset': part_formset
    }

    return render(request, 'nod/create_jobsheet.html', context)
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
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
import json
from django.template import RequestContext, loader
from django.contrib.auth import logout
import datetime
from dateutil.relativedelta import relativedelta

# london_tz = pytz.timezone("Europe/London")

from .forms import *
from nod.models import *
from .tables import *


def index(request):
    # Mechanic
    if request.user.staffmember.role == '1':
        uuid = request.user.staffmember.uuid
        my_jobs_table = MyJobsTable(Job.objects.filter(is_deleted=False, mechanic__uuid=uuid))
        RequestConfig(request).configure(my_jobs_table)
        return render(request, "nod/index-mechanic.html", {'my_jobs_table': my_jobs_table})
        # return render(request, "nod/index-mechanic.html")
    # Foreperson
    if request.user.staffmember.role == '2':
        automated_invoice_checks()
        return render(request, "nod/index-foreperson.html")
    # Franchisee
    if request.user.staffmember.role == '3':
        automated_invoice_checks()
        return render(request, "nod/index-franchisee.html")
    # Receptionist
    if request.user.staffmember.role == '4':
        automated_invoice_checks()
        return render(request, "nod/index-receptionist.html")
    # Admin
    if request.user.staffmember.role == '5':
        return render(request, "nod/index-administrator.html")
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('/accounts/login/')


def automated_invoice_checks():
    for c in AccountHolder.objects.filter(is_deleted=False):
        for invoice in c.get_unpaid_invoices():
            if invoice.issue_date <= datetime.date.today() - relativedelta(month=1):
                InvoiceReminder.objects.create(invoice=invoice, reminder_phase='2')
                invoice.reminder_phase = '2'
                invoice.save()
            if invoice.issue_date <= datetime.date.today() - relativedelta(month=2):
                InvoiceReminder.objects.create(invoice=invoice, reminder_phase='3')
                invoice.reminder_phase = '3'
                invoice.save()
            if invoice.issue_date <= datetime.date.today() - relativedelta(month=3):
                InvoiceReminder.objects.create(invoice=invoice, reminder_phase='4')
                invoice.reminder_phase = '4'
                invoice.save()
    return None


@login_required
def logout_view(request):
    logout(request)
    return render(request, 'registration/login.html')


@login_required
def user_table(request):
    if request.user.staffmember.role == '5':
        user_table = UserTable(StaffMember.objects.filter(is_deleted=False))
        RequestConfig(request).configure(user_table)
        return render(request, "nod/users.html", {'user_table': user_table})
    else:
        messages.error(request, "You must be Admin in order to view this page.")
        return redirect('/garits/')


@login_required
def part_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' \
            or request.user.staffmember.role == '2':
        part_table = PartTable(Part.objects.filter(is_deleted=False))
        RequestConfig(request).configure(part_table)
        return render(request, "nod/parts.html", {'part_table': part_table})
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def active_jobs_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4'\
            or request.user.staffmember.role == '2':
        job_table = ActiveJobsTable(Job.objects.filter(is_deleted=False, status='2'))
        RequestConfig(request).configure(job_table)
        return render(request, "nod/jobs.html", {'job_table': job_table})
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def untaken_jobs_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '1' or\
                    request.user.staffmember.role == '2' or request.user.staffmember.role == '4':
        untaken_job_table = UntakenJobsTable(Job.objects.filter(is_deleted=False, mechanic=None))
        RequestConfig(request).configure(untaken_job_table)
        return render(request, "nod/untaken_jobs.html", {'untaken_job_table': untaken_job_table})
    else:
        messages.error(request, "You must be a franchisee/mechanic/foreperson/receptionist in order to view this page.")
        return redirect('/garits/')


# @login_required
# def my_jobs_table(request):
#     if request.user.staffmember.role == '1' or request.user.staffmember.role == '2':
#         uuid = request.user.staffmember.uuid
#         my_jobs_table = UntakenJobsTable(Job.objects.filter(is_deleted=False, mechanic__uuid=uuid))
#         RequestConfig(request).configure(my_jobs_table)
#         return render(request, "nod/index-mechanic.html", {'my_jobs_table': my_jobs_table})
#     else:
#         messages.error(request, "You must be a mechanic/foreperson in order to view this page.")
#         return redirect('/garits/')


@login_required
def supplier_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4'\
            or request.user.staffmember.role == '2':
        supplier_table = SupplierTable(Supplier.objects.filter(is_deleted=False))
        RequestConfig(request).configure(supplier_table)
        return render(request, "nod/suppliers.html", {'supplier_table': supplier_table})
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def account_holder_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4'\
            or request.user.staffmember.role == '2':
        account_holders_table = AccountHolderTable(AccountHolder.objects.filter(is_deleted=False,
                                                                                businesscustomer=None).exclude(forename="",
                                                                                                          surname=""))
        RequestConfig(request).configure(account_holders_table)

        # deletes account holders which were created (automatically when accessing the 'create' page)
        # but then weren't submitted (left empty) for over 30 mintutes.
        for a in Customer.objects.filter(forename="", surname=""):
            if a.updated < timezone.now() - timedelta(minutes=30):
                for v in a.vehicle_set.all():
                    v.delete()
                a.delete()

        context = {
            'account_holders_table': account_holders_table,
        }
        return render(request, "nod/account_holders.html", context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def business_customers_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4'\
            or request.user.staffmember.role == '2':
        business_customers_table = BusinessCustomerTable(BusinessCustomer.objects.filter(is_deleted=False).exclude(company_name=""))
        RequestConfig(request).configure(business_customers_table)

        # deletes business customers which were created (automatically when accessing the 'create' page)
        # but then weren't submitted (left empty) for over 30 mintutes.
        for b in BusinessCustomer.objects.filter(company_name=""):
            if b.updated < timezone.now() - timedelta(minutes=30):
                for v in b.vehicle_set.all():
                    v.delete()
                b.delete()

        context = {
            'business_customers_table': business_customers_table,
        }
        return render(request, "nod/business_customers.html", context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def create_job(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4'\
            or request.user.staffmember.role == '2':
        TaskCreateFormSet = formset_factory(JobCreateTaskForm, formset=BaseJobTaskCreateForm)
        tasks_data = []

        # PartCreateFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
        # parts_data = []

        task_helper = TaskFormSetHelper()
        # part_helper = PartFormSetHelper()

        if request.method == 'POST':
            print("b")
            form = JobCreateForm(request.POST)
            task_formset = TaskCreateFormSet(request.POST, prefix='fs1')
            # part_formset = PartCreateFormSet(request.POST, prefix='fs2')

            if form.is_valid() and task_formset.is_valid():
                    # and part_formset.is_valid():

                job_number = form.cleaned_data['job_number']
                vehicle = form.cleaned_data['vehicle']
                booking_date = form.cleaned_data['booking_date']
                bay = form.cleaned_data['bay']


                vehicle = get_object_or_404(Vehicle, reg_number=vehicle)
                # bay = get_object_or_404(Bay, bay_type=bay)
                try:
                    with transaction.atomic():
                        job = Job.objects.create(job_number=job_number, vehicle=vehicle, status='3', booking_date=booking_date,
                                         bay=bay)
                # job.job_number = job.id?

                        for task_form in task_formset:
                            task_name = task_form.cleaned_data['task_name']

                            if task_name:
                                task = get_object_or_404(Task, description=task_name)
                                jobtask = JobTask.objects.create(task=task, job=job, status='3')
                                jobtask.duration = task.estimated_time
                                jobtask.save()


                        # for part_form in part_formset:
                        #     part_name = part_form.cleaned_data['part_name']
                        #     quantity = part_form.cleaned_data['quantity']
                        #
                        #     if part_name and quantity:
                        #         part = get_object_or_404(Part, name=part_name)
                        #
                        #         # checks that the quantity required is not more than the total quantity in stock.
                        #         # if it is, it removes the quantity used for a job from the total quantity and,
                        #         # creates a job part object, otherwise, it throws an error.
                        #         # TODO: do something to warn if drops below threshold
                        #         if part.quantity >= quantity:
                        #             part.quantity -= quantity
                        #             JobPart.objects.create(part=part, job=job, quantity=quantity)
                        #
                        #         else:
                        #             raise forms.ValidationError(
                        #                 'Not enough parts in stock.',
                        #                 code='insufficient_parts'
                        #             )

                        messages.success(request, "Job No." + job.reg_num + " was successfully created.")
                        return HttpResponseRedirect('/garits/jobs/pending/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            data = {}
            last_id = Job.objects.last().id
            new_id = last_id + 1
            data['job_number'] = new_id
            form = JobCreateForm(initial=data)
            task_formset = TaskCreateFormSet(initial=tasks_data, prefix='fs1')
            # part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')

        context = {
            'form': form,
            'task_formset': task_formset,
            # 'part_formset': part_formset,
            'task_helper': task_helper,
            # 'part_helper': part_helper,
        }

        return render(request, 'nod/create_jobsheet.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_job(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '1' or \
                    request.user.staffmember.role == '4':
        job = get_object_or_404(Job, uuid=uuid)

        TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm, min_num=1, extra=0)
        task_set = job.jobtask_set.all()
        tasks_data = [{'task_name': t.task, 'status': t.status, 'duration': t.duration}
                      for t in task_set]

        PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm, min_num=1, extra=0)
        part_set = job.jobpart_set.all()
        parts_data = [{'part_name': p.part, 'quantity': p.quantity}
                      for p in part_set]

        task_helper = TaskFormSetHelper()
        part_helper = PartFormSetHelper()

        if request.method == 'POST':
            form = JobEditForm(request.POST)
            task_formset = TaskFormSet(request.POST, prefix='fs1')
            part_formset = PartFormSet(request.POST, prefix='fs2')

            if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
                # job_number = form.cleaned_data['job_number']
                vehicle = form.cleaned_data['vehicle']
                booking_date = form.cleaned_data['booking_date']
                bay = form.cleaned_data['bay']


                vehicle = get_object_or_404(Vehicle, reg_number=vehicle)
                # bay = get_object_or_404(Bay, bay_type=bay)

                # job.job_number = job.id?
                try:
                    with transaction.atomic():
                        job.booking_date = booking_date
                        job.bay = bay

                        old_jobtasks = job.jobtask_set.all()
                        for jt in old_jobtasks:
                            jt.is_deleted = True
                            jt.save()

                        for task_form in task_formset:
                            task_name = task_form.cleaned_data.get('task_name')
                            status = task_form.cleaned_data.get('status')
                            duration = task_form.cleaned_data.get('duration')

                            if task_name:
                                task = get_object_or_404(Task, description=task_name)
                                # jobtask = JobTask.objects.get_or_create(task=task, job=job, is_deleted=False)
                                jobtask = job.jobtask_set.get_or_create(task=task)

                                # get_or_create returns tuple {object returned, whether it was created or just retrieved}
                                if jobtask[0].is_deleted is True:
                                    jobtask[0].is_deleted = False
                                    jobtask[0].save()
                                if jobtask[1] is True:
                                    job.jobtask_set.add(jobtask[0])

                                jobtask = jobtask[0]
                                if status:
                                    jobtask.status = status
                                else:
                                    jobtask.status = '3'
                                if duration:
                                    jobtask.duration = duration
                                else:
                                    jobtask.duration = task.estimated_time
                                jobtask.save()

                        old_jobparts = job.jobpart_set.all()
                        for jp in old_jobparts:
                            jp.is_deleted = True
                            jp.save()

                        for part_form in part_formset:
                            part_name = part_form.cleaned_data.get('part_name')
                            quantity = part_form.cleaned_data.get('quantity')

                            if part_name and quantity:
                                part = get_object_or_404(Part, name=part_name)
                                # jobpart = JobPart.objects.get_or_create(part=part, job=job, is_deleted=False)
                                jobpart = job.jobpart_set.get_or_create(part=part, quantity=quantity)

                                if jobpart[0].is_deleted is True:
                                    jobpart[0].is_deleted = False
                                    jobpart[0].save()
                                if jobpart[1] is True:
                                    job.jobpart_set.add(jobpart[0])

                                # jobpart[0].quantity = quantity


                                # checks that the quantity required is not more than the total quantity in stock.
                                # if it is, it removes the quantity used for a job from the total quantity and assigns,
                                # the quantity to the job part object, otherwise, it throws an error.
                                # TODO: do something if q drops below threshold
                                if part.quantity >= quantity:
                                    part.quantity -= quantity
                                    part.save()
                                else:
                                    # TODO: when changed back to TRUE, must subtract ^
                                    jobpart[0].sufficient_quantity = False
                                    # raise forms.ValidationError(
                                    #     'Not enough parts in stock.',
                                    #     code='insufficient_parts'
                                    # )
                                    jobpart[0].save()

                        for t in job.jobtask_set.filter(is_deleted=False):
                            if t.status == '1':
                                complete = True
                                job.status = '1'
                            else:
                                complete = False
                                break


                        if complete is False:
                            for t in job.jobtask_set.filter(is_deleted=False):
                                if t.status == '2':
                                    job.status = '2'
                                    break
                                else:
                                    job.status = '3'

                        job.save()
                        if complete is True:
                            last_id = Invoice.objects.last().id
                            new_id = last_id + 1
                            invoice = Invoice.objects.create(job_done=job, invoice_number=new_id, issue_date=datetime.date.today())

                        messages.success(request, "Your changes to Job No." + str(job.job_number) + " were saved.")
                        return HttpResponseRedirect('/garits/jobs/pending/')

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

            form = JobEditForm(initial=data)
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
    else:
        if request.user.staffmember.role == '2':
            job = get_object_or_404(Job, uuid=uuid)

            TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm, min_num=1, extra=0)
            task_set = job.jobtask_set.all()
            tasks_data = [{'task_name': t.task, 'status': t.status, 'duration': t.duration}
                          for t in task_set]

            PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm, min_num=1, extra=0)
            part_set = job.jobpart_set.all()
            parts_data = [{'part_name': p.part, 'quantity': p.quantity}
                          for p in part_set]

            task_helper = TaskFormSetHelper()
            part_helper = PartFormSetHelper()

            if request.method == 'POST':
                form = JobEditForm(request.POST)
                mechanic_form = MechanicJobForm(request.POST)
                task_formset = TaskFormSet(request.POST, prefix='fs1')
                part_formset = PartFormSet(request.POST, prefix='fs2')

                if form.is_valid() and task_formset.is_valid() and part_formset.is_valid() and mechanic_form.is_valid():
                    # job_number = form.cleaned_data['job_number']
                    vehicle = form.cleaned_data['vehicle']
                    booking_date = form.cleaned_data['booking_date']
                    bay = form.cleaned_data['bay']
                    mechanic = mechanic_form.cleaned_data['mechanic']

                    vehicle = get_object_or_404(Vehicle, reg_number=vehicle)

                    # bay = get_object_or_404(Bay, bay_type=bay)

                    # job.job_number = job.id?
                    try:
                        with transaction.atomic():
                            job.booking_date = booking_date
                            job.bay = bay
                            job.mechanic = mechanic

                            old_jobtasks = job.jobtask_set.all()
                            for jt in old_jobtasks:
                                jt.is_deleted = True
                                jt.save()

                            for task_form in task_formset:
                                task_name = task_form.cleaned_data.get('task_name')
                                status = task_form.cleaned_data.get('status')
                                duration = task_form.cleaned_data.get('duration')

                                if task_name:
                                    task = get_object_or_404(Task, description=task_name)
                                    # jobtask = JobTask.objects.get_or_create(task=task, job=job, is_deleted=False)
                                    jobtask = job.jobtask_set.get_or_create(task=task)

                                    # get_or_create returns tuple {object returned, whether it was created or just retrieved}
                                    if jobtask[0].is_deleted is True:
                                        jobtask[0].is_deleted = False
                                        jobtask[0].save()
                                    if jobtask[1] is True:
                                        job.jobtask_set.add(jobtask[0])

                                    jobtask = jobtask[0]
                                    if status:
                                        jobtask.status = status
                                    else:
                                        jobtask.status = '3'
                                    if duration:
                                        jobtask.duration = duration
                                    else:
                                        jobtask.duration = task.estimated_time
                                    jobtask.save()

                            old_jobparts = job.jobpart_set.all()
                            for jp in old_jobparts:
                                jp.is_deleted = True
                                jp.save()

                            for part_form in part_formset:
                                part_name = part_form.cleaned_data.get('part_name')
                                quantity = part_form.cleaned_data.get('quantity')

                                if part_name and quantity:
                                    part = get_object_or_404(Part, name=part_name)
                                    # jobpart = JobPart.objects.get_or_create(part=part, job=job, is_deleted=False)
                                    jobpart = job.jobpart_set.get_or_create(part=part, quantity=quantity)

                                    if jobpart[0].is_deleted is True:
                                        jobpart[0].is_deleted = False
                                        jobpart[0].save()
                                    if jobpart[1] is True:
                                        job.jobpart_set.add(jobpart[0])

                                    # jobpart[0].quantity = quantity


                                    # checks that the quantity required is not more than the total quantity in stock.
                                    # if it is, it removes the quantity used for a job from the total quantity and assigns,
                                    # the quantity to the job part object, otherwise, it throws an error.
                                    # TODO: do something if q drops below threshold
                                    if part.quantity >= quantity:
                                        part.quantity -= quantity
                                        part.save()
                                    else:
                                        # TODO: when changed back to TRUE, must subtract ^
                                        jobpart[0].sufficient_quantity = False
                                        # raise forms.ValidationError(
                                        #     'Not enough parts in stock.',
                                        #     code='insufficient_parts'
                                        # )
                                        jobpart[0].save()


                            for t in job.jobtask_set.filter(is_deleted=False):
                                if t.status == '1':
                                    complete = True
                                    job.status = '1'
                                else:
                                    complete = False
                                    break


                            if complete is False:
                                for t in job.jobtask_set.filter(is_deleted=False):
                                    if t.status == '2':
                                        job.status = '2'
                                        break
                                    else:
                                        job.status = '3'

                            job.save()
                            if complete is True:
                                last_id = Invoice.objects.last().id
                                new_id = last_id + 1
                                invoice = Invoice.objects.create(job_done=job, invoice_number=new_id, issue_date=datetime.date.today())

                            messages.success(request, "Your changes to Job No." + str(job.job_number) + " were saved.")
                            return HttpResponseRedirect('/garits/jobs/active/')

                    except IntegrityError:
                        messages.error(request, "There was an error saving")

            else:
                data = {}
                data2 = {}
                data['job_number'] = job.job_number
                data['vehicle'] = job.vehicle.reg_number
                data['type'] = job.type
                data['bay'] = job.bay
                data['status'] = job.status
                data['booking_date'] = job.booking_date
                data['work_carried_out'] = job.work_carried_out
                data2['mechanic'] = job.mechanic

                form = JobEditForm(initial=data)
                mechanic_form = MechanicJobForm(initial=data2)
                task_formset = TaskFormSet(initial=tasks_data, prefix='fs1')
                part_formset = PartFormSet(initial=parts_data, prefix='fs2')

            context = {
                'form': form,
                'mechanic_form': mechanic_form,
                'task_formset': task_formset,
                'part_formset': part_formset,
                'task_helper': task_helper,
                'part_helper': part_helper,
                'job': job,
            }

            return render(request, 'nod/assign_jobsheet.html', context)
        else:
            messages.error(request, "You must be a franchisee/mechanic/foreperson/receptionist in order to view this page.")
            return redirect('/garits/')


# @login_required
# def assign_mechanic_job(request, uuid):
#     if request.user.staffmember.role == '2':
#         job = get_object_or_404(Job, uuid=uuid)
#
#         TaskFormSet = formset_factory(JobTaskForm, formset=BaseJobTaskForm, min_num=1, extra=0)
#         task_set = job.jobtask_set.all()
#         tasks_data = [{'task_name': t.task, 'status': t.status, 'duration': t.duration}
#                       for t in task_set]
#
#         PartFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm, min_num=1, extra=0)
#         part_set = job.jobpart_set.all()
#         parts_data = [{'part_name': p.part, 'quantity': p.quantity}
#                       for p in part_set]
#
#         task_helper = TaskFormSetHelper()
#         part_helper = PartFormSetHelper()
#
#         if request.method == 'POST':
#             form = JobEditForm(request.POST)
#             mechanic_form = MechanicJobForm(request.POST)
#             task_formset = TaskFormSet(request.POST, prefix='fs1')
#             part_formset = PartFormSet(request.POST, prefix='fs2')
#
#             if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
#                 # job_number = form.cleaned_data['job_number']
#                 vehicle = form.cleaned_data['vehicle']
#                 booking_date = form.cleaned_data['booking_date']
#                 bay = form.cleaned_data['bay']
#                 mechanic = mechanic_form.cleaned_data['mechanic']
#
#                 vehicle = get_object_or_404(Vehicle, reg_number=vehicle)
#
#                 # bay = get_object_or_404(Bay, bay_type=bay)
#
#                 # job.job_number = job.id?
#                 try:
#                     with transaction.atomic():
#                         job.booking_date = booking_date
#                         job.bay = bay
#                         job.mechanic = mechanic
#
#                         old_jobtasks = job.jobtask_set.all()
#                         for jt in old_jobtasks:
#                             jt.is_deleted = True
#                             jt.save()
#
#                         for task_form in task_formset:
#                             task_name = task_form.cleaned_data.get('task_name')
#                             status = task_form.cleaned_data.get('status')
#                             duration = task_form.cleaned_data.get('duration')
#
#                             if task_name:
#                                 task = get_object_or_404(Task, description=task_name)
#                                 # jobtask = JobTask.objects.get_or_create(task=task, job=job, is_deleted=False)
#                                 jobtask = job.jobtask_set.get_or_create(task=task)
#
#                                 # get_or_create returns tuple {object returned, whether it was created or just retrieved}
#                                 if jobtask[0].is_deleted is True:
#                                     jobtask[0].is_deleted = False
#                                     jobtask[0].save()
#                                 if jobtask[1] is True:
#                                     job.jobtask_set.add(jobtask[0])
#
#                                 jobtask = jobtask[0]
#                                 if status:
#                                     jobtask.status = status
#                                 else:
#                                     jobtask.status = '3'
#                                 if duration:
#                                     jobtask.duration = duration
#                                 else:
#                                     jobtask.duration = task.estimated_time
#                                 jobtask.save()
#
#                         old_jobparts = job.jobpart_set.all()
#                         for jp in old_jobparts:
#                             jp.is_deleted = True
#                             jp.save()
#
#                         for part_form in part_formset:
#                             part_name = part_form.cleaned_data.get('part_name')
#                             quantity = part_form.cleaned_data.get('quantity')
#
#                             if part_name and quantity:
#                                 part = get_object_or_404(Part, name=part_name)
#                                 # jobpart = JobPart.objects.get_or_create(part=part, job=job, is_deleted=False)
#                                 jobpart = job.jobpart_set.get_or_create(part=part, quantity=quantity)
#
#                                 if jobpart[0].is_deleted is True:
#                                     jobpart[0].is_deleted = False
#                                     jobpart[0].save()
#                                 if jobpart[1] is True:
#                                     job.jobpart_set.add(jobpart[0])
#
#                                 # jobpart[0].quantity = quantity
#
#
#                                 # checks that the quantity required is not more than the total quantity in stock.
#                                 # if it is, it removes the quantity used for a job from the total quantity and assigns,
#                                 # the quantity to the job part object, otherwise, it throws an error.
#                                 # TODO: do something if q drops below threshold
#                                 if part.quantity >= quantity:
#                                     part.quantity -= quantity
#                                     part.save()
#                                 else:
#                                     # TODO: when changed back to TRUE, must subtract ^
#                                     jobpart[0].sufficient_quantity = False
#                                     # raise forms.ValidationError(
#                                     #     'Not enough parts in stock.',
#                                     #     code='insufficient_parts'
#                                     # )
#                                     jobpart[0].save()
#
#                         job.save()
#
#                         return HttpResponseRedirect('/garits/jobs/active/')
#
#                 except IntegrityError:
#                     messages.error(request, "There was an error saving")
#
#         else:
#             data = {}
#             data2 = {}
#             data['job_number'] = job.job_number
#             data['vehicle'] = job.vehicle.reg_number
#             data['type'] = job.type
#             data['bay'] = job.bay
#             data['status'] = job.status
#             data['booking_date'] = job.booking_date
#             data['work_carried_out'] = job.work_carried_out
#             data2['mechanic'] = job.mechanic
#
#             form = JobEditForm(initial=data)
#             mechanic_form = MechanicJobForm(initial=data2)
#             task_formset = TaskFormSet(initial=tasks_data, prefix='fs1')
#             part_formset = PartFormSet(initial=parts_data, prefix='fs2')
#
#         context = {
#             'form': form,
#             'mechanic_form': mechanic_form,
#             'task_formset': task_formset,
#             'part_formset': part_formset,
#             'task_helper': task_helper,
#             'part_helper': part_helper,
#             'job': job,
#         }
#
#         return render(request, 'nod/assign_jobsheet.html', context)
#     else:
#         messages.error(request, "You must be a foreperson in order to view this page.")
#         return redirect('/garits/')


@login_required
def delete_job(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        job = get_object_or_404(Job, uuid=uuid)

        job.is_deleted = True
        job.save()

        messages.error(request, "Job No." + job.job_number + " deleted.")
        return HttpResponseRedirect('/garits/jobs/active/')
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid() and password_form.is_valid():
            username = form.cleaned_data['user_name']
            password_form.save()
            update_session_auth_hash(request, password_form.user)

            request.user.username = username

            request.user.save()

            return HttpResponseRedirect('/thanks/')

    else:
        data = {}
        data['user_name'] = request.user.username

        form = ProfileForm(initial=data)
        password_form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'password_form': password_form,
        'user': request.user
    }

    return render(request, 'nod/edit_profile.html', context)


@login_required
def create_dropin(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or\
                    request.user.staffmember.role == '2':
        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
        email_data = []
        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
        phone_data = []

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = DropinForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            customer_uuid = form.data['customer_uuid']
            print(customer_uuid)
            try:
                dropin = Dropin.objects.get(uuid=customer_uuid, is_deleted=False)
            except MultipleObjectsReturned:
                pass
            except ObjectDoesNotExist:
                pass

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                date = form.cleaned_data['date']

                # create Dropin Customer object using input data
                # dropin = Dropin.objects.create(forename=forename, surname=surname, date=date)

                try:
                    with transaction.atomic():
                        dropin.forename = forename
                        dropin.surname = surname
                        dropin.date = date

                        dropin.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                dropin.emails.add(email)
                                dropin.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                dropin.phone_numbers.add(phone)
                                dropin.save()

                        dropin.save()

                        return HttpResponseRedirect('/garits/customers/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            dropin = Dropin.objects.create()
            data = {}
            data['customer_uuid'] = dropin.uuid
            form = DropinForm(initial=data)
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'dropin': dropin,
        }

        return render(request, 'nod/create_dropin.html', context)
    else:
        messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_dropin(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        dropin = get_object_or_404(Dropin, uuid=uuid)

        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
        user_emails = dropin.emails.filter(is_deleted=False)
        email_data = [{'email_address': e.address, 'email_type': e.type}
                      for e in user_emails]

        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
        user_phone_numbers = dropin.phone_numbers.filter(is_deleted=False)
        phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                      for p in user_phone_numbers]

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = DropinForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                date = form.cleaned_data['date']

                try:
                    with transaction.atomic():
                        dropin.forename = forename
                        dropin.surname = surname
                        dropin.date = date

                        dropin.save()

                        old_emails = dropin.emails.all()
                        print(old_emails)
                        for e in old_emails:
                            e.is_deleted = True
                            e.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                # updates = {'is_deleted':'True'}
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                dropin.emails.add(email)
                                dropin.save()

                        old_phones = dropin.phone_numbers.all()
                        for p in old_phones:
                            p.is_deleted = True
                            p.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                dropin.phone_numbers.add(phone)
                                dropin.save()

                        dropin.save()

                        return HttpResponseRedirect('/garits/customers/')

                except IntegrityError:
                    #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
        else:
            data = {}
            data['forename'] = dropin.forename
            data['surname'] = dropin.surname
            data['date'] = dropin.date

            form = DropinForm(initial=data)
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'dropin': dropin,
        }

        return render(request, 'nod/edit_dropin.html', context)
    else:
        messages.error(request, "You must be a foreperson/franchisee/receptionist in order to view this page.")
        return redirect('/garits/')


@login_required
def create_account_holder(request):
    if request.user.staffmember.role == '3':
        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
        email_data = []
        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
        phone_data = []

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = AccountHolderForm(request.POST)
            discount_form = DiscountPlanForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            customer_uuid = form.data['customer_uuid']
            print(customer_uuid)

            try:
                account_holder = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
            except MultipleObjectsReturned:
                pass
            except ObjectDoesNotExist:
                pass

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                print('a)')
                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                date = form.cleaned_data['date']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']
                discount_plan = discount_form.cleaned_data['discount_plan']

                # create Account Holder Customer object using input data
                # account_holder = AccountHolder.objects.create(forename=forename, surname=surname, date=date,
                #                                               address=address, postcode=postcode,
                #                                               discount_plan=discount_plan)
                try:
                    with transaction.atomic():
                        print('b')
                        account_holder.forename = forename
                        account_holder.surname = surname
                        account_holder.date = date
                        account_holder.address = address
                        account_holder.postcode = postcode

                        if discount_plan is not '':
                            # if fixed
                            if discount_plan == '1':
                                discount = FixedDiscount.objects.get()

                            # flexible
                            if discount_plan == '2':
                                discount = FlexibleDiscount.objects.first()

                            # variable
                            if discount_plan == '3':
                                discount = VariableDiscount.objects.get()

                            account_holder.content_object = discount
                            print('c')

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                account_holder.emails.add(email)
                                account_holder.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                account_holder.phone_numbers.add(phone)
                                account_holder.save()
                        print(request.POST)
                        account_holder.save()

                        return HttpResponseRedirect('/garits/customers/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            account_holder = AccountHolder.objects.create()
            data = {}
            data['customer_uuid'] = account_holder.uuid
            form = AccountHolderForm(initial=data)
            discount_form = DiscountPlanForm()
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'discount_form': discount_form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'account_holder': account_holder,
        }

        return render(request, 'nod/create_account_holder.html', context)
    else:
        if request.user.staffmember.role == '4' or request.user.staffmember.role == '2':
            EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
            email_data = []
            PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
            phone_data = []

            email_helper = EmailFormSetHelper()
            phone_helper = PhoneFormSetHelper()

            if request.method == 'POST':
                form = AccountHolderForm(request.POST)
                email_formset = EmailFormSet(request.POST, prefix='fs1')
                phone_formset = PhoneFormSet(request.POST, prefix='fs2')

                customer_uuid = form.data['customer_uuid']
                print(customer_uuid)

                try:
                    account_holder = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
                except MultipleObjectsReturned:
                    pass
                except ObjectDoesNotExist:
                    pass

                if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                    print('a)')
                    forename = form.cleaned_data['forename']
                    surname = form.cleaned_data['surname']
                    date = form.cleaned_data['date']
                    address = form.cleaned_data['address']
                    postcode = form.cleaned_data['postcode']

                    # create Account Holder Customer object using input data
                    # account_holder = AccountHolder.objects.create(forename=forename, surname=surname, date=date,
                    #                                               address=address, postcode=postcode,
                    #                                               discount_plan=discount_plan)
                    try:
                        with transaction.atomic():
                            print('b')
                            account_holder.forename = forename
                            account_holder.surname = surname
                            account_holder.date = date
                            account_holder.address = address
                            account_holder.postcode = postcode

                            for email_form in email_formset:
                                email_address = email_form.cleaned_data.get('email_address')
                                email_type = email_form.cleaned_data.get('email_type')

                                if email_address and email_type:
                                    email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                    email = email[0]
                                    if email.is_deleted is True:
                                        email.is_deleted = False
                                        email.save()
                                    account_holder.emails.add(email)
                                    account_holder.save()

                            for phone_form in phone_formset:
                                phone_number = phone_form.cleaned_data.get('phone_number')
                                phone_type = phone_form.cleaned_data.get('phone_type')

                                if phone_number and phone_type:
                                    phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                    phone = phone[0]
                                    if phone.is_deleted is True:
                                        phone.is_deleted = False
                                        phone.save()
                                    account_holder.phone_numbers.add(phone)
                                    account_holder.save()
                            print(request.POST)
                            account_holder.save()

                            return HttpResponseRedirect('/garits/customers/')

                    except IntegrityError:
                        messages.error(request, "There was an error saving")

            else:
                account_holder = AccountHolder.objects.create()
                data = {}
                data['customer_uuid'] = account_holder.uuid
                form = AccountHolderForm(initial=data)
                email_formset = EmailFormSet(initial=email_data, prefix='fs1')
                phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

            context = {
                'form': form,
                'email_formset': email_formset,
                'phone_formset': phone_formset,
                'email_helper': email_helper,
                'phone_helper': phone_helper,
                'account_holder': account_holder,
            }

            return render(request, 'nod/create_account_holder.html', context)
        else:
            messages.error(request, "You must be a foreperson/franchisee/receptionist in order to view this page.")
            return redirect('/garits/')


@login_required
def edit_account_holder(request, uuid):
    if request.user.staffmember.role == '3':
        account_holder = get_object_or_404(AccountHolder, uuid=uuid)

        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
        user_emails = account_holder.emails.filter(is_deleted=False)
        email_data = [{'email_address': e.address, 'email_type': e.type}
                      for e in user_emails]

        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
        user_phone_numbers = account_holder.phone_numbers.filter(is_deleted=False)
        phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                      for p in user_phone_numbers]

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()
        print('1')

        if request.method == 'POST':
            form = AccountHolderForm(request.POST)
            discount_form = DiscountPlanForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')
            print('2')


            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                print('3')

                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                date = form.cleaned_data['date']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']
                discount_plan = discount_form.cleaned_data['discount_plan']

                try:
                    with transaction.atomic():
                        print('4')

                        account_holder.forename = forename
                        account_holder.surname = surname
                        account_holder.date = date
                        account_holder.address = address
                        account_holder.postcode = postcode

                        if discount_plan is not '':
                            # if fixed
                            if discount_plan == '1':
                                discount = FixedDiscount.objects.get()

                            # flexible
                            if discount_plan == '2':
                                discount = FlexibleDiscount.objects.first()

                            # variable
                            if discount_plan == '3':
                                discount = VariableDiscount.objects.get()

                            account_holder.content_object = discount

                        old_emails = account_holder.emails.all()
                        print(old_emails)
                        for e in old_emails:
                            e.is_deleted = True
                            e.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                # updates = {'is_deleted':'True'}
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                account_holder.emails.add(email)
                                account_holder.save()

                        old_phones = account_holder.phone_numbers.all()
                        for p in old_phones:
                            p.is_deleted = True
                            p.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                account_holder.phone_numbers.add(phone)
                                account_holder.save()

                        account_holder.save()

                        messages.success(request, "Changes were saved successfully!")
                        return redirect('view-customer', uuid=account_holder.uuid)

                except IntegrityError:
                    #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
            else:
                messages.error(request, 'There was an error saving your profile.')

        else:
            data = {}
            data['customer_uuid'] = account_holder.uuid
            data['forename'] = account_holder.forename
            data['surname'] = account_holder.surname
            data['date'] = account_holder.date
            data['address'] = account_holder.address
            data['postcode'] = account_holder.postcode
            data2 = {}
            discount = account_holder.content_object
            if discount == FixedDiscount.objects.get():
                data2['discount_plan'] = '1'
            else:
                if discount == FlexibleDiscount.objects.first():
                    data2['discount_plan'] = '2'
                else:
                    if discount == VariableDiscount.objects.get():
                        data2['discount_plan'] = '3'
                    else:
                        data2['discount_plan'] = ""

            form = AccountHolderForm(initial=data)
            discount_form = DiscountPlanForm(initial=data2)
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'discount_form': discount_form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'account_holder': account_holder,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
        }

        return render(request, 'nod/edit_account_holder.html', context)
    else:
        if request.user.staffmember.role == '4' or request.user.staffmember.role == '2':
            account_holder = get_object_or_404(AccountHolder, uuid=uuid)

            EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
            user_emails = account_holder.emails.filter(is_deleted=False)
            email_data = [{'email_address': e.address, 'email_type': e.type}
                          for e in user_emails]

            PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
            user_phone_numbers = account_holder.phone_numbers.filter(is_deleted=False)
            phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                          for p in user_phone_numbers]

            email_helper = EmailFormSetHelper()
            phone_helper = PhoneFormSetHelper()
            print('1')

            if request.method == 'POST':
                form = AccountHolderForm(request.POST)
                email_formset = EmailFormSet(request.POST, prefix='fs1')
                phone_formset = PhoneFormSet(request.POST, prefix='fs2')
                print('2')


                if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                    print('3')

                    forename = form.cleaned_data['forename']
                    surname = form.cleaned_data['surname']
                    date = form.cleaned_data['date']
                    address = form.cleaned_data['address']
                    postcode = form.cleaned_data['postcode']

                    try:
                        with transaction.atomic():
                            print('4')

                            account_holder.forename = forename
                            account_holder.surname = surname
                            account_holder.date = date
                            account_holder.address = address
                            account_holder.postcode = postcode

                            old_emails = account_holder.emails.all()
                            print(old_emails)
                            for e in old_emails:
                                e.is_deleted = True
                                e.save()

                            for email_form in email_formset:
                                email_address = email_form.cleaned_data.get('email_address')
                                email_type = email_form.cleaned_data.get('email_type')

                                if email_address and email_type:
                                    # updates = {'is_deleted':'True'}
                                    email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                    email = email[0]
                                    if email.is_deleted is True:
                                        email.is_deleted = False
                                        email.save()
                                    account_holder.emails.add(email)
                                    account_holder.save()

                            old_phones = account_holder.phone_numbers.all()
                            for p in old_phones:
                                p.is_deleted = True
                                p.save()

                            for phone_form in phone_formset:
                                phone_number = phone_form.cleaned_data.get('phone_number')
                                phone_type = phone_form.cleaned_data.get('phone_type')

                                if phone_number and phone_type:
                                    phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                    phone = phone[0]
                                    if phone.is_deleted is True:
                                        phone.is_deleted = False
                                        phone.save()
                                    account_holder.phone_numbers.add(phone)
                                    account_holder.save()

                            account_holder.save()

                            messages.success(request, "Changes were saved successfully!")
                            return redirect('view-customer', uuid=account_holder.uuid)

                    except IntegrityError:
                        #If the transaction failed
                        messages.error(request, 'There was an error saving your profile.')
                else:
                    messages.error(request, 'There was an error saving your profile.')

            else:
                data = {}
                data['customer_uuid'] = account_holder.uuid
                data['forename'] = account_holder.forename
                data['surname'] = account_holder.surname
                data['date'] = account_holder.date
                data['address'] = account_holder.address
                data['postcode'] = account_holder.postcode

                form = AccountHolderForm(initial=data)
                email_formset = EmailFormSet(initial=email_data, prefix='fs1')
                phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

            context = {
                'form': form,
                'email_formset': email_formset,
                'phone_formset': phone_formset,
                'account_holder': account_holder,
                'email_helper': email_helper,
                'phone_helper': phone_helper,
            }

            return render(request, 'nod/edit_account_holder.html', context)
        else:
            messages.error(request, "You must be a foreperson/franchisee/receptionist in order to view this page.")
            return redirect('/garits/')


@login_required
def create_business_customer(request):
    if request.user.staffmember.role == '3':
        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
        email_data = []
        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
        phone_data = []

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = BusinessCustomerForm(request.POST)
            discount_form = DiscountPlanForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            customer_uuid = form.data['customer_uuid']

            try:
                business_customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
            except MultipleObjectsReturned:
                pass
            except ObjectDoesNotExist:
                pass

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                company_name = form.cleaned_data['company_name']
                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                rep_role = form.cleaned_data['rep_role']
                date = form.cleaned_data['date']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']
                discount_plan = discount_form.cleaned_data['discount_plan']

                # create Business Company Customer object using input data
                # business_customer = BusinessCustomer.objects.create(forename=forename, surname=surname, date=date,
                #                                                     address=address, postcode=postcode,
                #                                                     discount_plan=discount_plan, company_name=company_name,
                #                                                     rep_role=rep_role)
                try:
                    with transaction.atomic():
                        business_customer.company_name = company_name
                        business_customer.forename = forename
                        business_customer.surname = surname
                        business_customer.rep_role = rep_role
                        business_customer.date = date
                        business_customer.address = address
                        business_customer.postcode = postcode

                        if discount_plan is not '':
                            # if fixed
                            if discount_plan == '1':
                                discount = FixedDiscount.objects.get()

                            # flexible
                            if discount_plan == '2':
                                discount = FlexibleDiscount.objects.first()

                            # variable
                            if discount_plan == '3':
                                discount = VariableDiscount.objects.get()

                            business_customer.content_object = discount

                        business_customer.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                business_customer.emails.add(email)
                                business_customer.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                business_customer.phone_numbers.add(phone)
                                business_customer.save()

                        business_customer.save()

                        return HttpResponseRedirect('/garits/customers/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            business_customer = BusinessCustomer.objects.create()
            data = {}
            data['customer_uuid'] = business_customer.uuid
            form = BusinessCustomerForm(initial=data)
            discount_form = DiscountPlanForm()
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'discount_form': discount_form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'business_customer': business_customer
        }

        return render(request, 'nod/create_business_customer.html', context)
    else:
        if request.user.staffmember.role == '4' or request.user.staffmember.role == '2':
            EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
            email_data = []
            PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
            phone_data = []

            email_helper = EmailFormSetHelper()
            phone_helper = PhoneFormSetHelper()

            if request.method == 'POST':
                form = BusinessCustomerForm(request.POST)
                email_formset = EmailFormSet(request.POST, prefix='fs1')
                phone_formset = PhoneFormSet(request.POST, prefix='fs2')

                customer_uuid = form.data['customer_uuid']

                try:
                    business_customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
                except MultipleObjectsReturned:
                    pass
                except ObjectDoesNotExist:
                    pass

                if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                    company_name = form.cleaned_data['company_name']
                    forename = form.cleaned_data['forename']
                    surname = form.cleaned_data['surname']
                    rep_role = form.cleaned_data['rep_role']
                    date = form.cleaned_data['date']
                    address = form.cleaned_data['address']
                    postcode = form.cleaned_data['postcode']

                    # create Business Company Customer object using input data
                    # business_customer = BusinessCustomer.objects.create(forename=forename, surname=surname, date=date,
                    #                                                     address=address, postcode=postcode,
                    #                                                     discount_plan=discount_plan, company_name=company_name,
                    #                                                     rep_role=rep_role)
                    try:
                        with transaction.atomic():
                            business_customer.company_name = company_name
                            business_customer.forename = forename
                            business_customer.surname = surname
                            business_customer.rep_role = rep_role
                            business_customer.date = date
                            business_customer.address = address
                            business_customer.postcode = postcode

                            business_customer.save()

                            for email_form in email_formset:
                                email_address = email_form.cleaned_data.get('email_address')
                                email_type = email_form.cleaned_data.get('email_type')

                                if email_address and email_type:
                                    email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                    email = email[0]
                                    if email.is_deleted is True:
                                        email.is_deleted = False
                                        email.save()
                                    business_customer.emails.add(email)
                                    business_customer.save()

                            for phone_form in phone_formset:
                                phone_number = phone_form.cleaned_data.get('phone_number')
                                phone_type = phone_form.cleaned_data.get('phone_type')

                                if phone_number and phone_type:
                                    phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                    phone = phone[0]
                                    if phone.is_deleted is True:
                                        phone.is_deleted = False
                                        phone.save()
                                    business_customer.phone_numbers.add(phone)
                                    business_customer.save()

                            business_customer.save()

                            return HttpResponseRedirect('/garits/customers/')

                    except IntegrityError:
                        messages.error(request, "There was an error saving")

            else:
                business_customer = BusinessCustomer.objects.create()
                data = {}
                data['customer_uuid'] = business_customer.uuid
                form = BusinessCustomerForm(initial=data)
                email_formset = EmailFormSet(initial=email_data, prefix='fs1')
                phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

            context = {
                'form': form,
                'email_formset': email_formset,
                'phone_formset': phone_formset,
                'email_helper': email_helper,
                'phone_helper': phone_helper,
                'business_customer': business_customer
            }

            return render(request, 'nod/create_business_customer.html', context)
        else:
            messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
            return redirect('/garits/')


@login_required
def edit_business_customer(request, uuid):
    if request.user.staffmember.role == '3':
        business_customer = get_object_or_404(BusinessCustomer, uuid=uuid)

        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
        user_emails = business_customer.emails.filter(is_deleted=False)
        email_data = [{'email_address': e.address, 'email_type': e.type}
                      for e in user_emails]

        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
        user_phone_numbers = business_customer.phone_numbers.filter(is_deleted=False)
        phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                      for p in user_phone_numbers]

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = BusinessCustomerForm(request.POST)
            discount_form = DiscountPlanForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                company_name = form.cleaned_data['company_name']
                forename = form.cleaned_data['forename']
                surname = form.cleaned_data['surname']
                rep_role = form.cleaned_data['rep_role']
                date = form.cleaned_data['date']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']
                discount_plan = discount_form.cleaned_data['discount_plan']

                try:
                    with transaction.atomic():
                        business_customer.company_name = company_name
                        business_customer.forename = forename
                        business_customer.surname = surname
                        business_customer.rep_role = rep_role
                        business_customer.date = date
                        business_customer.address = address
                        business_customer.postcode = postcode

                        if discount_plan is not '':
                            # if fixed
                            if discount_plan == '1':
                                discount = FixedDiscount.objects.get()

                            # flexible
                            if discount_plan == '2':
                                discount = FlexibleDiscount.objects.first()

                            # variable
                            if discount_plan == '3':
                                discount = VariableDiscount.objects.get()

                            business_customer.content_object = discount

                        business_customer.save()

                        old_emails = business_customer.emails.all()
                        print(old_emails)
                        for e in old_emails:
                            e.is_deleted = True
                            e.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                # updates = {'is_deleted':'True'}
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                business_customer.emails.add(email)
                                business_customer.save()

                        old_phones = business_customer.phone_numbers.all()
                        for p in old_phones:
                            p.is_deleted = True
                            p.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                business_customer.phone_numbers.add(phone)
                                business_customer.save()

                        business_customer.save()

                        messages.success(request, "Changes were saved successfully!")
                        return redirect('view-customer', uuid=business_customer.uuid)

                except IntegrityError:
                    #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
        else:
            data = {}
            data['customer_uuid'] = business_customer.uuid
            data['company_name'] = business_customer.company_name
            data['forename'] = business_customer.forename
            data['surname'] = business_customer.surname
            data['rep_role'] = business_customer.rep_role
            data['date'] = business_customer.date
            data['address'] = business_customer.address
            data['postcode'] = business_customer.postcode
            data2 = {}
            discount = business_customer.content_object
            if discount == FixedDiscount.objects.get():
                data2['discount_plan'] = '1'
            else:
                if discount == FlexibleDiscount.objects.first():
                    data2['discount_plan'] = '2'
                else:
                    if discount == VariableDiscount.objects.get():
                        data2['discount_plan'] = '3'
                    else:
                        data2['discount_plan'] = ""

            form = BusinessCustomerForm(initial=data)
            discount_form = DiscountPlanForm(initial=data2)
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'discount_form': discount_form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'business_customer': business_customer,
        }

        return render(request, 'nod/edit_business_customer.html', context)
    else:
        if request.user.staffmember.role == '4' or request.user.staffmember.role == '2':
            business_customer = get_object_or_404(BusinessCustomer, uuid=uuid)

            EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
            user_emails = business_customer.emails.filter(is_deleted=False)
            email_data = [{'email_address': e.address, 'email_type': e.type}
                          for e in user_emails]

            PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
            user_phone_numbers = business_customer.phone_numbers.filter(is_deleted=False)
            phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                          for p in user_phone_numbers]

            email_helper = EmailFormSetHelper()
            phone_helper = PhoneFormSetHelper()

            if request.method == 'POST':
                form = BusinessCustomerForm(request.POST)
                email_formset = EmailFormSet(request.POST, prefix='fs1')
                phone_formset = PhoneFormSet(request.POST, prefix='fs2')

                if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                    company_name = form.cleaned_data['company_name']
                    forename = form.cleaned_data['forename']
                    surname = form.cleaned_data['surname']
                    rep_role = form.cleaned_data['rep_role']
                    date = form.cleaned_data['date']
                    address = form.cleaned_data['address']
                    postcode = form.cleaned_data['postcode']

                    try:
                        with transaction.atomic():
                            business_customer.company_name = company_name
                            business_customer.forename = forename
                            business_customer.surname = surname
                            business_customer.rep_role = rep_role
                            business_customer.date = date
                            business_customer.address = address
                            business_customer.postcode = postcode

                            business_customer.save()

                            old_emails = business_customer.emails.all()
                            print(old_emails)
                            for e in old_emails:
                                e.is_deleted = True
                                e.save()

                            for email_form in email_formset:
                                email_address = email_form.cleaned_data.get('email_address')
                                email_type = email_form.cleaned_data.get('email_type')

                                if email_address and email_type:
                                    # updates = {'is_deleted':'True'}
                                    email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                    email = email[0]
                                    if email.is_deleted is True:
                                        email.is_deleted = False
                                        email.save()
                                    business_customer.emails.add(email)
                                    business_customer.save()

                            old_phones = business_customer.phone_numbers.all()
                            for p in old_phones:
                                p.is_deleted = True
                                p.save()

                            for phone_form in phone_formset:
                                phone_number = phone_form.cleaned_data.get('phone_number')
                                phone_type = phone_form.cleaned_data.get('phone_type')

                                if phone_number and phone_type:
                                    phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                    phone = phone[0]
                                    if phone.is_deleted is True:
                                        phone.is_deleted = False
                                        phone.save()
                                    business_customer.phone_numbers.add(phone)
                                    business_customer.save()

                            business_customer.save()

                            messages.success(request, "Changes were saved successfully!")
                            return redirect('view-customer', uuid=business_customer.uuid)

                    except IntegrityError:
                        #If the transaction failed
                        messages.error(request, 'There was an error saving your profile.')
            else:
                data = {}
                data['customer_uuid'] = business_customer.uuid
                data['company_name'] = business_customer.company_name
                data['forename'] = business_customer.forename
                data['surname'] = business_customer.surname
                data['rep_role'] = business_customer.rep_role
                data['date'] = business_customer.date
                data['address'] = business_customer.address
                data['postcode'] = business_customer.postcode

                form = BusinessCustomerForm(initial=data)
                email_formset = EmailFormSet(initial=email_data, prefix='fs1')
                phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

            context = {
                'form': form,
                'email_formset': email_formset,
                'phone_formset': phone_formset,
                'email_helper': email_helper,
                'phone_helper': phone_helper,
                'business_customer': business_customer,
            }

            return render(request, 'nod/edit_business_customer.html', context)
        else:
            messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
            return redirect('/garits/')


@login_required
def delete_customer(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        try:
            customer = Dropin.objects.get(uuid=uuid, is_deleted=False)
        except ObjectDoesNotExist:
            try:
                customer = AccountHolder.objects.get(uuid=uuid, is_deleted=False)
            except ObjectDoesNotExist:
                try:
                    customer = BusinessCustomer.objects.get(uuid=uuid, is_deleted=False)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass # TODO: get last one?
            except MultipleObjectsReturned:
                pass
        except MultipleObjectsReturned:
            pass

        customer.is_deleted = True
        customer.save()

        return HttpResponseRedirect('/garits/customers/')
    else:
        messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
        return redirect('/garits/')


@login_required
def view_customer(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
        request.user.staffmember.role == '2':
        try:
            customer = BusinessCustomer.objects.get(uuid=uuid, is_deleted=False)

        except ObjectDoesNotExist:
            try:
                customer = AccountHolder.objects.get(uuid=uuid, is_deleted=False)
            except ObjectDoesNotExist:
                try:
                    customer = Dropin.objects.get(uuid=uuid, is_deleted=False)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass # TODO: get last one?
            except MultipleObjectsReturned:
                pass
        except MultipleObjectsReturned:
            pass

        if customer.suspended:
            if len(customer.get_unpaid_invoices()) < 0:
                for invoice in customer.get_unpaid_invoices():
                    if invoice.reminder_phase == '4' or invoice.issue_date <= (datetime.date.today() - relativedelta(months=3, weeks=1)):
                        customer.suspended = True
                        break
                    else:
                        customer.suspended = False
            else:
                customer.suspended = False
        customer.save()

        if customer.suspended is True:
            messages.error(request, "SUSPENDED")

        vehicle_table = VehicleTable(customer.vehicle_set.filter(is_deleted=False))
        RequestConfig(request).configure(vehicle_table)

        invoice_table = UnpaidInvoiceTable(customer.get_unpaid_invoices())
        RequestConfig(request).configure(invoice_table)

        template = loader.get_template('nod/view_customer.html')
        context = RequestContext(request, {
            'customer': customer,
            'vehicle_table': vehicle_table,
            'invoice_table': invoice_table
        })
        return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def create_vehicle(request, customer_uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':

        # get customer from uuid. First try Dropin customer with given uuid, if not found or if multiple found,
        # check for account holder, if still not found, check business customer.
        try:
            customer = Dropin.objects.get(uuid=customer_uuid, is_deleted=False)
        except ObjectDoesNotExist:
            try:
                customer = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
            except ObjectDoesNotExist:
                try:
                    customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass # TODO: get last one?
            except MultipleObjectsReturned:
                pass
        except MultipleObjectsReturned:
            pass

        if request.method == 'POST':
            form = VehicleForm(request.POST)

            if form.is_valid():
                reg_number = form.cleaned_data['reg_number']
                make = form.cleaned_data['make']
                model = form.cleaned_data['model']
                engine_serial = form.cleaned_data['engine_serial']
                chassis_number = form.cleaned_data['chassis_number']
                color = form.cleaned_data['color']
                mot_base_date = form.cleaned_data['mot_base_date']
                type = form.cleaned_data['type']

                vehicle = Vehicle.objects.create(customer=customer, reg_number=reg_number, make=make, model=model,
                                                 engine_serial=engine_serial, chassis_number=chassis_number, color=color,
                                                 mot_base_date=mot_base_date, type=type)

                return render(request, 'nod/create_vehicle_success.html', {'vehicle': vehicle})

        else:
            form = VehicleForm()

        context = {
            'form': form,
            'customer': customer,
        }
        return render(request, 'nod/create_vehicle.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_vehicle(request, customer_uuid, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':

        # get customer from uuid. First try Dropin customer with given uuid, if not found or if multiple found,
        # check for account holder, if still not found, check business customer.
        try:
            customer = Dropin.objects.get(uuid=customer_uuid, is_deleted=False)
        except ObjectDoesNotExist:
            try:
                customer = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
            except ObjectDoesNotExist:
                try:
                    customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass # TODO: get last one?
            except MultipleObjectsReturned:
                pass
        except MultipleObjectsReturned:
            pass

        vehicle = get_object_or_404(Vehicle, uuid=uuid)
        print(uuid)
        print(vehicle.uuid)
        if request.method == 'POST':
            form = VehicleForm(request.POST)

            if form.is_valid():
                reg_number = form.cleaned_data['reg_number']
                make = form.cleaned_data['make']
                model = form.cleaned_data['model']
                engine_serial = form.cleaned_data['engine_serial']
                chassis_number = form.cleaned_data['chassis_number']
                color = form.cleaned_data['color']
                mot_base_date = form.cleaned_data['mot_base_date']
                type = form.cleaned_data['type']

                vehicle.reg_number = reg_number
                vehicle.make = make
                vehicle.model = model
                vehicle.engine_serial = engine_serial
                vehicle.chassis_number = chassis_number
                vehicle.color = color
                vehicle.mot_base_date = mot_base_date
                vehicle.type = type

                vehicle.save()

                return redirect('view-customer', uuid=vehicle.get_customer().uuid)
            else:
                messages.error(request, "There was an error with the data input.")

        else:
            data = {}
            data['reg_number'] = vehicle.reg_number
            data['make'] = vehicle.make
            data['model'] = vehicle.model
            data['engine_serial'] = vehicle.engine_serial
            data['chassis_number'] = vehicle.chassis_number
            data['color'] = vehicle.color
            data['mot_base_date'] = vehicle.mot_base_date
            data['type'] = vehicle.type

            form = VehicleForm(initial=data)

        context = {
            'form': form,
            'customer': customer,
            'vehicle': vehicle
        }
        return render(request, 'nod/edit_vehicle.html', context)
    else:
        messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
        return redirect('/garits/')


@login_required
def delete_vehicle(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        vehicle = get_object_or_404(Vehicle, uuid=uuid)

        vehicle.is_deleted = True
        vehicle.save()

        # TODO: check that customer string is correct
        messages.error(request, "Vehicle " + vehicle.reg_number + " was removed from " + vehicle.get_customer().__str__())
        return redirect('view-customer', uuid=vehicle.get_customer().uuid)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


def get_vehicles(request, customer_uuid):
    # get customer from uuid. First try Dropin customer with given uuid, if not found or if multiple found,
    # check for account holder, if still not found, check business customer.
    try:
        customer = Dropin.objects.get(uuid=customer_uuid, is_deleted=False)
    except ObjectDoesNotExist:
        try:
            customer = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
        except ObjectDoesNotExist:
            try:
                customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass # TODO: get last one?
        except MultipleObjectsReturned:
            pass
    except MultipleObjectsReturned:
        pass

    data = None
    if request.is_ajax():
        vehicles = customer.vehicle_set.filter(is_deleted=False)
        results = []
        for v in vehicles:
            v_json = {}
            v_json['reg_number'] = v.reg_number
            v_json['make'] = v.make
            v_json['model'] = v.model
            v_json['uuid'] = v.uuid
            results.append(v_json)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required
def create_part(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        if request.method == 'POST':
            form = CreatePartForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']
                manufacturer = form.cleaned_data['manufacturer']
                vehicle_type = form.cleaned_data['vehicle_type']
                years = form.cleaned_data['years']
                code = form.cleaned_data['code']
                quantity = form.cleaned_data['quantity']
                price = form.cleaned_data['price']
                low_level_threshold = form.cleaned_data['low_level_threshold']

                Part.objects.create(name=name, manufacturer=manufacturer, vehicle_type=vehicle_type, years=years,
                                    code=code, quantity=quantity, price=price, low_level_threshold=low_level_threshold)

                return HttpResponseRedirect('/garits/parts/')

        else:
            form = CreatePartForm()

        return render(request, 'nod/create_part.html', {'form': form})
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_part(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        part = get_object_or_404(Part, uuid=uuid)

        if request.method == 'POST':
            form = EditPartForm(request.POST)

            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                price = form.cleaned_data['price']
                low_level_threshold = form.cleaned_data['low_level_threshold']

                part.quantity = quantity
                part.price = price
                part.low_level_threshold = low_level_threshold

                part.save()

                message = part.name + " was successfully edited!"
                messages.success(request, message)
                return HttpResponseRedirect('/garits/parts/')

        else:
            data = {}
            data['quantity'] = part.quantity
            data['price'] = part.price
            data['low_level_threshold'] = part.low_level_threshold

            form = EditPartForm(initial=data)

        context = {
            'form': form,
            'part': part,
        }
        return render(request, 'nod/edit_part.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def delete_part(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or\
                    request.user.staffmember.role == '2':
        part = get_object_or_404(Part, uuid=uuid)

        part.is_deleted = True
        part.save()

        messages.error(request, part.name + " was deleted.")
        return HttpResponseRedirect('/garits/parts/')
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


def get_vehicles_autocomplete(request):
    if request.is_ajax():
        q = request.GET.get('term')
        vehicles = Vehicle.objects.filter(reg_number__icontains=q, is_deleted=False)[:10]
        results = []
        for v in vehicles:
            v_json = {}
            v_json['id'] = v.id
            v_json['label'] = v.reg_number
            v_json['value'] = v.reg_number
            results.append(v_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required
def replenish_stock(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        PartCreateFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
        parts_data = []

        part_helper = PartFormSetHelper()

        if request.method == 'POST':
            part_formset = PartCreateFormSet(request.POST, prefix='fs2')
            form = ReplenishmentOrderForm(request.POST)

            if form.is_valid() and part_formset.is_valid():
                supplier_name = form.cleaned_data['company_name']
                date = form.cleaned_data['date']

                supplier = get_object_or_404(Supplier, company_name=supplier_name)

                try:
                    with transaction.atomic():
                        order = PartOrder.objects.create(supplier=supplier, date=date)

                        for part_form in part_formset:
                            part_name = part_form.cleaned_data['part_name']
                            quantity = part_form.cleaned_data['quantity']

                            if part_name and quantity:
                                part = get_object_or_404(Part, name=part_name)

                                order.orderpartrelationship_set.create(part=part, quantity=quantity,
                                                                                          is_deleted=False)

                                part.quantity += quantity
                                part.save()

                        messages.success(request, "Parts were successfully added to the stock!")
                        return HttpResponseRedirect('/garits/parts/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')
            form = ReplenishmentOrderForm()

        context = {
            'part_formset': part_formset,
            'part_helper': part_helper,
            'form': form
        }

        return render(request, 'nod/replenish_order.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_replenish_stock(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        order = get_object_or_404(PartOrder, uuid=uuid)
        PartCreateFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm, min_num=1, extra=0)
        part_set = order.orderpartrelationship_set.all()
        parts_data = [{'part_name': p.part, 'quantity': p.quantity}
                      for p in part_set]

        part_helper = PartFormSetHelper()

        if request.method == 'POST':
            part_formset = PartCreateFormSet(request.POST, prefix='fs2')
            form = ReplenishmentOrderForm(request.POST)

            if form.is_valid() and part_formset.is_valid():
                supplier_name = form.cleaned_data['company_name']
                date = form.cleaned_data['date']

                supplier = get_object_or_404(Supplier, company_name=supplier_name)

                try:
                    with transaction.atomic():
                        for part_form in part_formset:
                            part_name = part_form.cleaned_data['part_name']
                            quantity = part_form.cleaned_data['quantity']

                            if part_name and quantity:
                                part = get_object_or_404(Part, name=part_name)
                                print('a')
                                print(order)
                                print(part)
                                print(order.orderpartrelationship_set.all())
                                print(order.orderpartrelationship_set.get_or_create(part=part, is_deleted=False))
                                op = order.orderpartrelationship_set.get_or_create(part=part, is_deleted=False)

                                print('d')
                                # if object was created
                                if op[1] is True:
                                    print('b')
                                    op[0].quantity = quantity
                                    op[0].save()
                                    part.quantity += quantity
                                    part.save()
                                else:
                                    print('c')
                                    part.quantity = part.quantity - op[0].quantity + quantity
                                    part.save()
                                    op[0].quantity = quantity
                                    op[0].save()

                        return HttpResponseRedirect('/thanks/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            data = {}
            data['company_name'] = order.supplier.company_name
            data['date'] = order.date
            part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')
            form = ReplenishmentOrderForm(initial=data)

        context = {
            'part_formset': part_formset,
            'part_helper': part_helper,
            'form': form,
            'order': order
        }
        return render(request, 'nod/edit_replenish_order.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


def get_suppliers_autocomplete(request):
    if request.is_ajax():
        q = request.GET.get('term')
        suppliers = Supplier.objects.filter(company_name__icontains=q, is_deleted=False)[:10]
        results = []
        for s in suppliers:
            s_json = {}
            s_json['id'] = s.id
            s_json['label'] = s.company_name
            s_json['value'] = s.company_name
            results.append(s_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required
def create_supplier(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
        email_data = []
        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet)
        phone_data = []

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = SupplierForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')


            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                company_name = form.cleaned_data['company_name']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']

                try:
                    with transaction.atomic():
                        # create Supplier object using input data
                        supplier = Supplier.objects.create(company_name=company_name, address=address, postcode=postcode)

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                supplier.emails.add(email)
                                supplier.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                supplier.phone_numbers.add(phone)
                                supplier.save()

                        supplier.save()

                        return HttpResponseRedirect('/thanks/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            form = SupplierForm()
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
        }

        return render(request, 'nod/create_supplier.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_supplier(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        supplier = get_object_or_404(Supplier, uuid=uuid)

        EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet, min_num=1, extra=0)
        user_emails = supplier.emails.filter(is_deleted=False)
        email_data = [{'email_address': e.address, 'email_type': e.type}
                      for e in user_emails]

        PhoneFormSet = formset_factory(PhoneForm, formset=BasePhoneFormSet, min_num=1, extra=0)
        user_phone_numbers = supplier.phone_numbers.filter(is_deleted=False)
        phone_data = [{'phone_number': p.phone_number, 'phone_type': p.type}
                      for p in user_phone_numbers]

        email_helper = EmailFormSetHelper()
        phone_helper = PhoneFormSetHelper()

        if request.method == 'POST':
            form = SupplierForm(request.POST)
            email_formset = EmailFormSet(request.POST, prefix='fs1')
            phone_formset = PhoneFormSet(request.POST, prefix='fs2')

            if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
                company_name = form.cleaned_data['company_name']
                address = form.cleaned_data['address']
                postcode = form.cleaned_data['postcode']

                try:
                    with transaction.atomic():
                        supplier.company_name = company_name
                        supplier.address = address
                        supplier.postcode = postcode

                        supplier.save()

                        old_emails = supplier.emails.all()
                        print(old_emails)
                        for e in old_emails:
                            e.is_deleted = True
                            e.save()

                        for email_form in email_formset:
                            email_address = email_form.cleaned_data.get('email_address')
                            email_type = email_form.cleaned_data.get('email_type')

                            if email_address and email_type:
                                email = EmailModel.objects.get_or_create(type=email_type, address=email_address)
                                email = email[0]
                                if email.is_deleted is True:
                                    email.is_deleted = False
                                    email.save()
                                supplier.emails.add(email)
                                supplier.save()

                        old_phones = supplier.phone_numbers.all()
                        for p in old_phones:
                            p.is_deleted = True
                            p.save()

                        for phone_form in phone_formset:
                            phone_number = phone_form.cleaned_data.get('phone_number')
                            phone_type = phone_form.cleaned_data.get('phone_type')

                            if phone_number and phone_type:
                                phone = PhoneModel.objects.get_or_create(type=phone_type, phone_number=phone_number)
                                phone = phone[0]
                                if phone.is_deleted is True:
                                    phone.is_deleted = False
                                    phone.save()
                                supplier.phone_numbers.add(phone)
                                supplier.save()

                        supplier.save()

                        return HttpResponseRedirect('/thanks/')

                except IntegrityError:
                    #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
        else:
            data = {}
            data['company_name'] = supplier.company_name
            data['address'] = supplier.address
            data['postcode'] = supplier.postcode

            form = SupplierForm(initial=data)
            email_formset = EmailFormSet(initial=email_data, prefix='fs1')
            phone_formset = PhoneFormSet(initial=phone_data, prefix='fs2')

        context = {
            'form': form,
            'email_formset': email_formset,
            'phone_formset': phone_formset,
            'email_helper': email_helper,
            'phone_helper': phone_helper,
            'supplier': supplier,
        }

        return render(request, 'nod/edit_supplier.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def delete_supplier(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        # try:
        #     staff = get_object_or_404(Mechanic, uuid=uuid)
        # except ObjectDoesNotExist:
        supplier = get_object_or_404(Supplier, uuid=uuid)

        supplier.is_deleted = True
        supplier.save()

        messages.error(request, "Supplier " + supplier.company_name + " was deleted.")
        return HttpResponseRedirect('/garits/suppliers/')
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def sell_parts(request, customer_uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or\
                    request.user.staffmember.role == '2':
        # get customer from uuid. First try Dropin customer with given uuid, if not found or if multiple found,
        # check for account holder, if still not found, check business customer.
        try:
            customer = BusinessCustomer.objects.get(uuid=customer_uuid, is_deleted=False)
        except ObjectDoesNotExist:
            try:
                customer = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
            except ObjectDoesNotExist:
                try:
                    customer = Dropin.objects.get(uuid=customer_uuid, is_deleted=False)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    pass # TODO: get last one?
            except MultipleObjectsReturned:
                pass
        except MultipleObjectsReturned:
            pass

        PartCreateFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
        parts_data = []

        part_helper = PartFormSetHelper()

        if request.method == 'POST':
            part_formset = PartCreateFormSet(request.POST, prefix='fs2')
            form = CustomerPartsOrderForm(request.POST)

            if form.is_valid() and part_formset.is_valid():
                date = form.cleaned_data['date']

                try:
                    with transaction.atomic():

                        order = CustomerPartsOrder.objects.create(date=date, content_object=customer)
                        customer.part_orders.add(order)
                        customer.save()

                        last_id = Invoice.objects.last().id
                        new_id = last_id + 1
                        invoice = Invoice.objects.create(part_order=order, invoice_number=new_id, issue_date=date)

                        for part_form in part_formset:
                            part_name = part_form.cleaned_data['part_name']
                            quantity = part_form.cleaned_data['quantity']

                            if part_name and quantity:
                                part = get_object_or_404(Part, name=part_name)
                                part_sold = SellPart.objects.create(part=part, quantity=quantity, order=order)
                                invoice.parts_sold.add(part_sold)
                                #TODO: don't allow to drop below 0. and raise error if drops below threshold.
                                part.quantity -= quantity
                                part.save()

                        invoice.save()

                        messages.success(request, "Parts sold! Invoice created!")
                        return redirect('view-customer', uuid=customer.uuid)

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            data = {}
            data['date'] = timezone.datetime.now()
            part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')
            form = CustomerPartsOrderForm(initial=data)

        context = {
            'part_formset': part_formset,
            'part_helper': part_helper,
            'form': form,
            'customer': customer
        }

        return render(request, 'nod/sell_parts.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def create_user(request):
    if request.user.staffmember.role == '5':
        if request.method == 'POST':
            form = UserForm(request.POST)

            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['user_name']
                role = form.cleaned_data['role']
                hourly_rate = form.cleaned_data['hourly_rate']
                password = form.cleaned_data['password']

                # TODO: superuser if admin??
                # TODO: specify permissions
                user = User.objects.create(first_name=first_name, last_name=last_name, username=username)
                user.set_password(password)
                user.save()
                # mechanic or foreperson
                if role == '1' or role == '2':
                    Mechanic.objects.create(user=user, role=role, hourly_pay=hourly_rate)
                else:
                    StaffMember.objects.create(user=user, role=role)

                return HttpResponseRedirect('/garits/users/')

        else:
            form = UserForm()

        return render(request, 'nod/create_user.html', {'form': form})
    else:
        messages.error(request, "You must be Admin in order to view this page.")
        return redirect('/garits/')


@login_required
def edit_user(request, uuid):
    if request.user.staffmember.role == '5':
        # try:
        # staff = get_object_or_404(Mechanic, uuid=uuid)
        # except ObjectDoesNotExist:
        staff = get_object_or_404(StaffMember, uuid=uuid)
        if staff.role == '1' or staff.role == '2':
            staff = get_object_or_404(Mechanic, uuid=uuid)

        if request.method == 'POST':
            form = UserForm(request.POST)

            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['user_name']
                role = form.cleaned_data['role']
                hourly_rate = form.cleaned_data['hourly_rate']
                password = form.cleaned_data['password']

                # TODO: superuser if admin??
                # TODO: specify permissions
                staff.user.first_name = first_name
                staff.user.last_name = last_name
                if password is not "":
                    staff.user.set_password(password)
                staff.user.username = username
                staff.user.save()
                # mechanic or foreperson
                if staff.role == '1' or staff.role == '2':
                    staff = get_object_or_404(Mechanic, uuid=uuid)
                    if role == '1' or role == '2':
                        staff.hourly_pay = hourly_rate
                        staff.role = role
                    else:
                        staff = staff.staffmember_ptr
                else:
                    if role == '1' or role == '2':
                        if Mechanic.objects.get(staffmember_ptr_id=staff.id):
                            Mechanic.objects.get(staffmember_ptr_id=staff.id).delete()
                        staff = Mechanic.objects.get_or_create(staffmember_ptr_id=staff.id, hourly_pay=hourly_rate, user_id=staff.user_id,
                                                        created=staff.created)
                        staff = staff[0]

                staff.role = role
                staff.save()

                return HttpResponseRedirect('/garits/users/')

        else:
            data = {}
            data['first_name'] = staff.user.first_name
            data['last_name'] = staff.user.last_name
            data['user_name'] = staff.user.username
            if staff.role == '1' or staff.role == '2':
                data['hourly_rate'] = staff.hourly_pay
            data['role'] = staff.role
            form = UserForm(initial=data)

        context = {
            'form': form,
            'staff': staff
        }

        return render(request, 'nod/edit_user.html', context)
    else:
        messages.error(request, "How'd you even get this far without being admin?")
        return redirect('/garits/')


@login_required
def delete_user(request, uuid):
    if request.user.staffmember.role == '5':
        staff = get_object_or_404(StaffMember, uuid=uuid)

        staff.is_deleted = True
        staff.save()

        messages.error(request, "User " + staff.user.first_name + " " + staff.user.last_name + " was deleted.")
        return HttpResponseRedirect('/garits/users/')
    else:
        messages.error(request, "Impossibru.")
        return redirect('/garits/')


@login_required
def price_control(request):
    if request.user.staffmember.role == '5':
        control = PriceControl.objects.get()

        if request.method == 'POST':
            form = PriceControlForm(request.POST)

            if form.is_valid():
                vat = form.cleaned_data['vat']
                marked_up = form.cleaned_data['marked_up']

                control.vat = vat
                control.marked_up = marked_up
                control.save()

                return HttpResponseRedirect('/thanks/')

        else:
            data = {}
            data['vat'] = control.vat
            data['marked_up'] = control.marked_up
            form = PriceControlForm(initial=data)

        context = {
            'form': form,
        }

        return render(request, 'nod/price_control.html', context)
    else:
        messages.error(request, "Impossibru.")
        return redirect('/garits/')


@login_required
def view_invoice(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        invoice = get_object_or_404(Invoice, uuid=uuid)
        if invoice.job_done:
            job = invoice.job_done
            customer = invoice.get_customer()
            vehicle = invoice.job_done.vehicle
            mechanic = invoice.job_done.mechanic
            if invoice.reminder_phase == '1':
                template = loader.get_template('nod/view_invoice.html')
            else:
                if invoice.reminder_phase == '2':
                    template = loader.get_template('nod/view_invoice_reminder_1.html')
                else:
                    if invoice.reminder_phase == '3':
                        template = loader.get_template('nod/view_invoice_reminder_2.html')
                    else:
                        template = loader.get_template('nod/view_invoice_reminder_final.html')
            context = RequestContext(request, {
                'invoice': invoice,
                'job': job,
                'customer': customer,
                'vehicle': vehicle,
                'mechanic': mechanic,
            })
            return HttpResponse(template.render(context))
        else:
            if invoice.part_order:
                order = invoice.part_order
                customer = invoice.get_customer()
                if invoice.reminder_phase == '1':
                    template = loader.get_template('nod/view_invoice_parts.html')
                else:
                    if invoice.reminder_phase == '2':
                        template = loader.get_template('nod/view_invoice_reminder_1_parts.html')
                    else:
                        if invoice.reminder_phase == '3':
                            template = loader.get_template('nod/view_invoice_reminder_2_parts.html')
                        else:
                            template = loader.get_template('nod/view_invoice_reminder_final_parts.html')
                context = RequestContext(request, {
                    'invoice': invoice,
                    'order': order,
                    'customer': customer,
                })
                return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def view_invoice_reminder1(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        invoice = get_object_or_404(Invoice, uuid=uuid)
        invoice_reminder = get_object_or_404(InvoiceReminder, invoice=invoice, reminder_phase='2')
        job = invoice.job_done
        customer = invoice.get_customer()
        vehicle = invoice.job_done.vehicle

        if invoice_reminder.reminder_phase == '2':
            pass
        else:
            messages.error(request, "reminder doesn't exist")
            return redirect('/garits/')

        template = loader.get_template('nod/view_invoice_reminder_1.html')

        context = RequestContext(request, {
            'invoice': invoice,
            'reminder': invoice_reminder,
            'job': job,
            'customer': customer,
            'vehicle': vehicle,
        })
        return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def view_invoice_reminder2(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        invoice = get_object_or_404(Invoice, uuid=uuid)
        invoice_reminder = get_object_or_404(InvoiceReminder, invoice=invoice, reminder_phase='3')
        job = invoice.job_done
        customer = invoice.get_customer()
        vehicle = invoice.job_done.vehicle
        if invoice_reminder.reminder_phase == '3':
            pass
        else:
            messages.error(request, "reminder doesn't exist")

        template = loader.get_template('nod/view_invoice_reminder_2.html')

        context = RequestContext(request, {
            'invoice': invoice,
            'reminder': invoice_reminder,
            'job': job,
            'customer': customer,
            'vehicle': vehicle,
        })
        return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def view_invoice_reminder3(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        invoice = get_object_or_404(Invoice, uuid=uuid)
        invoice_reminder = get_object_or_404(InvoiceReminder, invoice=invoice, reminder_phase='4')
        job = invoice.job_done
        customer = invoice.get_customer()
        vehicle = invoice.job_done.vehicle
        if invoice_reminder.reminder_phase == '4':
            pass
        else:
            messages.error(request, "reminder doesn't exist")
            return redirect('/garits/')

        template = loader.get_template('nod/view_invoice_reminder3.html')

        context = RequestContext(request, {
            'invoice': invoice,
            'reminder': invoice_reminder,
            'job': job,
            'customer': customer,
            'vehicle': vehicle,
        })
        return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def pay_invoice(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        invoice = get_object_or_404(Invoice, uuid=uuid)
        customer = invoice.get_customer()
        if request.method == 'POST':
            form = PaymentForm(request.POST)

            if form.is_valid():
                amount = form.cleaned_data['amount']
                date = form.cleaned_data['date']
                payment_type = form.cleaned_data['payment_type']
                last_4_digits = form.cleaned_data['last_4_digits']
                cvv = form.cleaned_data['cvv']

                try:
                    with transaction.atomic():
                        if payment_type == '2':
                            if last_4_digits and cvv:
                                Card.objects.create(amount=amount, date=date, payment_type=payment_type, last_4_digits=last_4_digits,
                                                    cvv=cvv, invoice=invoice)
                            else:
                                raise forms.ValidationError(
                                    'No card details filled.',
                                    code='card_details_missing'
                                )
                        else:
                            Payment.objects.create(amount=amount, date=date, payment_type=payment_type, invoice=invoice)

                        invoice.paid = True
                        invoice.save()

                        try:
                            if customer.suspended:
                                if len(customer.get_unpaid_invoices()) < 0:
                                    for invoice in customer.get_unpaid_invoices():
                                        if invoice.reminder_phase == '4' or invoice.issue_date <= (datetime.date.today() - relativedelta(months=3, weeks=1)):
                                            customer.suspended = True
                                            break
                                        else:
                                            customer.suspended = False
                                else:
                                    customer.suspended = False
                            customer.save()
                        except AttributeError:
                            pass

                        messages.success(request, "Invoice No. " + str(invoice.invoice_number) + " was paid.")
                        return HttpResponseRedirect("nod/print_invoice.html")

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            data = {}
            data['amount'] = invoice.total_price()
            form = PaymentForm(initial=data)

        context = {
            'form': form,
            'invoice': invoice,
            'customer': customer,
        }

        return render(request, 'nod/pay_invoice.html', context)
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def create_payment(request, job_uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or\
                    request.user.staffmember.role == '2':
        job = get_object_or_404(Job, uuid=job_uuid)
        if request.method == 'POST':
            form = PaymentForm(request.POST)

            if form.is_valid():
                amount = form.cleaned_data['amount']
                date = form.cleaned_data['date']
                payment_type = form.cleaned_data['payment_type']
                last_4_digits = form.cleaned_data['last_4_digits']
                cvv = form.cleaned_data['cvv']

                try:
                    with transaction.atomic():
                        if payment_type == '2':
                            if last_4_digits and cvv:
                                Card.objects.create(amount=amount, date=date, payment_type=payment_type, last_4_digits=last_4_digits,
                                                    cvv=cvv, job=job)
                            else:
                                raise forms.ValidationError(
                                    'No card details filled.',
                                    code='card_details_missing'
                                )
                        else:
                            Payment.objects.create(amount=amount, date=date, payment_type=payment_type, job=job)

                        job.invoice.paid = True
                        job.invoice.save()

                        return HttpResponseRedirect('/thanks/')

                except IntegrityError:
                    messages.error(request, "There was an error saving")

        else:
            data = {}
            form = PaymentForm()

        context = {
            'form': form,
            'job': job,
        }

        return render(request, 'nod/create_payment.html', context)
    else:
        messages.error(request, "You must be a franchisee/foreperson/receptionist in order to view this page.")
        return redirect('/garits/')


@login_required
def generate_invoice_for_job(request, job_uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        job = get_object_or_404(Job, uuid=job_uuid)

        last_id = Invoice.objects.last().id
        new_id = last_id + 1
        invoice = Invoice.objects.create(invoice_number=new_id, job_done=job)

        for p in job.jobpart_set.filter(is_deleted=False):
            invoice.parts_for_job.add(p)

        invoice.save()

        context = {
            'invoice': invoice,
            'job': job,
        }

        return redirect('invoice')
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def spare_parts_report_table(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        spare_parts_report_table = SparePartsReportTable(SparePartsReport.objects.filter(is_deleted=False))
        RequestConfig(request).configure(spare_parts_report_table)
        return render(request, "nod/spare_parts_reports.html", {'reports_table': spare_parts_report_table})
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')


@login_required
def generate_spare_parts_report(request):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        month = datetime.date.today().month
        year = datetime.date.today().year

        date = datetime.date(year, month, 1)
        today = datetime.date.today()
        report = SparePartsReport.objects.create(start_date=date, end_date=today, date=today)

        for part in Part.objects.filter(is_deleted=False):
            spare = SparePart.objects.create(report=report, part=part, new_stock_level=part.quantity)
            delivered = 0
            for p in OrderPartRelationship.objects.filter(part=part, order__date__gte=report.start_date):
                delivered += p.quantity
            spare.delivery = delivered

            used = 0
            for p in JobPart.objects.filter(part=part, job__booking_date__gte=report.start_date):
                used += p.quantity
            for p in SellPart.objects.filter(part=part, order__date__gte=report.start_date):
                used +=p.quantity
            spare.used = used

            spare.initial_stock_level = spare.new_stock_level + spare.used - spare.delivery
            spare.save()

        view_spare_parts_report(request, report.uuid)
    #     template = loader.get_template('nod/view_spare_parts_report.html')
    #     context = RequestContext(request, {
    #         'report': report,
    #     })
    #
    #     return HttpResponse(template.render(context))
    # else:
    #     messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
    #     return redirect('/garits/')


@login_required
def view_spare_parts_report(request, uuid):
    if request.user.staffmember.role == '3' or request.user.staffmember.role == '4' or \
                    request.user.staffmember.role == '2':
        report = get_object_or_404(SparePartsReport, uuid=uuid)

        template = loader.get_template('nod/view_spare_parts_report.html')
        context = RequestContext(request, {
            'report': report,
        })
        return HttpResponse(template.render(context))
    else:
        messages.error(request, "You must be a franchisee/receptionist/foreperson in order to view this page.")
        return redirect('/garits/')
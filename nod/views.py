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

# london_tz = pytz.timezone("Europe/London")

from .forms import *
from .models import *


def index(request):
    return render(request, "nod/base.html")

@login_required
def create_job(request):
    TaskCreateFormSet = formset_factory(JobCreateTaskForm, formset=BaseJobTaskCreateForm)
    tasks_data = []

    PartCreateFormSet = formset_factory(JobPartForm, formset=BaseJobPartForm)
    parts_data = []

    task_helper = TaskFormSetHelper()
    part_helper = PartFormSetHelper()
    print("a")

    if request.method == 'POST':
        print("b")
        form = JobCreateForm(request.POST)
        task_formset = TaskCreateFormSet(request.POST, prefix='fs1')
        part_formset = PartCreateFormSet(request.POST, prefix='fs2')

        if form.is_valid() and task_formset.is_valid() and part_formset.is_valid():
            print("c")
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


                    for part_form in part_formset:
                        part_name = part_form.cleaned_data['part_name']
                        quantity = part_form.cleaned_data['quantity']

                        if part_name and quantity:
                            part = get_object_or_404(Part, name=part_name)

                            # checks that the quantity required is not more than the total quantity in stock.
                            # if it is, it removes the quantity used for a job from the total quantity and,
                            # creates a job part object, otherwise, it throws an error.
                            # TODO: do something to warn if drops below threshold
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
        last_id = Job.objects.last().id
        new_id = last_id + 1
        data['job_number'] = new_id
        form = JobCreateForm(initial=data)
        task_formset = TaskCreateFormSet(initial=tasks_data, prefix='fs1')
        part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')

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


def delete_job(request, uuid):
    job = get_object_or_404(Job, uuid=uuid)

    job.is_deleted = True
    job.save()

    return HttpResponseRedirect('/deleted/')


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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        dropin = Dropin.objects.create()
        form = DropinForm()
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


@login_required
def edit_dropin(request, uuid):
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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
    else:
        data = {}
        data['forename'] = dropin.forename
        data['surname'] = dropin.surname
        data['date'] = dropin.date.strftime('%d/%m/%Y')

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


@login_required
def create_account_holder(request):
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

        try:
            account_holder = AccountHolder.objects.get(uuid=customer_uuid, is_deleted=False)
        except MultipleObjectsReturned:
            pass
        except ObjectDoesNotExist:
            pass

        if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
            forename = form.cleaned_data['forename']
            surname = form.cleaned_data['surname']
            date = form.cleaned_data['date']
            address = form.cleaned_data['address']
            postcode = form.cleaned_data['postcode']
            discount_plan = form.cleaned_data['discount_plan']

            # create Account Holder Customer object using input data
            # account_holder = AccountHolder.objects.create(forename=forename, surname=surname, date=date,
            #                                               address=address, postcode=postcode,
            #                                               discount_plan=discount_plan)
            try:
                with transaction.atomic():
                    account_holder.forename = forename
                    account_holder.surname = surname
                    account_holder.date = date
                    account_holder.address = address
                    account_holder.postcode = postcode
                    account_holder.discount_plan = discount_plan

                    account_holder.save()

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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        account_holder = AccountHolder.objects.create()
        form = AccountHolderForm()
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


@login_required
def edit_account_holder(request, uuid):
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

    if request.method == 'POST':
        form = AccountHolderForm(request.POST)
        email_formset = EmailFormSet(request.POST, prefix='fs1')
        phone_formset = PhoneFormSet(request.POST, prefix='fs2')

        if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
            forename = form.cleaned_data['forename']
            surname = form.cleaned_data['surname']
            date = form.cleaned_data['date']
            address = form.cleaned_data['address']
            postcode = form.cleaned_data['postcode']
            discount_plan = form.cleaned_data['discount_plan']

            try:
                with transaction.atomic():
                    account_holder.forename = forename
                    account_holder.surname = surname
                    account_holder.date = date
                    account_holder.address = address
                    account_holder.postcode = postcode
                    account_holder.discount_plan = discount_plan

                    account_holder.save()

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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
    else:
        data = {}
        data['forename'] = account_holder.forename
        data['surname'] = account_holder.surname
        data['date'] = account_holder.date.strftime('%d/%m/%Y')
        data['address'] = account_holder.address
        data['postcode'] = account_holder.postcode
        data['discount_plan'] = account_holder.discount_plan

        form = DropinForm(initial=data)
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


@login_required
def create_business_customer(request):
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
            discount_plan = form.cleaned_data['discount_plan']

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
                    business_customer.discount_plan = discount_plan

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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        business_customer = BusinessCustomer.objects.create()
        form = BusinessCustomerForm()
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


@login_required
def edit_business_customer(request, uuid):
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
            discount_plan = form.cleaned_data['discount_plan']

            try:
                with transaction.atomic():
                    business_customer.company_name = company_name
                    business_customer.forename = forename
                    business_customer.surname = surname
                    business_customer.rep_role = rep_role
                    business_customer.date = date
                    business_customer.address = address
                    business_customer.postcode = postcode
                    business_customer.discount_plan = discount_plan

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

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
    else:
        data = {}
        data['company_name'] = business_customer.company_name
        data['forename'] = business_customer.forename
        data['surname'] = business_customer.surname
        data['rep_role'] = business_customer.rep_role
        data['date'] = business_customer.date.strftime('%d/%m/%Y')
        data['address'] = business_customer.address
        data['postcode'] = business_customer.postcode
        data['discount_plan'] = business_customer.discount_plan

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


def delete_customer(request, uuid):
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

    return HttpResponseRedirect('/deleted/')


def create_vehicle(request, customer_uuid):
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


def edit_vehicle(request, customer_uuid, uuid):
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

            return HttpResponseRedirect('/thanks/')
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


def delete_vehicle(request, uuid):
    vehicle = get_object_or_404(Vehicle, uuid=uuid)

    vehicle.is_deleted = True
    vehicle.save()

    return HttpResponseRedirect('/deleted/')


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


def create_part(request):
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

            return HttpResponseRedirect('/thanks/')

    else:
        form = CreatePartForm()

    return render(request, 'nod/create_part.html', {'form': form})


def edit_part(request, uuid):
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

            return HttpResponseRedirect('/thanks/')

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


def delete_part(request, uuid):
    part = get_object_or_404(Part, uuid=uuid)

    part.is_deleted = True
    part.save()

    return HttpResponseRedirect('/deleted/')


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


def replenish_stock(request):
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

                    return HttpResponseRedirect('/thanks/')

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


def edit_replenish_stock(request, uuid):
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


def create_supplier(request):
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


def edit_supplier(request, uuid):
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


def create_payment(request, job_uuid):
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


def sell_parts(request, customer_uuid):
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

                    for part_form in part_formset:
                        part_name = part_form.cleaned_data['part_name']
                        quantity = part_form.cleaned_data['quantity']

                        if part_name and quantity:
                            part = get_object_or_404(Part, name=part_name)
                            part_sold = SellPart.objects.create(part=part, quantity=quantity, order=order)
                            #TODO: don't allow to drop below 0. and raise error if drops below threshold.
                            part.quantity -= quantity
                            part.save()

                    return HttpResponseRedirect('/thanks/')

            except IntegrityError:
                messages.error(request, "There was an error saving")

    else:
        part_formset = PartCreateFormSet(initial=parts_data, prefix='fs2')
        form = CustomerPartsOrderForm()

    context = {
        'part_formset': part_formset,
        'part_helper': part_helper,
        'form': form,
        'customer': customer
    }

    return render(request, 'nod/sell_parts.html', context)


def create_user(request):
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
                Mechanic.objects.create(user=user, role=role, hourly_rate=hourly_rate)
            else:
                StaffMember.objects.create(user=user, role=role)

            return HttpResponseRedirect('/thanks/')

    else:
        form = UserForm()

    return render(request, 'nod/create_user.html', {'form': form})


def edit_user(request, uuid):
    # try:
    # staff = get_object_or_404(Mechanic, uuid=uuid)
    # except ObjectDoesNotExist:
    staff = get_object_or_404(StaffMember, uuid=uuid)

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
                if role == '1' or role == '2':
                    staff.hourly_pay = hourly_rate
                    staff.role = role
                else:
                    staff.hourly_pay = None
            else:
                if role == '1' or role == '2':
                    staff.hourly_pay = hourly_rate

            staff.role = role
            staff.save()

            return HttpResponseRedirect('/thanks/')

    else:
        data = {}
        data['first_name'] = staff.user.first_name
        data['last_name'] = staff.user.last_name
        data['user_name'] = staff.user.username
        try:
            data['hourly_rate'] = staff.hourly_rate
        except AttributeError:
            pass
        data['role'] = staff.role
        form = UserForm(initial=data)

    context = {
        'form': form,
        'staff': staff
    }

    return render(request, 'nod/edit_user.html', context)

def delete_user(request, uuid):
    # try:
    #     staff = get_object_or_404(Mechanic, uuid=uuid)
    # except ObjectDoesNotExist:
    staff = get_object_or_404(StaffMember, uuid=uuid)

    staff.is_deleted = True
    staff.save()

    return HttpResponseRedirect('/deleted/')


def price_control(request):
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
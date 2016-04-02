from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/edit/$', views.edit_profile, name='edit-profile'),
    url(r'^jobs/create/$', views.create_job, name='create-job'),
    url(r'^jobs/(?P<uuid>\w+)/edit/$', views.edit_job, name='edit-job'),
    url(r'^customers/dropin/create/$', views.create_dropin, name='create-dropin'),
    url(r'^customers/dropin/(?P<uuid>\w+)/edit/$', views.edit_dropin, name='edit-dropin'),
    url(r'^customers/account_holder/create/$', views.create_account_holder, name='create-account-holder'),
    url(r'^customers/account_holder/(?P<uuid>\w+)/edit/$', views.edit_account_holder, name='edit-account-holder'),
    url(r'^customers/business_customer/create/$', views.create_business_customer, name='create-business-customer'),
    url(r'^customers/business_customer/(?P<uuid>\w+)/edit/$', views.edit_business_customer, name='edit-business-customer'),
]
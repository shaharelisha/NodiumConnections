from django.conf.urls import url

from nod import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/edit/$', views.edit_profile, name='edit-profile'),
    url(r'^jobs/pending/$', views.untaken_jobs_table, name='untaken-jobs'),
    url(r'^jobs/active/$', views.active_jobs_table, name='active-jobs'),
    url(r'^jobs/paused/$', views.paused_jobs_table, name='paused-jobs'),
    url(r'^jobs/create/$', views.create_job, name='create-job'),
    url(r'^jobs/(?P<uuid>\w+)/edit/$', views.edit_job, name='edit-job'),
    # TODO: make only available to foreperson
    # url(r'^jobs/(?P<uuid>\w+)/edit/assign/$', views.assign_mechanic_job, name='assign-mechanic-job'),
    url(r'^jobs/(?P<job_uuid>\w+)/payment/$', views.create_payment, name='create-payment'),
    url(r'^parts/$', views.part_table, name='parts'),
    url(r'^parts/create/$', views.create_part, name='create-part'),
    url(r'^parts/(?P<uuid>\w+)/edit/$', views.edit_part, name='edit-part'),
    url(r'^customers/dropin/$', views.dropin_table, name='dropins'),
    url(r'^customers/dropin/create/$', views.create_dropin, name='create-dropin'),
    url(r'^customers/dropin/(?P<uuid>\w+)/$', views.view_dropin, name='view-dropin'),
    url(r'^customers/dropin/(?P<uuid>\w+)/edit/$', views.edit_dropin, name='edit-dropin'),
    url(r'^customers/account_holders/$', views.account_holder_table, name='account-holders'),
    url(r'^customers/account_holders/create/$', views.create_account_holder, name='create-account-holder'),
    url(r'^customers/account_holders/(?P<uuid>\w+)/edit/$', views.edit_account_holder, name='edit-account-holder'),
    url(r'^customers/business_customer/$', views.business_customers_table, name='business-customers'),
    url(r'^customers/business_customer/create/$', views.create_business_customer, name='create-business-customer'),
    url(r'^customers/business_customer/(?P<uuid>\w+)/edit/$', views.edit_business_customer, name='edit-business-customer'),
    url(r'^customers/(?P<customer_uuid>\w+)/vehicle/create/$', views.create_vehicle, name='create-vehicle'),
    url(r'^customers/(?P<customer_uuid>\w+)/vehicle/(?P<uuid>\w+)/edit/$', views.edit_vehicle, name='edit-vehicle'),
    url(r'^customers/(?P<customer_uuid>\w+)/sell_parts/$', views.sell_parts, name='sell-parts'),
    url(r'^customers/(?P<uuid>\w+)/$', views.view_customer, name='view-customer'),
    url(r'^invoices/(?P<uuid>\w+)/pay/$', views.pay_invoice, name='pay-invoice'),
    url(r'^invoices/(?P<uuid>\w+)/$', views.view_invoice, name='view-invoice'),
    url(r'^invoices/(?P<uuid>\w+)/reminder1/$', views.view_invoice_reminder1, name='view-invoice-reminder1'),
    url(r'^invoices/(?P<uuid>\w+)/reminder2/$', views.view_invoice_reminder2, name='view-invoice-reminder2'),
    url(r'^invoices/(?P<uuid>\w+)/reminder3/$', views.view_invoice_reminder3, name='view-invoice-reminder3'),
    url(r'^api/get_vehicles/(?P<customer_uuid>\w+)/$', views.get_vehicles, name='get-vehicles'),
    url(r'^api/get_vehicles/', views.get_vehicles_autocomplete, name='get-vehicles-autocomplete'),
    url(r'^delete/job/(?P<uuid>\w+)/$', views.delete_job, name='delete-job'),
    url(r'^delete/vehicle/(?P<uuid>\w+)/$', views.delete_vehicle, name='delete-vehicle'),
    url(r'^delete/customers/(?P<uuid>\w+)/$', views.delete_customer, name='delete-customer'),
    url(r'^delete/part/(?P<uuid>\w+)/$', views.delete_part, name='delete-part'),
    url(r'^delete/users/(?P<uuid>\w+)/$', views.delete_user, name='delete-user'),
    url(r'^delete/suppliers/(?P<uuid>\w+)/$', views.delete_supplier, name='delete-supplier'),
    url(r'^replenishment_order/place_order/$', views.replenish_stock, name='replenish-order'),
    url(r'^replenishment_order/(?P<uuid>\w+)/edit/$', views.edit_replenish_stock, name='edit-replenish-order'),
    url(r'^api/get_suppliers/', views.get_suppliers_autocomplete, name='get-suppliers-autocomplete'),
    url(r'^suppliers/$', views.supplier_table, name='suppliers'),
    url(r'^suppliers/create/$', views.create_supplier, name='create-supplier'),
    url(r'^suppliers/(?P<uuid>\w+)/edit/$', views.edit_supplier, name='edit-supplier'),
    url(r'^users/$', views.user_table, name='users'),
    url(r'^users/create/$', views.create_user, name='create-user'),
    url(r'^users/(?P<uuid>\w+)/edit/$', views.edit_user, name='edit-user'),
    url(r'^price_control/$', views.price_control, name='price-control'),
    url(r'^spare_parts_reports/$', views.spare_parts_report_table, name='spare-parts-report'),
    url(r'^spare_parts_reports/create/new/$', views.generate_spare_parts_report, name='generate-spare-parts-report'),
    url(r'^spare_parts_reports/(?P<uuid>\w+)/$', views.view_spare_parts_report, name='view-spare-parts-report'),
    url(r'^time_reports/$', views.time_report_table, name='time-report'),
    url(r'^time_reports/create/new/$', views.generate_time_report, name='generate-time-report'),
    url(r'^time_reports/(?P<uuid>\w+)/$', views.view_time_report, name='view-time-report'),
    url(r'^mot_reminders/(?P<uuid>\w+)/$', views.view_mot_reminder, name='view-mot-reminder'),
]
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/edit/$', views.edit_profile, name='edit-profile'),
    url(r'^jobs/create/$', views.create_job, name='create-job'),
    url(r'^jobs/(?P<uuid>\w+)/edit/$', views.edit_job, name='edit-job'),
    url(r'^jobs/(?P<job_uuid>\w+)/payment/$', views.create_payment, name='create-payment'),
    url(r'^parts/$', views.part_table, name='parts'),
    url(r'^parts/create/$', views.create_part, name='create-part'),
    url(r'^parts/(?P<uuid>\w+)/edit/$', views.edit_part, name='edit-part'),
    url(r'^customers/$', views.customer_tables, name='customers'),
    url(r'^customers/dropin/create/$', views.create_dropin, name='create-dropin'),
    url(r'^customers/dropin/(?P<uuid>\w+)/edit/$', views.edit_dropin, name='edit-dropin'),
    url(r'^customers/account_holder/create/$', views.create_account_holder, name='create-account-holder'),
    url(r'^customers/account_holder/(?P<uuid>\w+)/edit/$', views.edit_account_holder, name='edit-account-holder'),
    url(r'^customers/business_customer/create/$', views.create_business_customer, name='create-business-customer'),
    url(r'^customers/business_customer/(?P<uuid>\w+)/edit/$', views.edit_business_customer, name='edit-business-customer'),
    url(r'^customers/(?P<customer_uuid>\w+)/vehicle/create/$', views.create_vehicle, name='create-vehicle'),
    url(r'^customers/(?P<customer_uuid>\w+)/vehicle/(?P<uuid>\w+)/edit/$', views.edit_vehicle, name='edit-vehicle'),
    url(r'^customers/(?P<customer_uuid>\w+)/sell_parts/$', views.sell_parts, name='sell-parts'),
    url(r'^api/get_vehicles/(?P<customer_uuid>\w+)/$', views.get_vehicles, name='get-vehicles'),
    url(r'^api/get_vehicles/', views.get_vehicles_autocomplete, name='get-vehicles-autocomplete'),
    url(r'^delete/job/(?P<uuid>\w+)/$', views.delete_job, name='delete-job'),
    url(r'^delete/vehicle/(?P<uuid>\w+)/$', views.delete_vehicle, name='delete-vehicle'),
    url(r'^delete/customers/(?P<uuid>\w+)/$', views.delete_customer, name='delete-customer'),
    url(r'^delete/part/(?P<uuid>\w+)/$', views.delete_part, name='delete-part'),
    url(r'^delete/users/(?P<uuid>\w+)/$', views.delete_user, name='delete-user'),
    url(r'^replenishment_order/place_order/$', views.replenish_stock, name='replenish-order'),
    url(r'^replenishment_order/(?P<uuid>\w+)/edit/$', views.edit_replenish_stock, name='edit-replenish-order'),
    url(r'^api/get_suppliers/', views.get_suppliers_autocomplete, name='get-suppliers-autocomplete'),
    url(r'^suppliers/create/$', views.create_supplier, name='create-supplier'),
    url(r'^suppliers/(?P<uuid>\w+)/edit/$', views.edit_supplier, name='edit-supplier'),
    url(r'^users/$', views.user_table, name='users'),
    url(r'^users/create/$', views.create_user, name='create-user'),
    url(r'^users/(?P<uuid>\w+)/edit/$', views.edit_user, name='edit-user'),
    url(r'^price_control/$', views.price_control, name='price-control'),




]
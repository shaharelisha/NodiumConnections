from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^jobs/create/$', views.create_job, name='create-job'),
    url(r'^jobs/(?P<uuid>\w+)/edit/$', views.edit_job, name='edit-job'),
]
from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search),
    url(r'^.+/$', views.details, name='details'),
]
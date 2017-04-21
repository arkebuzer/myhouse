from django.conf.urls import url

from . import views

app_name = 'meteo'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<time_delta>month)$', views.index, name='month'),
    url(r'^(?P<time_delta>day)$', views.index, name='day'),
    url(r'^(?P<time_delta>hour)$', views.index, name='hour')
]

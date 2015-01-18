from django.conf.urls import patterns, url
from motionSound import views

urlpatterns = patterns('',
  # /motionSound/
  url(r'^$', views.index, name='index'),
  # /motionSound/log/
  url(r'^log/$', views.log, name="log"),
  # /motionSoun/config/
  url(r'^config/$', views.config, name="config")
)

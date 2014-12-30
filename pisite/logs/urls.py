from django.conf.urls import patterns, url
from logs import views

urlpatterns = patterns('',
  # /logs/
  url(r'^$', views.index, name='index'),
  # /logs/logname
  url(r'^(?P<logName>\S+)/$', views.log, name="individualLog")
)
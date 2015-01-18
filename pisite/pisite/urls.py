from django.conf.urls import patterns, include, url
from django.contrib import admin

from home import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pisite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^logs/', include('logs.urls', namespace="logs")),
    url(r'^motionSound/', include('motionSound.urls', namespace="motionSound")),
    url(r'^admin/', include(admin.site.urls)),

    # Pages within the home app
    #
    # Home page
    url(r'^$', views.index, name="home"),
    # Sound upload page
    #url(r'^uploadSound$', views.uploadSound, name="uploadSound")
)

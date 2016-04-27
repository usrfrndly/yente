from django.conf import settings
from django.views.generic.base import RedirectView
from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^users', 'pygrl.views.users'),
    url(r'^/?$', RedirectView.as_view(url='/index.html')),
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
from django.conf.urls import url
from core.views import (
    index, authenticate, confirm, report, complete, status
)
from account.views import (register, ping)

urlpatterns = [
    url(r'^api/$', index),
    url(r'^api/station/register$', register, name='register'),
    url(r'^api/station/ping$', ping, name='ping'),
    url(r'^api/authenticate$', authenticate, name='authenticate'),
    url(r'^api/confirm$', confirm, name='confirm'),
    url(r'^api/report$', report, name='report'),
    url(r'^api/complete$', complete, name='complete'),
    url(r'^api/status$', status, name='status'),
]

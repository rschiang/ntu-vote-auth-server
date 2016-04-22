from django.conf.urls import url
from .views import (index, authenticate, confirm, report, complete)
from account.views import (register, ping)

urlpatterns = [
    url(r'^$', index),
    url(r'^api/station/register$', register),
    url(r'^api/station/ping$', ping),
    url(r'^api/authenticate$', authenticate),
    url(r'^api/confirm$', confirm),
    url(r'^api/report$', report),
    url(r'^api/complete$', complete, name='callback'),
]

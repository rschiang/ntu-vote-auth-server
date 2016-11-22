from django.conf.urls import url, include
from core.views import (
    index, authenticate, confirm, report, complete
)
from account.views import (register, ping)
from staff.views import status

urlpatterns = [
    url(r'^api/$', index),

    # general G series
    url(r'^api/general/', include([
        url(r'^register$', register, name='register'),
        url(r'^ping$', ping, name='ping'),
    ])),

    # A series
    url(r'^api/elector/', include([
        url(r'^authenticate$', authenticate, name='authenticate'),
        url(r'^confirm$', confirm, name='confirm'),
        url(r'^reject$', report, name='report'),
        url(r'^complete$', complete, name='callback'),
    ])),
    # R
    url(r'^api/reset/', include([
    ])),
    # C
    url(r'^api/entry/', include([
    ])),
    # T
    url(r'^api/test/', include([
    ])),
    # M
    url(r'^api/status$', status, name='status'),
]

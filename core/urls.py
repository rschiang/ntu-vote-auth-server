from django.conf.urls import url, include
from core.views import (
    index, authenticate, confirm, report, complete
)
from account.views import (register, ping)
from staff.views import status

urlpatterns = [
    url(r'^api/', include([
        url(r'^$', index),

        # general G series
        url(r'^general/', include([
            url(r'^register$', register, name='register'),
            url(r'^ping$', ping, name='ping'),
        ], namespace='general')),

        # A series
        url(r'^elector/', include([
            url(r'^authenticate$', authenticate, name='authenticate'),
            url(r'^confirm$', confirm, name='confirm'),
            url(r'^reject$', report, name='report'),
            url(r'^complete$', complete, name='callback'),
        ], namespace='elector')),
        # R
        url(r'^resets/', include([
            ], namespace='resets')),
        # C
        url(r'^entry/', include([
            ], namespace='entry')),
        # T
        url(r'^test/', include([
            ], 'test')),
        # M
        url(r'^status$', status, name='status'),
    ])),
]

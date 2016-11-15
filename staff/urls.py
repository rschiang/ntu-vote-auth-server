from django.conf.urls import url
from staff.views import (
    reset_list,
)
from account.views import (register, ping)

urlpatterns = [
    url(r'^reset/$', reset_list, name='reset_list'),
]

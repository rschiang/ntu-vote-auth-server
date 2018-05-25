import account.views as account
import core.views as core
from django.urls import include, path

api_urlpatterns = [
    # General views
    path('', core.index),
    path('version', core.version)

    # Account views
    path('account/', include([
        path('register', account.register, name='register'),
        path('ping', account.ping, name='ping'),
    ], namespace='account')),

    # Election-specific views
    path('election/<slug:name>/', include([
        # Station actions
        path('authenticate', core.authenticate, name='authenticate'),
        path('allocate', core.allocate, name='allocate'),
        path('reject', core.reject, name='reject'),
        path('cancel', core.cancel, name='cancel'),
        path('abort', core.abort, name='abort'),

        # Callback events
        path('allocated', core.allocated, name='allocated-event'),
        path('voted', core.voted, name='voted-event'),
    ], namespace='election')),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]

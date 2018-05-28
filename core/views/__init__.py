# Class-based views
from .abort import AbortView
from .allocate import AllocateView
from .authenticate import AuthenticateView
from .voted import VotedEventView
from .cancel import CancelView
from .version import VersionView

# Views
from .exception_handler import rest_exception_handler   # noqa: F401
from .index import index    # noqa: F401

abort = AbortView.as_view()
allocate = AllocateView.as_view()
authenticate = AuthenticateView.as_view()
cancel = CancelView.as_view()
version = VersionView.as_view()
voted = VotedEventView.as_view()

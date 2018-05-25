# Views
from .abort import AbortView
from .allocate import AllocateView
from .authenticate import AuthenticateView
from .cancel import CancelView
from .index import index    # noqa: F401
from .reject import RejectView
from .version import VersionView

abort = AbortView.as_view()
allocate = AllocateView.as_view()
authenticate = AuthenticateView.as_view()
cancel = CancelView.as_view()
# index = index
reject = RejectView.as_view()
version = VersionView.as_view()

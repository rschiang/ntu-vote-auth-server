# Views
from .ping import PingView
from .register import RegisterView

ping = PingView.as_view()
register = RegisterView.as_view()

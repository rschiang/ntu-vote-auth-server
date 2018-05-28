# Views
from .booth import BoothView
from .ping import PingView
from .register import RegisterView

booth = BoothView.as_view()
ping = PingView.as_view()
register = RegisterView.as_view()

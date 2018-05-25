# Views
from .index import index    # noqa: F401
from .version import VersionView

version = VersionView.as_view()

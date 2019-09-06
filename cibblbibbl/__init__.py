__version__ = "0.0.1"

# prioriy modules
from . import settings as _settings
settings = _settings.settings
loginsettings = _settings.loginsettings


from . import match

from . import tournament
tournament.init("cibbl")

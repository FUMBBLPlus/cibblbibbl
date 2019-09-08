__version__ = "0.0.1"

# prioriy modules
from . import settings as _settings
settings = _settings.settings
loginsettings = _settings.loginsettings
data_settings = _settings.data_settings
data_bibbl_settings = _settings.data_bibbl_settings
data_cibbl_settings = _settings.data_cibbl_settings


from . import team
from . import match


from . import tournament
tournament.init("cibbl")

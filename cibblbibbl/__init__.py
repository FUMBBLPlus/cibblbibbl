__version__ = "0.0.1"

# prioriy modules
from . import data
from . import settings

from . import helper


from . import coach
from . import team
from . import match


from . import tournament
tournament.init("cibbl")

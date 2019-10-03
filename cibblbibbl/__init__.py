__version__ = "0.0.1"

# prioriy modules
from . import field
from . import config
from . import data
#from . import settings

from . import helper


from . import coach
from . import team
from . import player
from . import match

from . import group
from . import year
from . import season
from . import tournament
from . import matchup

from . import achievement

CIBBL = group.Group("cibbl")

from . import admin

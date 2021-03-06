__version__ = "0.0.1"

# prioriy modules
from . import field
from . import data

from . import helper
from . import bbcode
from . import phpwikicode


from . import coach
from . import position
from . import roster
from . import team
from . import player
from . import replay
from . import match

from . import group
from . import year
from . import season
from . import tournament
from . import matchup

from . import achievement


_init_existing_players = frozenset(player.iterexisting())
CIBBL = group.Group("cibbl")

# publishment
from . import page
from . import pagetitle

# administration
from . import admin


# magic modules
from . import session as _session
session = _session.fumbbl_session

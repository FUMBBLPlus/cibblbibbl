import collections
import cibblbibbl

from . import exporttools
from .mastercls import TeamAchievement
from .tp_match import TP_Match

class TP_Admin(TeamAchievement):
    # added manually
  rank = 10
  sortrank = 10

  export_bbcode = TP_Match.export_bbcode
  export_plaintext = TP_Match.export_plaintext


cls = TP_Admin

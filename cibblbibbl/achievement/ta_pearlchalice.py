import collections
import cibblbibbl

from . import exporttools
from .mastercls import TeamAchievement
from .tp_match import TP_Match

class TA_PearlChalice(TeamAchievement):
    # added manually
  rank = 10
  sortrank = 10

  export_plaintext = TP_Match.export_plaintext


cls = TA_PearlChalice

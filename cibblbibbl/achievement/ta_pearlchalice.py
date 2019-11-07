import collections
import cibblbibbl

from . import exporttools
from .mastercls import TeamAchievement
from .ta_obsidianchalice import TA_ObsidianChalice

class TA_PearlChalice(TeamAchievement):
    # added manually
  rank = 10
  sortrank = 10

  export_plaintext = TA_ObsidianChalice.export_plaintext


cls = TA_PearlChalice

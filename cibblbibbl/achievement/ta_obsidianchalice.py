import collections
import cibblbibbl
from cibblbibbl import bbcode

from . import exporttools
from .mastercls import TeamAchievement
from .tp_match import TP_Match

class TA_ObsidianChalice(TeamAchievement):
    # added manually
  rank = 10
  sortrank = 10

  def export_bbcode(self):
    s1 = bbcode.team(self.subject)
    return s1

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    s1 = self.subject.name
    return s0 + s1


cls = TA_ObsidianChalice

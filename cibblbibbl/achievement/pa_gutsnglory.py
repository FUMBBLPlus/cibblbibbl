import collections
import cibblbibbl
from cibblbibbl import bbcode

from . import exporttools
from .mastercls import PlayerAchievement

class PA_GutsNGlory(PlayerAchievement):
    # added manually
  rank = 10
  sortrank = 1009

  def export_bbcode(self):
    team = exporttools.team(self)
    s1 = f'{bbcode.player(self.subject)} ({bbcode.team(team)})'
    s2 = exporttools.alreadyearned(self)
    return s1 + s2

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    team = exporttools.team(self)
    if hasattr(team, "name"):
      teamname = team.name
    else:
      teamname = team
    s1 = f'{self.subject.name} ({teamname})'
    s2 = exporttools.alreadyearned(self)
    return s0 + s1 + s2


cls = PA_GutsNGlory

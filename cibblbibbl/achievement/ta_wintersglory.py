import collections
import cibblbibbl
import itertools

from . import exporttools
from .mastercls import TeamAchievement


class TA_WintersGlory(TeamAchievement):

  rank = 10
  sortrank = 20

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.season.name != "Winter":
        continue
      if T.posonly == "yes":
        continue
      if T.status != "Completed":
        continue
      pposgen = itertools.chain(T.ppos, itertools.repeat(0))
      standings = T.standings()
      for i in range(C["count"]):
        try:
          d = standings[i]
        except IndexError:
          break
        Te = d["team"]
        A = cls(T, Te)
        if A["status"] == "proposed":
          A["status"] = "proposed"  # explicit
        yield A

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    s1 = str(self.subject)
    s2 = exporttools.alreadyearned(self)
    return s0 + s1 + s2


cls = TA_WintersGlory
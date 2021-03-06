import collections
import cibblbibbl
from cibblbibbl import bbcode
import itertools

from . import exporttools
from .mastercls import TeamAchievement


class TA_WintersGlory(TeamAchievement):

  rank = 10
  sortrank = 20

  @classmethod
  def agent01(cls, group):
    C = cls.defaultconfig_of_group(group)._data
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.season.name != "Winter":
        continue
      if T.posonly == "yes":
        continue
      if T.status != "Completed":
        continue
      pposgen = itertools.chain(T.ppos, itertools.repeat(0))
      standings = T.standings()
      counts = C["count"]
      count = counts.get(str(T.Id), counts["<default>"])
      for i in range(count):
        try:
          d = standings[i]
        except IndexError:
          break
        Te = d["team"]
        A = cls(T, Te)
        if A.get("status", "proposed") == "proposed":
          A["status"] = "proposed"  # explicit
        yield A

  def export_bbcode(self):
    s1 = bbcode.team(self.subject)
    s2 = exporttools.alreadyearned(self)
    return s1 + s2

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    s1 = self.subject.name
    s2 = exporttools.alreadyearned(self)
    return s0 + s1 + s2


cls = TA_WintersGlory

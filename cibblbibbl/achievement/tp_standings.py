import collections
import cibblbibbl
import itertools

from . import exporttools
from .mastercls import TeamAchievement


class TP_Standings(TeamAchievement):

  rank = 10
  sortrank = 20

  @classmethod
  def agent01(cls, group):
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.status != "Completed":
        continue
      pposgen = itertools.chain(T.ppos, itertools.repeat(0))
      standings = T.standings()
      for nr, d in enumerate(standings, 1):
        prestige = next(pposgen)
        if not prestige:
          continue
        Te = d["team"]
        if isinstance(Te, cibblbibbl.team.GroupOfTeams):
          teams = Te
        else:
          teams = (Te,)
        for Te in teams:
          A = cls(T, Te)
          if A.get("status", "proposed") == "proposed":
            A["prestige"] = prestige
            A["nr"] = nr
            A["status"] = "proposed"  # explicit
          yield A

  def export_plaintext(self, show_Ids=False):
    s0 = f'{self["nr"]:>2}. '
    s1 = exporttools.idpart(self, show_Ids)
    s2 = self.subject.name
    s3 = f' ({self.prestige(self.season)} Prestige Points)'
    return s0 + s1 + s2 + s3


cls = TP_Standings

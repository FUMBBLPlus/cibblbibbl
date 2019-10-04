import collections
import cibblbibbl
import itertools

from .mastercls import Achievement


class TP_Standings(Achievement):
  subject_type = cibblbibbl.team.Team

  @classmethod
  def agent01(cls, group_key):
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
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
          if A["status"] == "proposed":
            if prestige or A["prestige"]:
              A["prestige"] = prestige
              A["status"] = "proposed"  # explicit
          yield A


cls = TP_Standings

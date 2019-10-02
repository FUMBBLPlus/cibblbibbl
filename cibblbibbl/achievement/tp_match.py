import collections
import cibblbibbl

from .mastercls import Achievement

class TP_Match(Achievement):
  subject_type = cibblbibbl.team.Team

  @classmethod
  def agent01(cls, group_key):
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      prestiges = collections.defaultdict(lambda: 0)
      for Mu in T.matchups:
        for Te in Mu.teams:
          prestiges[Te] += Mu.performance(Te).get("prestige", 0)
      for Te, prestige in prestiges.items():
        A = cls(T, Te)
        if A["status"] == "proposed":
          if prestige or A["prestige"]:
            A["prestige"] = prestige
            A["status"] = "proposed"  # explicit; easier to edit
        yield A


cls = TP_Match

import collections
import cibblbibbl

from .mastercls import TeamAchievement

class TP_Match(TeamAchievement):

  rank = 10

  @classmethod
  def agent01(cls, group_key):
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
        # despite it should have zero prestige value too
      prestiges = collections.defaultdict(lambda: 0)
      for Mu in T.matchups:
        if Mu.excluded == "yes":
          continue
        for Te in Mu.teams:
          prestiges[Te] += Mu.performance(Te).get("prestige", 0)
      for Te, prestige in prestiges.items():
        if not prestige:
          continue
        A = cls(T, Te)
        if A["status"] == "proposed":
          A["prestige"] = prestige
          A["status"] = "proposed"  # explicit; easier to edit
        yield A


cls = TP_Match

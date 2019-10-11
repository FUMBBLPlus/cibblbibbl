import collections
import cibblbibbl

from .mastercls import TeamAchievement

class TA_CrushingVictory(TeamAchievement):

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.abstract:
        continue
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      prestiges = collections.defaultdict(lambda: 0)
      for Mu in T.matchups:
        if Mu.abstract:
          continue
        if Mu.excluded == "yes":
          continue
        teams = sorted(Mu.teams)
        for i, Te in enumerate(teams):
          tds = Mu.performance(Te).get("td", 0)
          if tds < C["mintds"]:
            continue
          oppoTe = teams[1-i]
          oppotds = Mu.performance(oppoTe).get("td", 0)
          if C["oppomaxtds"] < oppotds:
            continue
          prestiges[Te] += C["value"]
      for Te, prestige in prestiges.items():
        A = cls(T, Te)
        if A["status"] == "proposed":
          if prestige or A["prestige"]:
            A["prestige"] = prestige
            A["status"] = "proposed"  # explicit; easier to edit
        yield A


cls = TA_CrushingVictory

import collections
import cibblbibbl

from .mastercls import PlayerAchievement

class PA_Perfection(PlayerAchievement):

  rank = 10

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    value = C["value"]
    larsonkeys = ("comp", "td", "int", "cas")
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      for Mu in T.matchups:
        for Pl in Mu.players:
          d = Mu.performance(Pl)
          larson = all(d.get(k, 0) for k in larsonkeys)
          if larson:
            A = cls(T, Pl)
            if A["status"] == "proposed":
              if value or A["prestige"]:
                A["prestige"] = value
                A["matchup"] = list(Mu.keys)
                Te = Mu.team_of_player(Pl)
                if Te:
                  A["team"] = str(Te.Id)
                A["status"] = "proposed"  # explicit
                if Mu.excluded == "yes":
                  A["matchup_excluded"] = "yes"
            yield A


cls = PA_Perfection

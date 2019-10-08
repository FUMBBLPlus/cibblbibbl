import collections
import cibblbibbl

from .mastercls import Achievement

class PA_StarPlayer(Achievement):
  subject_type = cibblbibbl.player.Player

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    trigspp = C["trigspp"]
    value = C["value"]
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.posonly == "yes":
        continue
      for Mu in T.matchups:
        for Pl in Mu.players:
          if not Pl.Id.isdecimal():
            continue
          d = Mu.performance(Pl)
          prespp = d.get("prespp", 0)
          postspp = prespp + d.get("spp", 0)
          if prespp < trigspp and trigspp <= postspp:
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


cls = PA_StarPlayer

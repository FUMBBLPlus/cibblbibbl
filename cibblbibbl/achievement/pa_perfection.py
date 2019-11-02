import collections
import cibblbibbl

from .. import field
from .mastercls import PlayerAchievement
from .pa_aerodynamicaim import PA_AerodynamicAim

class PA_Perfection(PlayerAchievement):

  rank = 10
  sortrank = 1020

  match = field.instrep.keyigetterproperty(3)

  argsnorm = PA_AerodynamicAim.argsnorm
  configfileargstrs = PA_AerodynamicAim.configfileargstrs
  export_plaintext = PA_AerodynamicAim.export_plaintext
  sort_key = PA_AerodynamicAim.sort_key

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    value = C["value"]
    larsonkeys = ("comp", "td", "int", "cas")
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      for Mu in T.matchups:
        for Pl in Mu.players:
          d = Mu.performance(Pl)
          larson = all(d.get(k, 0) for k in larsonkeys)
          if larson:
            A = cls(T, Pl, Mu.match)
            if A["status"] == "proposed":
              A["prestige"] = value
              A["status"] = "proposed"  # explicit
            yield A


cls = PA_Perfection

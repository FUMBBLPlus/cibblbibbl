import collections
import cibblbibbl

from .. import field
from .mastercls import PlayerAchievement
from .pa_bewaresupremekiller import PA_BewareSupremeKiller

class PA_TargetEliminated(PlayerAchievement):

  rank = 30
  sortrank = 1120

  match = field.instrep.keyigetterproperty(3)
  half = field.instrep.keyigetterproperty(4)
  turn = field.instrep.keyigetterproperty(5)
  victim = field.instrep.keyigetterproperty(6)

  argsnorm = PA_BewareSupremeKiller.argsnorm
  configfileargstrs = PA_BewareSupremeKiller.configfileargstrs
  export_plaintext = PA_BewareSupremeKiller.export_plaintext
  sort_key = PA_BewareSupremeKiller.sort_key

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    value = C["value"]
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      for Pl0, dead in T.deadplayers().items():
        for A0 in Pl0.achievements:
          if 10 <= A0.baseprestige:
            break
        else:
          continue
        if A0["status"] != "awarded":
          continue
        matchId, half, turn, reason, killerId = dead
        if killerId:
          Pl = cibblbibbl.player.player(killerId)
          Ma = cibblbibbl.match.Match(matchId)
          A = cls(T, Pl, Ma, half, turn, Pl0)
          if A["status"] == "proposed":
            A["prestige"] = value
            A["status"] = "proposed"  # explicit
            A["reason"] = reason
          yield A

    #agent02 = agent01  # TODO: might need more passes but it
                        # seems that not


cls = PA_TargetEliminated

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
  export_bbcode = PA_BewareSupremeKiller.export_bbcode
  export_plaintext = PA_BewareSupremeKiller.export_plaintext
  sort_key = PA_BewareSupremeKiller.sort_key

  @classmethod
  def agent01(cls, group):
    C = cls.defaultconfig_of_group(group)._data
    value = C["value"]
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      for Pl0, dead in T.deadplayers().items():
        for A0 in Pl0.achievements:
          if A0.get("status", "proposed") == "rejected":
            continue
          if T <= A0.tournament:
            continue
          if 10 <= A0.baseprestige:
            break
        else:
          continue
        matchId, half, turn, reason, killerId = dead
        if killerId:
          Pl = cibblbibbl.player.player(killerId)
          Ma = cibblbibbl.match.Match(matchId)
          A = cls(T, Pl, Ma, half, turn, Pl0)
          if A.get("status", "proposed") == "proposed":
            A["prestige"] = value
            A["status"] = "proposed"  # explicit
            A["reason"] = reason
          yield A

    #agent02 = agent01  # TODO: might need more passes but it
                        # seems that not


cls = PA_TargetEliminated

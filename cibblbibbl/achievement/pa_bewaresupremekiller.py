import collections
import cibblbibbl

from .mastercls import PlayerAchievement

class PA_BewareSupremeKiller(PlayerAchievement):

  rank = 20


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
      for Pl0, d in T.playerperformances().items():
        dead = d.get("dead")
        if not dead:
          continue
        for A0 in Pl0.achievements:
          if A0.clskey() == "pa_superstarplayer":
            break  # TODO: only awarded ones
        else:
          continue
        matchId, half, turn, reason, killerId = dead
        if killerId:
          Pl = cibblbibbl.player.player(killerId)
          Ma = cibblbibbl.match.Match(matchId)
          Mu = Ma.matchup
          A = cls(T, Pl)
          if A["status"] == "proposed":
            A["prestige"] = value
            A["matchup"] = list(Mu.keys)
            Te = Mu.team_of_player(Pl)
            if Te:
              A["team"] = str(Te.Id)
            A["status"] = "proposed"  # explicit
            if Mu.excluded == "yes":
              A["matchup_excluded"] = "yes"
            A["victimId"] = Pl0.Id
            A["matchId"] = matchId
            A["half"] = half
            A["turn"] = turn
            A["reason"] = reason
          yield A


cls = PA_BewareSupremeKiller
import collections
import cibblbibbl

from .. import field
from . import exporttools
from .mastercls import PlayerAchievement

class PA_BewareSupremeKiller(PlayerAchievement):

  rank = 20
  sortrank = 1110

  match = field.instrep.keyigetterproperty(3)
  half = field.instrep.keyigetterproperty(4)
  turn = field.instrep.keyigetterproperty(5)
  victim = field.instrep.keyigetterproperty(6)

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
          if A0.clskey() == "pa_superstarplayer":
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

  @classmethod
  def argsnorm(cls, args):
    args = list(args)
    args[0] = cibblbibbl.player.player(args[0])
    args[1] = cibblbibbl.match.Match(args[1])
    args[2] = int(args[2])
    args[3] = int(args[3])
    args[4] = cibblbibbl.player.player(args[4])
    return args

  @property
  def configfileargstrs(self):
    return [
        f'{self.match.Id:0>8}',
        str(self.half),
        str(self.turn),
        self.victim.Id,
    ]

  @property
  def sort_key(self):
    return (
        self.group_key,
        self.tournament,
        self.sortrank,
        self["name"],
        -self.baseprestige,
        self.subject.name,
        self.match,
        self.half,
        self.turn,
        self.victim.name,
    )


  def export_plaintext(self, show_Ids=False):
    rootA = self
    while rootA.prev is not None:
      rootA = rootA.prev
    s0 = exporttools.idpart(self, show_Ids)
    teamofmatch = exporttools.teamofmatch(self)
    team = exporttools.team(self)
    if hasattr(team, "name"):
      teamname = team.name
    else:
      teamname = team
    s1 = f'{self.subject.name} ({teamname})'
    reason = self.config["reason"]
    s2 = f' {exporttools.reasontrans.get(reason, reason)}'
    victimteam = exporttools.team(rootA, Pl=self.victim)
    if hasattr(victimteam, "name"):
      victimteamname = victimteam.name
    else:
      victimteamname = victimteam
    s3 = f' {self.victim.name} ({victimteamname})'
    s4 = f' in match #{self.match.Id}'
    oppoteam = exporttools.oppoteam(rootA, team_=teamofmatch)
    if not (oppoteam is victimteam):
      s5 = f' vs. {oppoteam.name}'
    else:
      s5 = ""
    s6 = exporttools.alreadyearned(self)
    return s0 + s1 + s2 + s3 + s4 + s5 + s6


cls = PA_BewareSupremeKiller

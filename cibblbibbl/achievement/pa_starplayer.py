import collections
import cibblbibbl
from cibblbibbl import bbcode

from .. import field
from . import agent
from . import exporttools
from .mastercls import PlayerAchievement
from .pa_aerodynamicaim import PA_AerodynamicAim

class PA_StarPlayer(PlayerAchievement):

  rank = 10
  sortrank = 1013

  match = field.instrep.keyigetterproperty(3)

  argsnorm = PA_AerodynamicAim.argsnorm
  configfileargstrs = PA_AerodynamicAim.configfileargstrs
  sort_key = PA_AerodynamicAim.sort_key

  @classmethod
  def agent01(cls, group):
    C = cls.defaultconfig_of_group(group)._data
    trigspp = C["trigspp"]
    value = C["value"]
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      for Mu in T.matchups:
        for Pl in Mu.players:
          #if not Pl.Id.isdecimal():  #TODO FIX
          #  continue
          d = Mu.performance(Pl)
          prespp = Pl.prespp(Mu)
          postspp = prespp + d.get("spp", 0)
          if prespp < trigspp and trigspp <= postspp:
            A = cls(T, Pl, Mu.match)
            if "proposed" in A.get("status", "proposed"):
              A["status"] = "proposed"  # explicit
              A["prestige"] = value
            yield A

  agent50 = classmethod(agent.iterpostponed)

  def export_bbcode(self):
    team = exporttools.team(self)
    s1 = f'{bbcode.player(self.subject)} ({bbcode.team(team)})'
    return s1

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    team = exporttools.team(self)
    if hasattr(team, "name"):
      teamname = team.name
    else:
      teamname = team
    s1 = f'{self.subject.name} ({teamname})'
    return s0 + s1

  def nexttournament(self):
    nexttournamentId = self.config.get("nexttournamentId")
    if nexttournamentId:
      return self.group.tournament[nexttournamentId]
    Re = self.match.replay
    with Re:
      normplayerIds = Re.normplayerIds
    for Te, playerIds in normplayerIds.items():
      if self.subject.Id in playerIds:
        return Te.next_tournament(self.tournament)
    else:
      msg = f'not found next tournament: {self.key}'
      raise Exception(msg)



cls = PA_StarPlayer

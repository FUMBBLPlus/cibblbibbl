import collections
import cibblbibbl
from cibblbibbl import bbcode

from .. import field
from . import exporttools
from .mastercls import PlayerAchievement

class PA_AerodynamicAim(PlayerAchievement):

  rank = 10
  sortrank = 1020

  match = field.instrep.keyigetterproperty(3)

  @classmethod
  def agent01(cls, group):
    C = cls.defaultconfig_of_group(group)._data
    value = C["value"]
    perfkey = C["perfkey"]
    perfvaltarget = C["perfvaltarget"]
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      for Mu in T.matchups:
        for Pl in Mu.players:
          d = Mu.performance(Pl)
          tvalue = d.get(perfkey, 0)
          if perfvaltarget <= tvalue:
            A = cls(T, Pl, Mu.match)
            if A.get("status", "proposed") == "proposed":
              A["prestige"] = value
              A["status"] = "proposed"  # explicit
            yield A

  @classmethod
  def argsnorm(cls, args):
    args = list(args)
    args[0] = cibblbibbl.player.player(args[0])
    args[1] = cibblbibbl.match.Match(args[1])
    return args

  @property
  def configfileargstrs(self):
    return [f'{self.match.Id:0>8}']

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
    )


  def export_bbcode(self):
    team = exporttools.team(self)
    teamofmatch = exporttools.teamofmatch(self)
    s1 = f'{bbcode.player(self.subject)} ({bbcode.team(team)})'
    s2 = f' in {bbcode.match(self.match, "match")}'
    oppoteam = exporttools.oppoteam(self, team_=teamofmatch)
    s3 = f' vs. {bbcode.team(oppoteam)}'
    s4 = exporttools.alreadyearned(self)
    return s1 + s2 + s3 + s4


  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    team = exporttools.team(self)
    teamofmatch = exporttools.teamofmatch(self)
    if hasattr(team, "name"):
      teamname = team.name
    else:
      teamname = team
    s1 = f'{self.subject.name} ({teamname})'
    s2 = f' in match #{self.match.Id}'
    oppoteam = exporttools.oppoteam(self, team_=teamofmatch)
    s3 = f' vs. {oppoteam.name}'
    s4 = exporttools.alreadyearned(self)
    return s0 + s1 + s2 + s3 + s4


cls = PA_AerodynamicAim

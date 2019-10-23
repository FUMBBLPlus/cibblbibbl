import collections
import cibblbibbl

from .. import field
from . import exporttools
from .mastercls import PlayerAchievement

class PA_AerodynamicAim(PlayerAchievement):

  rank = 10
  sortrank = 1020

  match = field.instrep.keyigetterproperty(3)

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    value = C["value"]
    perfkey = C["perfkey"]
    perfvaltarget = C["perfvaltarget"]
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
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
            if A["status"] == "proposed":
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


  def export_plaintext(self, show_Ids=False):
    Ma = self.match
    s0 = exporttools.idpart(self, show_Ids)
    team = exporttools.team(self)
    s1 = f'{self.subject} ({team})'
    s2 = f' in match #{self.match.Id}'
    oppoteam = exporttools.oppoteam(self, team_=team)
    s3 = f' vs. {oppoteam}'
    s4 = exporttools.alreadyearned(self)
    return s0 + s1 + s2 + s3 + s4


cls = PA_AerodynamicAim

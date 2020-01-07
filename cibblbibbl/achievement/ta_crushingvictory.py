import collections
import cibblbibbl

from .. import field
from . import exporttools
from .mastercls import TeamAchievement
from .pa_aerodynamicaim import PA_AerodynamicAim

class TA_CrushingVictory(TeamAchievement):

  rank = 10
  sortrank = 30

  match = field.instrep.keyigetterproperty(3)

  configfileargstrs = PA_AerodynamicAim.configfileargstrs
  sort_key = PA_AerodynamicAim.sort_key

  @classmethod
  def agent01(cls, group):
    C = cls.defaultconfig_of_group(group)._data
    value = C["value"]
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.abstract:
        continue
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      prestiges = collections.defaultdict(list)
      for Mu in T.matchups:
        Ma = Mu.match
        if Mu.abstract:
          continue
        if Mu.excluded == "yes":
          continue
        teams = sorted(Mu.teams)
        for i, Te in enumerate(teams):
          tds = Mu.performance(Te).get("td", 0)
          if tds < C["mintds"]:
            continue
          oppoTe = teams[1-i]
          oppotds = Mu.performance(oppoTe).get("td", 0)
          if C["oppomaxtds"] < oppotds:
            continue
          A = cls(T, Te, Ma)
          if A.get("status", "proposed") == "proposed":
            A["prestige"] = value
            A["status"] = "proposed"  # explicit; easier to edit
          yield A

  @classmethod
  def argsnorm(cls, args):
    args = list(args)
    args[0] = cibblbibbl.team.Team(int(args[0]))
    args[1] = cibblbibbl.match.Match(args[1])
    return args

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    s1 = self.subject.name
    s2 = f' in match #{self.match.Id}'
    s3 = exporttools.alreadyearned(self)
    return s0 + s1 + s2 + s3

cls = TA_CrushingVictory

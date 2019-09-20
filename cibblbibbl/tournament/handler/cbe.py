import pyfumbbl

import cibblbibbl

from . import default
from .. import tools

class CBETournament(
    default.AbstractTournament,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.rsym_prestige = {}

  @property
  def base_standings(self):
    m = cibblbibbl.tournament.tools.standings
    f = m.base_from_individual_results
    return f(self.individual_results)

  @property
  def individual_results(self):
    f_ind = cibblbibbl.tournament.tools.results.individual
    I = list(f_ind(self))
    teamtr = {Te: G for G in self.partner_groups for Te in G}
    IR = cibblbibbl.tournament.tools.results.IndividualResult
    I = [IR(teamtr[ir[0]], *ir[1:]) for ir in I]
    return I

  @property
  def partner_groups(self):
    return tuple(
      cibblbibbl.team.GroupOfTeams(p)
      for p in self.partners
    )

  @property
  def partners(self):
    L = self.config.get("partners")
    if L:
      return [[cibblbibbl.team.Team(ID) for ID in p] for p in L]
  @partners.setter
  def partners(self, L):
    L2 = [[Te.ID for Te in p] for p in L]
    self.config["partners"] = L2
  partners = partners.deleter(tools.config.deleter("partners"))

  @property
  def sub(self):
    d = cibblbibbl.tournament.byGroup[self.group_key]
    d2 = self.config.get("sub", {})
    return {name: d[str(ID)] for name, ID in d2.items()}
  @sub.setter
  def sub(self, d):
    Ts = list(d.values())
    assert all((T.group_key == self.group_key) for T in Ts)
    assert all((T.ID != self.ID) for T in Ts)
    self.config["sub"] = {name: T.ID for name, T in d.items()}
  sub = sub.deleter(tools.config.deleter("sub"))

  @property
  def schedule(self):
    f = cibblbibbl.tournament.tools.schedule.combined
    L = f(*[T.schedule for T in self.sub.values()])
    return L

  @property
  def standings(self):
    f = cibblbibbl.tournament.tools.standings.tiebroken
    L = f(self, base_=self.base_standings)
    # now we apply the individual standings back
    substandings = [
        S for T in self.sub.values() for S in T.standings
    ]
    dsub = {S["team"]: S for S in substandings}
    for S in L:
      teams = S["team"]
      S["perf"] = "\n".join(dsub[Te]["perf"] for Te in teams)
      S["matches"] = [dsub[Te]["matches"] for Te in teams]
    return L

  def excluded_teams(self, *args, **kwargs):
    return set()

  rsym_cad = default.Tournament.rsym_cad
  rsym_pts = default.Tournament.rsym_pts
  rsym_tdd = default.Tournament.rsym_tdd


def init(group_key, ID):
  return CBETournament(group_key, ID)

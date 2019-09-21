import itertools

import pyfumbbl

import cibblbibbl

from . import default
from . import cbe
from .. import tools

class HighestR5Tournament(
    default.Tournament,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):
  base_standings = cbe.CBETournament.base_standings
  excluded_teams = default.Tournament.excluded_teams
  rsym_cad = default.Tournament.rsym_cad
  rsym_pts = default.Tournament.rsym_pts
  rsym_tdd = default.Tournament.rsym_tdd
  sub = cbe.CBETournament.sub

  @property
  def custom_prestiges(self):
    r = {Te: {"gam": 0} for Te in self.teams}
    m_res = cibblbibbl.tournament.tools.results
    m_stand = cibblbibbl.tournament.tools.standings
    f = m_res.individual_from_schedule
    I = list(f(self, self.schedule))
    f = m_stand.base_from_individual_results
    B = f(I)
    base_rev = m_stand.base_revised(self,
        base_ = B,
        config_standings_key = "thisstandings",
    )
    d = {d["team"]: d["perf"] for d in base_rev}
    for Te, perf in d.items():
      gam = 0
      if self.season.name != "Winter":
        for rsym in perf:
          gam += self.rsym_prestige.get(rsym, 0)
      r[Te].update({"gam": gam})
    return r

  @property
  def fullschedule(self):
    Ss = [T.schedule for T in self.sub.values()]
    Ss.append(self.schedule)
    f = cibblbibbl.tournament.tools.schedule.combined
    L = f(*Ss)
    return L

  @property
  def individual_results(self):
    m_res = cibblbibbl.tournament.tools.results
    f_ind = m_res.individual_from_schedule
    I = list(f_ind(self, self.fullschedule))
    return I

  @property
  def rank_pairs(self):
    gen = zip(*[T.standings for T in self.sub.values()])
    T = tuple(
      tuple(d["team"] for d in rank_pair)
      for rank_pair in gen
    )
    return T

  @property
  def subschedule(self):
    Ss = [T.schedule for T in self.sub.values()]
    f = cibblbibbl.tournament.tools.schedule.combined
    L = f(*Ss)
    return L

  @property
  def teams(self):
    return set(ir.team for ir in self.individual_results)

  def reload_standings(self):
    m_res = cibblbibbl.tournament.tools.results
    m_stand = cibblbibbl.tournament.tools.standings
    hth_all = m_res.hth_all(self, schedule=self.fullschedule)
    base_rev = m_stand.base_revised(self,
        base_=self.base_standings,
    )
    # Now I look for the best ranked winner
    idx_d = {d["team"]: (i, d) for i, d in enumerate(base_rev)}
    ranks = [Te for rp in self.rank_pairs for Te in rp]
    for Te in ranks:
      i, d = idx_d[Te]
      perf = d.get("perf", "")
      if perf and perf[-1] == "W":
        d["pts"] += 1000000  # winner
        if i != 0:
          del base_rev[i]
          base_rev.insert(0, d)
        break
    standings = tools.standings.tiebroken(self,
        base_revised_ = base_rev,
        hth_all = hth_all,
    )
    self._standings = standings


def init(group_key, ID):
  return HighestR5Tournament(group_key, ID)

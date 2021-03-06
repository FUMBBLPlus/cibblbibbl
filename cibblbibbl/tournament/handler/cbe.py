import copy
import collections

import pyfumbbl

import cibblbibbl

from ... import field
from . import default
from .. import tools

class CBETournament(default.AbstractTournament):

  season_nr = default.Tournament.season_nr

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._matchups = ...

  @property
  def matchups(self):
    if self._matchups is ...:
      # I spawn abstract matchups based of every matchup of the
      # subtournaments; then I replace the teams with their
      # corresponding group number. I also delete the player
      # performances and reset the prestige values.
      group_of_partner = {
          Te: (nr, g)
          for nr, g in enumerate(self.partner_groups, 1)
          for Te in g
      }
      orig_matchups = tuple(
          cibblbibbl.matchup.sort_by_modified(
              Mu
              for T in self.sub.values()
              for Mu in T._iter_matchups()
          )
      )
      matchups = []
      for Mu in orig_matchups:
        filekeys = Mu.configfilepath.stem.split("-")
        AMu = cibblbibbl.matchup.AbstractMatchup(
            Mu.group_key,
            str(self.Id),
            Mu.round_,
            *sorted(Te.Id for Te in Mu.teams),
            filekeys = filekeys,
        )
        if not AMu.config:
          d = copy.deepcopy(Mu.config._data)
          d["player"] = {}
          dTP = d["team"]
          for teamId, d1 in list(dTP.items()):
            Te = cibblbibbl.team.Team(int(teamId))
            grnr, Gr = group_of_partner[Te]
            d1["id"] = teamId
            d1["prestige"] = 0
            groupId = f'{self.Id}-group{grnr:0>2}'
            dTP[groupId] = d1
            del dTP[teamId]
          AMu.config = d
          AMu.modified = Mu.modified
        matchups.append(AMu)
      self._matchups = tuple(matchups)
    return self._matchups

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
      return [[cibblbibbl.team.Team(Id) for Id in p] for p in L]
  @partners.setter
  def partners(self, L):
    L2 = [[Te.Id for Te in p] for p in L]
    self.config["partners"] = L2
  partners = partners.deleter(
      field.config.deleter("partners")
  )

  @property
  def sub(self):
    d = self.group.tournaments
    d2 = self.config.get("sub", {})
    return {name: d[str(Id)] for name, Id in d2.items()}
  @sub.setter
  def sub(self, d):
    Ts = list(d.values())
    assert all((T.group_key == self.group_key) for T in Ts)
    assert all((T.Id != self.Id) for T in Ts)
    self.config["sub"] = {name: T.Id for name, T in d.items()}
  sub = sub.deleter(field.config.deleter("sub"))

  def bestplayers(self):
    return {}

  def deadplayers(self):
    return {}

  def export_awards_bbcode(self):
    return self.export_awards_plaintext()  # TODO

  def export_awards_plaintext(self, show_Ids = False):
    nrsuffix = {1: "st", 2: "nd", 3: "rd"}
    TP_Standings = cibblbibbl.achievement.tp_standings.cls
    standings = self.standings()
    partner_groups = self.partner_groups
    parts = []
    gen = reversed(list(enumerate(standings, 1)))
    for i, (nr, d) in enumerate(gen):
      if i:
        parts.append("")
      groupnr = partner_groups.index(d["team"]) + 1
      nrstr = f'{nr}{nrsuffix.get(nr, "th")} place: '
      if show_Ids:
        teams = [f'[{Te.Id}] {Te}' for Te in d["team"]]
      else:
        teams = [str(Te) for Te in d["team"]]
      teamstr = " and ".join(teams)
      groupstr = f' (Partners #{groupnr})'
      parts.append(nrstr + teamstr + groupstr)
      prestige = TP_Standings(self, d["team"][0])["prestige"]
      parts.append(f'Prestige Points Earned: {prestige}')
    return "\n".join(parts)

  def extraplayerperformances(self, join=False):
    return {}

  def get_team(self, teamId):
    group_nr = int(teamId[-2:])
    group_index = group_nr - 1
    return self.partner_groups[group_index]

  def playerperformances(self):
    return{}

  def standings(self):
    # As the team performance keys are replaced with the group
    # numbers, the team records provided by the default
    # standings function is wrong: they are Team(groupNr).
    # I fix this by replacing them with the proper GroupOfTeams
    # instances. I also define a "perfs" record which contains
    # the performances of the individual teams in order.
    group_of_number = {
        nr: g
        for nr, g in enumerate(self.partner_groups, 1)
        for Te in g
    }
    substandings = [
        S for T in self.sub.values() for S in T.standings()
    ]
    dsub = {S["team"]: S for S in substandings}
    standings = default.Tournament.standings(self)
    for d in standings:
      d["perfs"] = [dsub[Te]["perf"] for Te in d["team"]]
    return standings


def init(group_key, Id):
  return CBETournament(group_key, Id)

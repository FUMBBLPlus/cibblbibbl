import bisect

from . import field

import pyfumbbl

import cibblbibbl


class Group(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  achievements = field.insts.self_tournament_achievements
  config = field.config.cachedconfig
  excluded_team_ids = field.config.field(
      "excluded_teams", default=[]
  )
  key = field.instrep.keyigetterproperty(0)
  matchups = field.insts.self_tournaments_matchups

  def __init__(self, key: str, *,
      register_tournaments = True,
      register_teams = True,
      register_achievements = True,
  ):
    self.years = set()
    self.seasons = set()
    self.tournaments = {}
    self.teams = set()
    if register_tournaments:
      self.register_tournaments()
    if register_teams:
      self.register_teams()
    if register_achievements:
      self.register_achievements()

  @property
  def configfilepath(self):
    return cibblbibbl.data.path / self.key / "config.json"

  @property
  def excluded_teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamId)
        for teamId in self.config.get("excluded_teams", [])
    )
  @excluded_teams.setter
  def excluded_teams(self, sequence):
    self.excluded_team_ids = [Te.Id for Te in sorted(sequence)]
  @excluded_teams.deleter
  def excluded_teams(self):
    self.excluded_team_ids = []

  @property
  def season_names(self):
    return tuple(self.config["seasons"])

  def exclude_teams(self, *teams):
    for Te in teams:
      if hasattr(Te, "nr"):
        Te = Te.nr
      L = self.excluded_team_ids
      bisect.insort(L, int(Te))
      self.excluded_team_ids = L  # directly is not good

  def register_achievements(self):
    cibblbibbl.achievement.collect(self.key)

  def register_teams(self):
    for M in self.matchups:
      for Te in M.teams:
        if Te not in self.teams:
          self.teams.add(Te)
          Te._matchups[self.key] = []
        Te._matchups[self.key].append(M)

  def register_tournaments(self):
    C = self.config
    seasons = tuple(C["seasons"])
    get_handler_f = cibblbibbl.tournament.handler.get_handler
    for groupId in C.get("groupIds", []):
      for d in pyfumbbl.group.tournaments(groupId):
        Id = str(d["id"])
        handler_ = get_handler_f(self.key, Id)
        T = handler_.init(self.key, Id)
        T.register()
    for Id in C.get("abstract_tournaments", []):
      handler_ = get_handler_f(self.key, Id)
      T = handler_.init(self.key, Id)
      T.register()

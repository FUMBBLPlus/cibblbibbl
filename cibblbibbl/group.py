import bisect

from . import field

import pyfumbbl

import cibblbibbl


class Group(metaclass=cibblbibbl.helper.InstanceRepeater):

  achievements = field.insts.self_tournament_achievements
  config = field.config.CachedConfig()
  excluded_teamIds = field.config.DDField(
      key="excluded_teams", default=lambda i, d: set()
  )
  excluded_teams = field.insts.excluded_teams
  exclude_teams = field.insts.exclude_teams
  key = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = field.insts.self_tournaments_matchups
  regions = field.config.DDField()
  replays = field.insts.matches_replays

  def __init__(self, key: str):
    self.years = set()
    self.seasons = set()
    self.tournaments = {}
    self.teams = set()
    self.players = set()

  def init(self):
    self.register_tournaments()
    self.register_matchups()
    self.register_achievements()

  @property
  def configfilepath(self):
    return cibblbibbl.data.path / self.key / "config.json"

  @property
  def season_names(self):
    return tuple(self.config["seasons"])

  def register_achievements(self, rank=None):
    cibblbibbl.achievement.collect(self.key, rank=rank)

  def register_matchups(self):
    exc_teams = self.excluded_teams
    for Mu in self.matchups:
      for Te in Mu.teams:
        if Te in exc_teams:
          continue
        if Te not in self.teams:
          self.teams.add(Te)
          Te._matchups[self.key] = []
        Te._matchups[self.key].append(Mu)
      for Pl in Mu.players:
        if Pl not in self.players:
          self.players.add(Pl)
          Pl._matchups[self.key] = []
        Pl._matchups[self.key].append(Mu)
    for Te in self.teams:
      prevMu = None
      for Mu in sorted(Te.matchups(self.key)):
        if prevMu:
          prevMu._teamlinked[Te]["next"] = Mu
          Mu._teamlinked[Te]["prev"] = prevMu
        prevMu = Mu

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
    for T in self.tournaments.values():
      for Te in T.teams:
        Te.tournaments.add(T)

import bisect

from .jsonfile import jsonfile
import pyfumbbl

import cibblbibbl


class Group(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  dump_kwargs = (
      ("ensure_ascii", False),
      ("indent", "\t"),
      ("sort_keys", True),
  )

  def __init__(self, key: str, *,
      register_tournaments = True,
      register_teams = True,
  ):
    self._config = ...
    self._matchups = ...
    self.years = set()
    self.seasons = set()
    self.tournaments = {}
    self.teams = set()
    if register_tournaments:
       self.register_tournaments()
    if register_teams:
       self.register_teams()

  @property
  def config(self):
    if self._config is ...:
      self.reload_config()
    return self._config

  excluded_team_ids = cibblbibbl.config.field(
      "excluded_teams", default=[]
  )
  @property
  def excluded_teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamId)
        for teamId in self.config.get("excluded_teams", [])
    )
  @excluded_teams.setter
  def excluded_teams(self, sequence):
    excluded_team_ids = [Te.Id for Te in sorted(sequence)]
  @excluded_teams.deleter
  def excluded_teams(self):
    excluded_team_ids = []

  @property
  def key(self):
    return self._KEY[0]

  @property
  def matchups(self):
    if self._matchups is ...:
      self._matchups = tuple(
          cibblbibbl.matchup.sort_by_modified(
              M
              for T in self.tournaments.values()
              for M in T.matchups
          )
      )
    return self._matchups

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

  def reload_config(self):
    jf = jsonfile(
        cibblbibbl.data.path / self.key / "config.json",
        default_data = {},
        autosave = True,
        dump_kwargs = dict(self.dump_kwargs),
    )
    self._config = jf.data

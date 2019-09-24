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

  def __init__(self, key: str, register_tournaments=True):
    self._config = None
    self.years = set()
    self.seasons = set()
    self.tournaments = {}
    if register_tournaments:
       self.register_tournaments()

  @property
  def config(self):
    if self._config is None:
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
    return tuple(self.itermatchups())

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

  def itermatchups(self):
    for T in self.tournaments.values():
      yield from T.itermatchups()

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

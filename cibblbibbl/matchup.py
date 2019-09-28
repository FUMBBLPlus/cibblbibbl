import datetime

import pyfumbbl

import cibblbibbl

from . import matchup_config as MC


class Matchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  class IsLocked(Exception): pass

  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init__(self,
      group_key: str,
      tournamentId: str,
      round: int,
      low_teamId:int,
      high_teamId:int,
      *,
      register_match = True,
  ):
    self._config = ...
    self._match = ...

  @property
  def apischedulerecord(self):
    this_team_ids = self._KEY[3:5]
    for d in self.tournament.apischedule:
      team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
      if team_ids == this_team_ids:
        return d

  @property
  def config(self):
    if self._config is ...:
      self.reload_config()
    if not self._config:
      self.update_config()
    return self._config

  @property
  def configfiledir(self):
    tournamentId = str(self._KEY[1])
    if tournamentId.isdecimal():
      dir = f'{tournamentId:0>8}'
    else:
      dir = tournamentId
    return dir

  @property
  def configfilename(self):
    filename = (
        f'{self.round:0>2}'
        f'-{self._KEY[3]:0>7}'
        f'-{self._KEY[4]:0>7}'
        ".json"
    )
    return filename

  @property
  def configfilepath(self):
    filepath = (
        cibblbibbl.data.path
        / self.group_key
        / "matchup"
        / self.configfiledir
        / self.configfilename
    )
    return filepath

  @property
  def created(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["created"], fmt)

  excluded = cibblbibbl.config.yesnofield(
      "!excluded", default="no",
  )

  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key

  @property
  def highlightedteam(self):
    d = self.apischedulerecord
    teamId = d.get("result", {}).get("winner")
    if teamId:
      return cibblbibbl.team.Team(teamId)

  locked = cibblbibbl.config.yesnofield("!locked", default="no")

  @property
  def match(self):
    if self._match is ...:
      self._match = None
      d = self.apischedulerecord
      matchId = d.get("result", {}).get("id")
      if matchId:
        self._match = Ma = cibblbibbl.match.Match(matchId)
        Ma._matchup = self
    return self._match

  @property
  def modified(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["modified"], fmt)

  @property
  def position(self):
    return self.apischedulerecord["position"]

  @property
  def round(self):
    return self._KEY[2]

  @property
  def season(self):
    return self.tournament.season

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamId)
        for teamId in self._KEY[3:5]
    )

  @property
  def tournament(self):
    return self.group.tournaments[str(self._KEY[1])]

  @property
  def year(self):
    return self.tournament.year

  def calculate_config(self):
    G = self.group
    T = self.tournament
    R = self.apischedulerecord
    D = {}
    args = G, T, R, self, D
    D.update(dict(MC.Ids(*args)))
    D["!excluded"] = MC.excluded(*args)
    PP = D["player_performance"] = {}
    for t in MC.player_performances(*args):
      teamId, playerId, D2 = t
      PP.setdefault(teamId, {})[playerId] = D2
    TP = D["team_performance"] = {}
    for teamId, D2 in MC.team_performances(*args):
      TP[teamId] = D2
    Ma = self.match
    if Ma:
      del Ma.replaydata  # free up memory
    return D

  def iterdead(self):
    C = self.config
    for teamId, DPP in C["player_performance"].items():
      for playerId, dpp in DPP.items():
        dead = dpp.get("dead")
        if not dead:
          continue
        yield teamId, playerId, dpp

  def reload_config(self):
    jf = cibblbibbl.data.jsonfile(
        self.configfilepath,
        default_data = {},
        autosave=True,
        dump_kwargs=dict(self.dump_kwargs)
    )
    self._config = jf.data

  def rewrite_config(self):
    if self.locked:
      raise self.IsLocked(
          f'unable to rewrite config of locked matchup {self}'
      )
    if self._config is ...:
      self.reload_config()
    self._config.root.data = self.calculate_config()
    self._config = self._config.root.data

  def update_config(self):
    if self._config is ...:
      self.reload_config()
    self._config.root.data.update(self.calculate_config())


def sort_by_modified(matchups):
  return sorted(matchups, key=lambda M: M.modified)

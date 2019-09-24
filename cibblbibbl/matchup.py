import datetime

import pyfumbbl

import cibblbibbl

from . import matchup_config as MC


class Matchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init__(self,
      group_key: str,
      tournamentId: str,
      round: int,
      low_teamId:int,
      high_teamId:int,
  ):
    self._config = None

  @property
  def apischedulerecord(self):
    this_team_ids = self._KEY[3:5]
    for d in self.tournament.apischedule:
      team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
      if team_ids == this_team_ids:
        return d

  @property
  def config(self):
    if self._config is None:
      self.reload_config()
    if not self._config:
      self.update_config()
    return self._config

  @property
  def created(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["created"], fmt)

  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key

  @property
  def highlightedteam(self):
    d = self.apischedulerecord
    teamId = d.get("result", {}).get("winner")
    if teamId:
      return cibblbibbl.team.Team(teamId)

  @property
  def match(self):
    d = self.apischedulerecord
    matchId = d.get("result", {}).get("id")
    if matchId:
      return cibblbibbl.match.Match(matchId)

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

  def reload_config(self):
    filename = (
        f'{self.round:0>2}'
        f'-{self._KEY[3]:0>7}'
        f'-{self._KEY[4]:0>7}'
        ".json"
    )
    tournamentId = str(self._KEY[1])
    if tournamentId.isdecimal():
      tournament_dir = f'{tournamentId:0>8}'
    else:
      tournament_dir = tournamentId
    filepath = (
        cibblbibbl.data.path
        / "matchup"
        / tournament_dir
        / filename
    )
    jf = cibblbibbl.data.jsonfile(
        filepath,
        default_data = {},
        autosave=True,
        dump_kwargs=dict(self.dump_kwargs)
    )
    self._config = jf.data

  def rewrite_config(self):
    if self._config is None:
      self.reload_config()
    self._config.root.data = self.calculate_config()

  def update_config(self):
    if self._config is None:
      self.reload_config()
    self._config.root.data.update(self.calculate_config())

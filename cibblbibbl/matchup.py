import datetime

import pyfumbbl

import cibblbibbl

from . import matchup_config as MC


class BaseMatchup:

  class IsLocked(Exception): pass

  def __init__(self,
      group_key: str,
      tournamentId: str,
      *keys,
  ):
    self._group_key = group_key
    self._tournamentId = tournamentId
    self._keys = keys
    self._config = ...

  @property
  def config(self):
    if self._config is ...:
      self.reload_config()
    return self._config

  @property
  def configfilepath(self):
    return self.tournament.matchupsdir / self.configfilename

  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  excluded = cibblbibbl.config.yesnofield(
      "!excluded", default="no",
  )

  group = cibblbibbl.year.Year.group

  @property
  def group_key(self):
    return self._group_key

  @property
  def keys(self):
    return self._keys

  locked = cibblbibbl.config.yesnofield("!locked", default="no")

  @property
  def match(self):
    match, matchId = None, self.config.get("matchId")
    if matchId is not None:
      match = cibblbibbl.match.Match(int(matchId))
    return match
  @match.setter
  def match(self, value):
    if hasattr(value, "Id"):
      value = value.Id
    self.config["matchId"] = str(value)
  match = match.deleter(cibblbibbl.config.deleter("matchId"))

  @property
  def season(self):
    return self.tournament.season

  @property
  def season_nr(self):
    return self.tournament.season_nr

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(int(teamId))
        for teamId in self.config["team_performance"]
    )

  @property
  def tournament(self):
    return self.group.tournaments[self.tournamentId]

  @property
  def tournamentId(self):
    return str(self._tournamentId)

  def reload_config(self):
    jf = cibblbibbl.data.jsonfile(
        self.configfilepath,
        default_data = {},
        autosave=True,
        dump_kwargs=dict(self.dump_kwargs)
    )
    self._config = jf.data

  @property
  def year(self):
    return self.tournament.year

  @property
  def year_nr(self):
    return self.tournament.year_nr

  def performance(self, subject):
    if isinstance(subject, cibblbibbl.team.Team):
      return self.config["team_performance"][str(subject.Id)]
    elif isinstance(subject, cibblbibbl.player.Player):
      return self.config["player_performance"][str(subject.Id)]
    else:
      raise NotImplementedError(
          f'unknown performance subject type: {subject!r}'
      )



class AbstractMatchup(
    BaseMatchup,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self, *args, filekeys=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.filekeys = filekeys

  def __repr__(self):
    return (
        f'{self.__class__.__name__}'
        "("
        f'{self.group_key!r}, '
        f'{self.tournamentId!r}, '
        f'{", ".join(repr(k) for k in self.keys)}'
        ")"
    )

  @property
  def abstract(self):
    return True

  @property
  def configfilename(self):
    filekeys = self.filekeys or self.keys
    return "a-" + "-".join(str(v) for v in filekeys) + ".json"

  @property
  def modified(self):
    modified = self.config.get("modified")
    if modified:
      fmt = "%Y-%m-%d %H:%M:%S"
      modified = datetime.datetime.strptime(modified, fmt)
    return modified
  @modified.setter
  def modified(self, value):
    fmt = "%Y-%m-%d %H:%M:%S"
    if hasattr(value, "isdecimal"):
      dt = datetime.datetime.strptime(value, fmt)  # test
    else:
      value = value.strftime(fmt)
    self.config["modified"] = value
  @modified.deleter
  def modified(self):
    try:
      del self.config["modified"]
    except KeyError:
      pass

  def update_config(self, data):
    if self._config is ...:
      self.reload_config()
    self._config.root.data.update(data)



class Matchup(
    BaseMatchup,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self,
      group_key: str,
      tournamentId: str,
      round_: int,
      low_teamId:int,
      high_teamId:int,
  ):
    super().__init__(
        group_key,
        tournamentId,
        round_,
        low_teamId,
        high_teamId,
    )
    self._match = ...

  @property
  def abstract(self):
    return False

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
      dirname = f'{tournamentId:0>8}'
    else:
      dirname = tournamentId
    dir = (
        cibblbibbl.data.path
        / self.group_key
        / "matchup"
        / dirname
    )
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
    return self.configfiledir / self.configfilename

  @property
  def created(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["created"], fmt)

  @property
  def highlightedteam(self):
    d = self.apischedulerecord
    teamId = d.get("result", {}).get("winner")
    if teamId:
      return cibblbibbl.team.Team(teamId)

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
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamId)
        for teamId in self._KEY[3:5]
    )

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

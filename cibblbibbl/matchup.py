import datetime

import pyfumbbl

from . import field

import cibblbibbl

from . import matchup_config as MC


class BaseMatchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.cachedconfig
  excluded = field.config.yesnofield("!excluded", default="no")
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  locked = field.config.yesnofield("!locked", default="no")
  season = field.inst.season_of_self_tournament
  season_nr = field.inst.season_nr_of_self_tournament
  tournament = field.inst.tournament
  tournamentId = field.instrep.keyigetterproperty(1)
  year = field.inst.year_of_self_tournament
  year_nr = field.inst.year_nr_of_self_tournament

  def __init__(self, group_key: str, tournamentId: str, *keys):
    self._group_key = group_key
    self._tournamentId = tournamentId
    self._keys = keys

  @property
  def configfilepath(self):
    return self.tournament.matchupsdir / self.configfilename

  @property
  def keys(self):
    return self._KEY[2:]

  @property
  def match(self):
    matchId = self.config.get("matchId")
    if matchId is not None:
      return cibblbibbl.match.Match(int(matchId))
  @match.setter
  def match(self, value):
    if hasattr(value, "Id"):
      value = value.Id
    self.config["matchId"] = str(value)
  match = match.deleter(field.config.deleter("matchId"))

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(int(teamId))
        for teamId in self.config["team_performance"]
    )

  def performance(self, subject):
    if isinstance(subject, cibblbibbl.team.Team):
      return self.config["team_performance"][str(subject.Id)]
    elif isinstance(subject, cibblbibbl.player.Player):
      return self.config["player_performance"][str(subject.Id)]
    else:
      raise NotImplementedError(
          f'unknown performance subject type: {subject!r}'
      )



class AbstractMatchup(BaseMatchup):

  abstract = field.common.Constant(True)
  modified = field.config.TimeField()

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
  def configfilename(self):
    filekeys = self.filekeys or self.keys
    return "a-" + "-".join(str(v) for v in filekeys) + ".json"



class Matchup(BaseMatchup):

  abstract = field.common.Constant(False)
  created = field.matchup.ScheduleRecordTimeFieldGetter()
  highlightedteam = field.matchup.sr_highlightedteam_getter
  match = field.matchup.MatchLink()
  modified = field.matchup.ScheduleRecordTimeFieldGetter()
  position = field.matchup.sr_position_getter
  round_ = field.instrep.keyigetterproperty(2)

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
    pass

  @property
  def apischedulerecord(self):
    if not hasattr(self, "_apischedulerecord"):
      this_team_ids = self._KEY[3:5]
      for d in self.tournament.apischedule:
        team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
        if team_ids == this_team_ids:
          self._apischedulerecord = d
          return d
    else:
      return self._apischedulerecord

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
        f'{self.round_:0>2}'
        f'-{self._KEY[3]:0>7}'
        f'-{self._KEY[4]:0>7}'
        ".json"
    )
    return filename

  @property
  def configfilepath(self):
    return self.configfiledir / self.configfilename

  @property
  def schedulerecord(self):
    return self.apischedulerecord

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



def sort_by_modified(matchups):
  return sorted(matchups, key=lambda M: M.modified)

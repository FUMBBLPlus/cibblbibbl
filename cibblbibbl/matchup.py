import datetime

import pyfumbbl

from . import field

import cibblbibbl

from . import matchup_config


class BaseMatchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.CachedConfig()
  excluded = field.config.yesnofield("!excluded", default="no")
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  locked = field.config.yesnofield("!locked", default="no")
  season = field.common.DiggedAttr("tournament", "season")
  season_nr = field.common.DiggedAttr("tournament", "season_nr")
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
    return (
        self.tournament.matchupsconfigdir / self.configfilename
    )

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
  def player_perf_keys(self):
    PP_items = self.config["player"].items()
    return frozenset(
        (teamId, playerId)
        for teamId, d0 in PP_items
        for playerId, d1 in d0.items()
    )

  @property
  def players(self):
    RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
    PP_items = self.config["player"].items()
    S = set()
    for teamId, d0 in PP_items:
      Te = cibblbibbl.team.Team(int(teamId))
      for playerId, d1 in d0.items():
        Pl = cibblbibbl.player.player(playerId)
        Pl._name = d1["name"]
        Pl._team = Te
        Pl._typechar = d1["type"]
        if isinstance(Pl, RaisedDeadPlayer):
          if self.match:
            if not Pl.prevdeadmatchId:
              Pl.prevdeadmatchId = self.match.Id
            if not Pl.prevreason:
              Re = self.match.replay
              with Re:
                rosterdata = Re.teamdata[Te]["roster"]
                if rosterdata["necromancer"]:
                  Pl.prevreason = "raisedfromdead"
                else:
                  Pl.prevreason = "infected"
        S.add(Pl)
    return frozenset(S)

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(int(teamId))
        for teamId in self.config["team"]
        if teamId.isdecimal()
    )

  def performance(self, subject):
    if isinstance(subject, cibblbibbl.team.Team):
      return self.config["team"][str(subject.Id)]
    else:
      if isinstance(subject, cibblbibbl.player.BasePlayer):
        playerId = str(subject.Id)
      else:
        playerId = str(subject)
      PP_items = self.config["player"].items()
      for teamId, d0 in PP_items:
        try:
          return d0[playerId]
        except KeyError:
          continue
    raise NotImplementedError(
        f'unknown performance subject type: {subject!r}'
    )

  def team_of_player(self, player):
    if hasattr(player, "Id"):
      playerId0 = str(player.Id)
    else:
      playerId0 = str(player)
    for teamId, playerId1 in self.player_perf_keys:
      if playerId0 == playerId1:
        return cibblbibbl.team.Team(int(teamId))


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

  def iterdead(self):
    # https://stackoverflow.com/a/13243920/2334951
    yield from ()



class Matchup(BaseMatchup):

  abstract = field.common.Constant(False)
  configdir = field.config.MatchupsDirectory()
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
        if self.round_ != d["round"]:
          continue
        team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
        if team_ids == this_team_ids:
          self._apischedulerecord = d
          return d
    else:
      return self._apischedulerecord

  @property
  def configdir(self):
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
  def configfilebasename(self):
    filebasename = (
        f'{self.round_:0>2}'
        f'-{self._KEY[3]:0>7}'
        f'-{self._KEY[4]:0>7}'
    )
    return filebasename

  @property
  def configfilename(self):
    return self.configfilebasename + ".json"

  @property
  def configfilepath(self):
    return self.configdir / self.configfilename

  def configmaker(self, **kwargs):
    return matchup_config.MatchupConfigMaker(self, **kwargs)

  @property
  def schedulerecord(self):
    return self.apischedulerecord

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamId)
        for teamId in self._KEY[3:5]
    )

  def calculate_config(self):
    d = self.configmaker()()
    return d

  def iterdead(self):
    C = self.config
    for teamId, DPP in C["player"].items():
      for playerId, dpp in DPP.items():
        dead = dpp.get("dead")
        if not dead:
          continue
        yield teamId, playerId, dpp



def sort_by_modified(matchups):
  return sorted(matchups, key=lambda M: M.modified)

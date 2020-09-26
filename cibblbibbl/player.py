from slugify import slugify

import pyfumbbl

from . import field
from . import helper
from .jsonfile import jsonfile

import cibblbibbl


class UnchainedPlayerException(Exception):
  pass


class BasePlayer(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.CachedConfig()
  configfilename = field.filepath.idfilename
  dummy = field.config.DDField(default="no")
  Id = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = cibblbibbl.team.Team.matchups
  position = field.inst.position_by_self_positionId
  adminspp = field.config.DDField(
      default=lambda inst, desc: dict()
  )
  prevId = field.config.DDField(
      default = lambda i, d: i.get_prevId(),
      default_set_delete = False,
  )
  prevachievmul = field.config.DDField(default=1)
  prevdeadmatchId = field.config.DDField()
  prevreason = field.config.DDField()
  prevsppmul = field.config.DDField(default=1)
  replays = field.insts.matches_replays

  def __init__(self, playerId,
      name = ...,
      team = ...,
      typechar = ...,
  ):
    self._matchups = {}
    self._name = name
    if name is not ...:
      self._name = helper.norm_name(name)
    self._team = team
    self._typechar = typechar
    self.achievements = set()
    self._nextIds = set()
    if hasattr(self, "get_nextIds"):
      self._nextIds |= self.get_nextIds()
      for p in self.nexts:
        p.prevId = self.Id
    prev = self.prev
    if prev:
      self.prevId = prev.Id  # ensure saved in config
      prev._nextIds.add(self.Id)


  def __repr__(self):
    clsname = self.__class__.__name__
    return f'{clsname}({self.Id!r})'

  __str__ = field.inst.id_and_name_str

  __eq__ = field.ordering.eq_when_is
  __lt__ = field.ordering.PropTupCompar("sort_key")
  __le__ = field.ordering.PropTupCompar("sort_key")
  __ne__ = field.ordering.ne_when_is_not
  __gt__ = field.ordering.PropTupCompar("sort_key")
  __ge__ = field.ordering.PropTupCompar("sort_key")

  @staticmethod
  def configfilepathroot():
    return cibblbibbl.data.path / "player"

  @property
  def configfilepath(self):
    return self.configfilepathroot() / self.configfilename

  @property
  def name(self):
    if self._name is ...:
      self._name = helper.norm_name(self.getname)
    return self._name

  @property
  def nexts(self):
    nextIds = self._nextIds
    if nextIds is not None:
      return set(player(Id) for Id in list(nextIds))

  @property
  def prev(self):
    prevId = self.prevId
    if prevId is not None:
      return player(prevId)

  @property
  def team(self):
    if self._team is ...:
      teamId = self.config.get("team")
      if teamId is not None:
        self._team = cibblbibbl.team.Team(int(teamId))
      elif (
          self.prev and isinstance(self.prev, RaisedDeadPlayer)
      ):
        return self.prev.team
      else:
        raise ValueError(f'no team: {self!r}')
    return self._team
  @team.setter
  def team(self, value):
    self._team = value
    self.config["team"] = value.Id
  @team.deleter
  def team(self):
    self._team = ...
    try:
      del self.config["team"]
    except KeyError:
      pass

  @property
  def typechar(self):
    if self._typechar is ...:
      self._typechar = self.config.get("typechar")
    return self._typechar
  @typechar.setter
  def typechar(self, value):
    self._typechar = value
    self.config["typechar"] = value
  @typechar.deleter
  def typechar(self):
    self._typechar = ...
    try:
      del self.config["typechar"]
    except KeyError:
      pass


  # TODO prevId setter which backchains instantly

  def get_prevId(self):
    return None

  def prespp(self, matchup):
    value = matchup.performance(self).get("prespp", 0)
    matchId = matchup.match.Id
    for matchId1, value1 in self.adminspp.items():
      if int(matchId1) <= matchId:
        value += value1
    return value



class MercenaryPlayer(BasePlayer):

  permanent = field.common.Constant(False)
  prevsppmul = field.config.DDField(default=0)
  status = field.common.Constant("Active")

  @property
  def getname(self):
    replayId, playerId = self.Id[5:].split("-")
    Re = cibblbibbl.replay.Replay(int(replayId))
    Te = cibblbibbl.team.Team(int(playerId.split("M")[0]))
    with Re as Re:
      D = Re.normteamdata[Te]
    for d in D["playerArray"]:
      if d["playerId"] == self.Id: # ! NOT playerId
        break
    else:
      raise Exception(f'not found: {self.Id}')
    return d["playerName"]

  @property
  def positionId(self):
    replayId, playerId = self.Id[5:].split("-")
    Re = cibblbibbl.replay.Replay(int(replayId))
    Te = cibblbibbl.team.Team(int(playerId.split("M")[0]))
    with Re as Re:
      D = Re.normteamdata[Te]
    for d in D["playerArray"]:
      if d["playerId"] == self.Id: # ! NOT playerId
        break
    else:
      raise Exception(f'not found: {self.Id}')
    return d["positionId"]

  @property
  def sort_key(self):
    Id = self.Id[5:].replace("M", "-")
    idvals = tuple(int(x) for x in Id.split("-"))
    return (1000,) + idvals

  @property
  def team(self):
    return "Mercenary"

  @property
  def typechar(self):
    return "M"

  def prespp(self, matchup):
    return 0


class NormalPlayer(BasePlayer):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.player.get,
  )
  permanent = field.common.Constant(True)
  positionId = field.common.DiggedKeys(
      "apiget", "position", "id",
  )
  status = field.common.DiggedKeys("apiget", "status")

  @property
  def getname(self):
    if self._name is ...:
      if "name" in self.config:
        self._name = self.config["name"]
      else:
        self._name = self.apiget["name"]
    return self._name

  @property
  def team(self):
    team = BasePlayer.team.fget(self)
    if team is None:
      prev = self.prev
      if isinstance(self.prev, RaisedDeadPlayer):
        self._team = self.prev.team
    return self._team
  team = team.setter(BasePlayer.team.fset)
  team = team.deleter(BasePlayer.team.fdel)

  @property
  def typechar(self):
    typechar = BasePlayer.typechar.fget(self)
    if typechar is None:
      self._typechar = "R"
    return self._typechar
  typechar = typechar.setter(BasePlayer.typechar.fset)
  typechar = typechar.deleter(BasePlayer.typechar.fdel)

  @property
  def sort_key(self):
    return (1, int(self.Id))


Player = NormalPlayer


class RaisedDeadPlayer(BasePlayer):

  getname = field.common.DiggedAttr("prev", "getname")
  permanent = field.common.Constant(True)
  prevsppmul = field.config.DDField(default=0)

  @property
  def next(self):
    nextId = self.nextId
    return (player(nextId) if nextId is not None else None)

  @property
  def nextId(self):
    nextId = self.Id.split("_")[-1]
    if nextId.startswith("UNKNOWN"):
      raise UnchainedPlayerException(
          f'unchained raised dead player: {self.Id}'
      )
    elif nextId != "0":
      return nextId

  @property
  def positionId(self):
    return self.Id.split("_")[0].split("-")[1]

  @property
  def prevdeadmatchId(self):
    matchId = self.config.get("prevdeadmatchId")
    if matchId:
      return matchId
    if isinstance(self.prev, RaisedDeadPlayer):
      return self.prev.prevdeadmatchId
  prevdeadmatchId = prevdeadmatchId.setter(
      field.config.setter("prevdeadmatchId")
  )
  prevdeadmatchId = prevdeadmatchId.deleter(
      field.config.deleter("prevdeadmatchId")
  )

  @property
  def sort_key(self):
    nextIds = self._nextIds
    if nextIds:
      return (1, int(next(iter(nextIds))) - 0.1)
    else:
      return (1, int(self.prevId) + 0.1)

  @property
  def status(self):
    next = self.next
    if next:
      return next.status
    else:
      return "Retired"

  @property
  def typechar(self):
    return "D"

  def get_nextIds(self):
    nextId = self.nextId
    return ({nextId} if nextId is not None else set())

  def get_prevId(self):
    return self.Id.split("_")[-2]

  def prespp(self, matchup):
    return 0




class StarPlayer(BasePlayer):
  config = field.config.CachedConfig()
  permanent = field.common.Constant(False)
  prevsppmul = field.config.DDField(default=0)
  status = field.config.DDField(default="Active")

  @property
  def configfilepath(self):
    return (
        cibblbibbl.data.path
        / "starplayer"
        / f'{slugify(self.Id[5:])}.json'  # exclude STAR- prefix
    )

  @property
  def getname(self):
    return self.Id[5:] # exclude STAR- prefix

  @property
  def position(self):
    return None

  @property
  def positionId(self):
    return None

  @property
  def sort_key(self):
    return (100, self.Id)

  @property
  def team(self):
    return "Star Player"

  @property
  def typechar(self):
    return "S"

  def prespp(self, matchup):
    return 0


def iterexisting():
  directory = Player.configfilepathroot()
  for p in directory.glob("**/*.json"):
    playerId = p.stem
    Pl = player(playerId)
    yield Pl


def player(playerId, **kwargs):
  playerId = str(playerId)
  if playerId.isdecimal():
    return NormalPlayer(playerId, **kwargs)
  elif playerId.startswith("MERC"):
    return MercenaryPlayer(playerId, **kwargs)
  elif playerId.startswith("STAR"):
    return StarPlayer(playerId, **kwargs)
  elif playerId.startswith("RAISED"):
    return RaisedDeadPlayer(playerId, **kwargs)
  raise NotImplementedError(f'unknown playerId: {playerId}')

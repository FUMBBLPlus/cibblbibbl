import pyfumbbl

from . import field
from . import helper

import cibblbibbl


class BasePlayer(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.CachedConfig()
  configfilename = field.filepath.idfilename
  dummy = field.config.DDField(default="no")
  Id = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = cibblbibbl.team.Team.matchups
  position = field.inst.position_by_self_positionId
  prevId = field.config.DDField(
      default = lambda i, d: i.get_prevId(),
      default_set_delete = False,
  )
  prevachievmul = field.config.DDField(default=1)
  prevdeadmatchId = field.config.DDField()
  prevreason = field.config.DDField()
  prevsppmul = field.config.DDField(default=1)
  replays = field.insts.matches_replays

  def __init__(self, playerId, name=None):
    self._matchups = {}
    self._name = name
    if name is not None:
      self._name = helper.norm_name(name)
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
    return f'{clsname}({self.Id!r}, {self.name!r})'

  __eq__ = field.ordering.eq_when_is
  __lt__ = field.ordering.PropTupCompar("sort_key")
  __le__ = field.ordering.PropTupCompar("sort_key")
  __ne__ = field.ordering.ne_when_is_not
  __gt__ = field.ordering.PropTupCompar("sort_key")
  __ge__ = field.ordering.PropTupCompar("sort_key")

  @property
  def configfilepath(self):
    return (
        cibblbibbl.data.path
        / "player"
        / self.configfilename
    )

  @property
  def name(self):
    if self._name is None:
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

  # TODO prevId setter which backchains instantly

  def get_prevId(self):
    return None


class MercenaryPlayer(BasePlayer):

  prevsppmul = field.config.DDField(default=0)
  status = field.common.Constant("Active")

  @property
  def getname(self):
    nr = self.Id.split("-")[2]
    return f'Mercenary {self.position.name} #{nr}'

  @property
  def positionId(self):
    return self.Id.split("-")[1]

  @property
  def sort_key(self):
    idvals = tuple(int(x) for x in self.Id.split("-")[1:])
    return (1000,) + idvals


class NormalPlayer(BasePlayer):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.player.get,
  )
  positionId = field.common.DiggedKeys(
      "apiget", "position", "id",
  )
  status = field.common.DiggedKeys("apiget", "status")

  @property
  def getname(self):
    if self._name is None:
      self._name = self.apiget["name"]
    return self._name

  @property
  def sort_key(self):
    return (1, int(self.Id))


Player = NormalPlayer


class RaisedDeadPlayer(BasePlayer):

  getname = field.common.DiggedAttr("prev", "getname")
  prevsppmul = field.config.DDField(default=0)

  def get_nextIds(self):
    nextId = self.Id.split("_")[-1]
    if nextId.startswith("UNKNOWN"):
      raise Exception(
          f'unchained raised dead player: {self.Id}'
      )
    elif nextId == "0":
      return set()
    return {nextId}

  @property
  def positionId(self):
    return self.Id.split("_")[0].split("-")[1]

  def get_prevId(self):
    print("get_prevId", self)
    return self.Id.split("_")[-2]

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


class StarPlayer(BasePlayer):
  config = field.config.CachedConfig()
  getname = field.common.DiggedAttr("position", "name")
  prevsppmul = field.config.DDField(default=0)
  status = field.config.DDField(default="Active")

  @property
  def configfilepath(self):
    return (
        cibblbibbl.data.path
        / "starplayer"
        / f'{self.Id}.json'
    )

  @property
  def positionId(self):
    return self.Id.split("-")[1]

  @property
  def sort_key(self):
    return (100, int(self.positionId))


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


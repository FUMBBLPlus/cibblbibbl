import pyfumbbl

from . import field
from . import helper

import cibblbibbl


class BasePlayer(metaclass=cibblbibbl.helper.InstanceRepeater):

  Id = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = cibblbibbl.team.Team.matchups
  position = field.inst.position_by_self_positionId
  replays = field.insts.matches_replays

  def __init__(self, playerId: int, name=None):
    self._matchups = {}
    self._name = name
    if name is not None:
      self._name = helper.norm_name(name)
    self.achievements = set()

  def __repr__(self):
    clsname = self.__class__.__name__
    return f'{clsname}({self.Id!r}, {self.name!r})'

  @property
  def name(self):
    if self._name is None:
      self._name = helper.norm_name(self.getname)
    return self._name



class MercenaryPlayer(BasePlayer):

  status = field.common.Constant("Active")

  @property
  def getname(self):
    nr = self.Id.split("-")[2]
    return f'Mercenary {self.position.name} #{nr}'

  @property
  def positionId(self):
    return self.Id.split("-")[1]


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


Player = NormalPlayer


class RaisedDeadPlayer(BasePlayer):

  getname = field.common.DiggedAttr("prev", "getname")

  @property
  def next(self):
    nextplayerId = self.Id.split("_")[-1]
    if nextplayerId.startswith("UNKNOWN"):
      raise Exception(
          f'uncahained raised dead player: {self.Id}'
      )
    elif nextplayerId == "0":
      return None
    else:
      return player(nextplayerId)

  @property
  def positionId(self):
    return self.Id.split("_")[0].split("-")[1]

  @property
  def prev(self):
    return player(self.Id.split("_")[-1])

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


def player(playerId, **kwargs):
  if playerId.isdecimal():
    return NormalPlayer(playerId, **kwargs)
  elif playerId.startswith("MERC"):
    return MercenaryPlayer(playerId, **kwargs)
  elif playerId.startswith("STAR"):
    return StarPlayer(playerId, **kwargs)
  elif playerId.startswith("RAISED"):
    return RaisedDeadPlayer(playerId, **kwargs)
  raise NotImplementedError(f'unknown playerId: {playerId}')


import collections
import copy

from ..jsonfile import jsonfile

import cibblbibbl


class AchievementConfig:

  def __get__(self, instance, owner):
    if instance is None:
      o = owner
    else:
      o = instance
    if o._config is ...:
      jf = jsonfile(
          self.filepath(instance, owner),
          default_data = {},
          autosave = True,
          dump_kwargs = dict(owner.dump_kwargs),
      )
      o._config = jf.data
      if o is instance and not o._config:
        o._config.update(copy.deepcopy(owner.default_config))
      return o._config

  def filepath(self, instance, owner):
    p = (
      cibblbibbl.data.path
      / owner.group_key
      / "achievement"
    )
    if instance is None:
      p /= f'{owner.__name__.lower()}.json'
    else:
      p /= f'{owner.__name__.lower()}'
      tournamentId = instance.tournamentId
      if tournamentId.isdecimal():
        p /= f'{tournamentId:0>8}'
      else:
        p /= f'{tournamentId}'
      p /= f'{instance.subjId:0>8}.json'
    return p


class Achievement:

  default_config = {"status": "proposed"}
  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    cls._config = ...

  def __init__(self,
      group_key: str,
      tournamentId: str,

      year_nr: int,
      season_nr: int,
      teamId: str,
      playerId: str,
  ):
    self._config = ...
    self._year_nr = year_nr
    self._season_nr = season_nr
    self._teamId = str(teamId)
    self._playerId = (
        str(playerId) if playerId is not None else ""
    )
    self._key = (
        self.group_key,
        self.__class__.__name__.lower(),
        self.year_nr,
        self.season_nr,
        self.teamId,
        self.playerId,
    )

  def __delitem__(self, key):
    return self.config.__delitem__(key, value)

  def __eq__(self, other):
    return (hash(self) == hash(other))

  def __ge__(self, other):
    return self._key.__ge__(other._key)

  def __getitem__(self, key):
    try:
      return self.config.__getitem__(key)
    except KeyError:
      return self.clsconfig.__getitem__(key)

  def __gt__(self, other):
    return self._key.__gt__(other._key)

  def __hash__(self):
    return hash(self._key)

  def __le__(self, other):
    return self._key.__le__(other._key)

  def __lt__(self, other):
    return self._key.__lt__(other._key)

  def __ne__(self, other):
    return (hash(self) != hash(other))

  def __setitem__(self, key, value):
    return self.config.__setitem__(key, value)

  baseprestige = cibblbibbl.config.field("prestige", default=0)

  @classproperty
  def clsconfig(cls):
    if cls._clsconfig is ...:
      cls.reload_clsconfig()
    return cls._clsconfig

  @classproperty
  def clsconfigfilepath(cls):
    p = (
        cibblbibbl.data.path
        / cls.group_key
        / "achievement"
        / f'{cls.__name__.lower()}.json'
    )
    return p

  @classmethod
  def collect(cls):
    nr = 1
    L = []
    while True:
      attrname = f'agent{nr:0>2}'
      if hasattr(cls, attrname):
        L.extend(list(getattr(cls, attrname)()))
      else:
        break
      nr += 1
    return L

  @property
  def config(self):
    if self._config is ...:
      self.reload_config()
    if not self._config:
      self._config.update(copy.deepcopy(self.default_config))
    return self._config

  @property
  def configfilepath(self):
    p = (
        self.configfilepathroot
        / f'{self.year_nr:0>3}-{self.season_nr:0>2}'
    )
    if self.playerId:
      p /= f'{str(self.teamId):0>8}'
      p /= f'{str(self.playerId):0>8}.json'
    else:
      p /= f'{str(self.teamId):0>8}.json'
    return p

  @classproperty
  def configfilepathroot(cls):
    p = (
        cibblbibbl.data.path
        / cls.group_key
        / "achievement"
        / f'{cls.__name__.lower()}'
    )
    return p

  @classproperty
  def group(cls):
    return cibblbibbl.group.Group(cls.group_key)

  @classproperty
  def group_key(cls):
    return cls._group_key

  @property
  def player(self):
    if self.playerId:
      return cibblbibbl.player.Player(self.playerId)

  @property
  def playerId(self):
    return self._playerId

  @property
  def season(self):
    return cibblbibbl.season.Season(
        self.group_key, self.year_nr, self.season_nr
  )

  @property
  def season_key(self):
    return (self.year_nr, self.season_nr)

  @property
  def season_nr(self):
    return self._season_nr

  status = cibblbibbl.config.field("status", default="proposed")

  @property
  def subjec_key(self):
    return (self.teamId, self.playerId)

  @property
  def team(self):
    return cibblbibbl.team.Team(int(self.teamId))

  @property
  def teamId(self):
    return self._teamId

  year = cibblbibbl.season.Season.year

  @property
  def year_nr(self):
    return self._year_nr

  def reload_config(self):
    jf = jsonfile(
        self.configfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(self.dump_kwargs),
    )
    self._config = jf.data

  @classmethod
  def reload_clsconfig(cls):
    jf = jsonfile(
        cls.clsconfigfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(cls.dump_kwargs),
    )
    cls._clsconfig = jf.data

  def accept(self):
    self.status = "accepted"

  def reject(self):
    self.status = "rejected"

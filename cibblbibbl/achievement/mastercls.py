import collections
import copy

from ..jsonfile import jsonfile

import cibblbibbl



class Achievement:

  registry = {}

  def __init__(self, group_key, key):
    super().__init__()
    self._group_key = group_key = str(group_key)
    self._key = key = str(key)
    self._config = ...
    Achievement.registry[(group_key, key)] = self

  config = cibblbibbl.group.config
  dump_kwargs = cibblbibbl.group.Group.dump_kwargs
  group = cibblbibbl.year.group

  @property
  def group_key(self):
    return self._group_key

  @property
  def key(self):
    return self._key

  @property
  def configfilepath(self):
    p = (
        cibblbibbl.data.path
        / self.group_key
        / "achievement"
        / f'{self.key}.json'
    )
    return p

  reload_config = cibblbibbl.matchup.reload_config



class AchievementRecord(
    metaclass=cibblbibbl.helper.InstanceRepeater
):
  def __init__(self, *args):
        # args are managed by the metaclass and _get_key()
    super().__init__()
    self._config = ...

  @staticmethod
  def _get_key(
    group_key: str,
    achiev_key: str,
    year_nr: int,
    season_nr: int,
    teamIds,
    playerId: str,
  ):
    group_key = str(group_key)
    achiev_key = str(achiev_key)
    year_nr = int(year_nr)
    season_nr = int(season_nr)
    if hasattr(teamId, "len"):
      teamIds = tuple(int(v) for v in teamId)
    else:
      teamIds = (int(TeamId),)
    playerId = str(playerId) if playerId is not None else ""
    return (
        group_key,
        achiev_key,
        year_nr,
        season_nr,
        teamIds,
        playerId,
    )

  group_key = cibblbibbl.helper.instancerepeatergetter(0)
  achiev_key = cibblbibbl.helper.instancerepeatergetter(1)
  year_nr = cibblbibbl.helper.instancerepeatergetter(2)
  season_nr = cibblbibbl.helper.instancerepeatergetter(3)
  teamIds = cibblbibbl.helper.instancerepeatergetter(4)
  playerId = cibblbibbl.helper.instancerepeatergetter(5)

  group = cibblbibbl.year.group

  @property
  def achiev(self):
    k = (self.group_key, self.achiev_key)
    return Achievement.registry[k]

  year = cibbl.season.Season.year

  @property
  def season(self):
    return cibblbibbl.season.Season(
        self.group_key, self.year_nr, self.season_nr
  )

  @property
  def team(self):
    if len(self.teamIds) == 1:
      return cibblbibbl.team.Team(self.teamIds[0])
    elif 1 < len(self.teamIds):
      return cibblbibbl.team.GroupOfTeams(self.teamIds)

  @property
  def player(self):
    return cibblbibbl.player.Player(self.playerId)




class Achievement:

  default_config = {"status": "proposed"}
  dump_kwargs = cibblbibbl.group.Group.dump_kwargs
  inst_by_season = collections.defaultdict(set)
  inst_by_subjec = collections.defaultdict(set)

  def __new__(cls, *args, **kwargs):
    self = object.__new__(cls)
      # this is weirdly needed, maybe because of the
      # @classproperty_support
    self.__init__(*args, **kwargs)  # ditto
    cls.inst_by_season[self.season_key].add(self)
    cls.inst_by_subjec[self.subjec_key].add(self)
    return self

  def __del__(self):
    i, cls = self, self.__class__
    cls.inst_by_season[self.season_key].remove(i)
    cls.inst_by_subjec[self.subjec_key].remove(i)
    return super().__del__()

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    cls._clsconfig = ...
    cls.inst_by_season = collections.defaultdict(set)
    cls.inst_by_subjec = collections.defaultdict(set)

  def __init__(self,
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

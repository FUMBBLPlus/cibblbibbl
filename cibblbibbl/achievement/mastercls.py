import collections
import copy
import math

from ..jsonfile import jsonfile

import cibblbibbl

from .. import field
from . import agent


class Achievement(metaclass=cibblbibbl.helper.InstanceRepeater):

  rank = 0

  baseprestige = field.config.DDField(key="prestige",
    get_f_typecast = int,
    set_f_typecast = lambda x: math.floor(float(x)),
  )
  config = field.config.CachedConfig()
  defaultconfig = field.config.CachedConfig()
  group = field.inst.group_by_self_group_key
  group_key = field.common.DiggedAttr("tournament", "group_key")
  registry = {}
  season = field.common.DiggedAttr("tournament", "season")
  season_nr = field.common.DiggedAttr("tournament", "season_nr")
  subject = field.instrep.keyigetterproperty(1)
  subjectId = field.common.DiggedAttr("subject", "Id")
  tournament = field.instrep.keyigetterproperty(0)
  tournamentId = field.common.DiggedAttr("tournament", "Id")
  year = field.common.DiggedAttr("tournament", "year")
  year_nr = field.common.DiggedAttr("tournament", "year_nr")

  def __init__(self, tournament, subject):
    self.tournament.achievements.add(self)
    self.subject.achievements.add(self)

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    Achievement.registry[cls.clskey()] = cls

  def __del__(self):
    try:
      self.tournament.achievements.remove(self)
    except KeyError:
      pass
    try:
      self.subject.achievements.remove(self)
    except KeyError:
      pass

  def __delitem__(self, key):
    return self.config.__delitem__(key, value)

  def __getitem__(self, key):
    try:
      return self.config.__getitem__(key)
    except KeyError:
      return self.defaultconfig.__getitem__(key)

  def __setitem__(self, key, value):
    return self.config.__setitem__(key, value)

  __lt__ = field.ordering.PropTupCompar("sort_key")
  __le__ = field.ordering.PropTupCompar("sort_key")
  __gt__ = field.ordering.PropTupCompar("sort_key")
  __ge__ = field.ordering.PropTupCompar("sort_key")

  agent00 = classmethod(agent.iterexisting)

  @classmethod
  def clskey(cls):
    return cls.__name__.lower()

  @classmethod
  def collect(cls, group_key):
    agents = tuple(sorted((
        a for a in dir(cls) if a.startswith("agent")
    ), key=lambda a: int(a[-2:])))
    return {
        A
        for a in agents
        for A in getattr(cls, a)(group_key)
    }

  @classmethod
  def defaultconfigfilepath_of_group(cls, group_key):
    return (
      cibblbibbl.data.path
      / group_key
      / "achievement"
      / f'{cls.clskey()}.json'
    )

  @classmethod
  def defaultconfig_of_group(cls, group_key):
    jf = jsonfile(
        cls.defaultconfigfilepath_of_group(group_key),
        default_data = {},
        autosave = True,
        dump_kwargs = dict(field.config.dump_kwargs),
    )
    return jf.data

  @classmethod
  def getmember(cls, tournament, subject):
    return cls.__members__.get((tournament, subject))

  @property
  def key(self):
    return self._KEY

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.tournament.group.key
      / "achievement"
      / f'{self.clskey()}'
    )
    if self.tournament.Id.isdecimal():
      p /= f'{self.tournament.Id:0>8}'
    else:
      p /= f'{self.tournament.Id}'
    p /= f'{str(self.subject.Id):0>8}.json'
    return p

  @property
  def defaultconfigfilepath(self):
    return self.defaultconfigfilepath_of_group(self.group_key)

  @property
  def sort_key(self):
    Ttimesortkeyf = cibblbibbl.tournament.tools.timesortkey()
    return (
        self.group_key,
        self.clskey(),
        self.tournament,
        self.subjectId,
    )


class TeamAchievement(Achievement):
  subject_factory = cibblbibbl.team.Team

  @classmethod
  def subjectIdcast(cls, subjectId):
    return int(subjectId)


class PlayerAchievement(Achievement):
  subject_factory = cibblbibbl.player.player
  agent99 = classmethod(agent.iterprevs)

  @classmethod
  def subjectIdcast(cls, subjectId):
    return str(subjectId)

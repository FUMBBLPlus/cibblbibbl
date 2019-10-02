import collections
import copy

from ..jsonfile import jsonfile

import cibblbibbl


class Achievement(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  registry = {}

  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init__(self, tournament, subject):
    self.tournament = tournament
    self.subject = subject
    self.tournament.achievements.add(self)
    self.subject.achievements.add(self)

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    Achievement.registry[cls.__name__.lower()] = cls

  def __del__(self):
    self.tournament.achievements.remove(self)
    self.subject.achievements.remove(self)

  def __delitem__(self, key):
    return self.config.__delitem__(key, value)

  def __getitem__(self, key):
    try:
      return self.config.__getitem__(key)
    except KeyError:
      return self.defaultconfig.__getitem__(key)

  def __setitem__(self, key, value):
    return self.config.__setitem__(key, value)

  @classmethod
  def agent00(cls, group_key):
    G = cibblbibbl.group.Group(group_key)
    dir = (
      cibblbibbl.data.path
      / group_key
      / "achievement"
      / f'{cls.__name__.lower()}'
    )
    for p in dir.glob("**/*.json"):
      tournamentId = p.parent.name
      if tournamentId.isdecimal():
        tournamentId = tournamentId.lstrip("0")
      tournament = G.tournaments[tournamentId]
      subjectId = int(p.stem)
      subject = cls.subject_type(subjectId)
      yield cls(tournament, subject)

  @classmethod
  def collect(cls, group_key):
    nr = 0
    S = set()
    while nr < 100:
      attrname = f'agent{nr:0>2}'
      if hasattr(cls, attrname):
        agentmethod = getattr(cls, attrname)
        S |= set(agentmethod(group_key))
      else:
        break
      nr += 1
    return S

  iterexisting = agent00

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.tournament.group.key
      / "achievement"
      / f'{type(self).__name__.lower()}'
    )
    if self.tournament.Id.isdecimal():
      p /= f'{self.tournament.Id:0>8}'
    else:
      p /= f'{self.tournament.Id}'
    p /= f'{str(self.subject.Id):0>8}.json'
    return p

  @property
  def config(self):
    jf = jsonfile(
        self.configfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(self.dump_kwargs),
    )
    return jf.data

  @property
  def defaultconfigfilepath(self):
    return (
      cibblbibbl.data.path
      / self.tournament.group.key
      / "achievement"
      / f'{type(self).__name__.lower()}.json'
    )

  @property
  def defaultconfig(self):
    jf = jsonfile(
        self.defaultconfigfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(self.dump_kwargs),
    )
    return jf.data

import collections
import copy

from ..jsonfile import jsonfile

import cibblbibbl

from .. import field


class Achievement(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  registry = {}

  dump_kwargs = field.config.dump_kwargs

  def __init__(self, tournament, subject):
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

  def __eq__(self, other):
    return (hash(self) == hash(other))

  def __ge__(self, other):
    return self._sortkey.__ge__(other._sortkey)

  def __getitem__(self, key):
    try:
      return self.config.__getitem__(key)
    except KeyError:
      return self.defaultconfig.__getitem__(key)

  def __gt__(self, other):
    return self._sortkey.__gt__(other._sortkey)

  def __hash__(self):
    return hash(self._KEY)

  def __le__(self, other):
    return self._sortkey.__le__(other._sortkey)

  def __lt__(self, other):
    return self._sortkey.__lt__(other._sortkey)

  def __ne__(self, other):
    return (hash(self) != hash(other))

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
  def config(self):
    jf = jsonfile(
        self.configfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(self.dump_kwargs),
    )
    return jf.data

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
  def defaultconfig(self):
    jf = jsonfile(
        self.defaultconfigfilepath,
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

  group = cibblbibbl.year.Year.group

  @property
  def group_key(self):
    return self.tournament.group_key

  @property
  def season(self):
    return self.tournament.season

  @property
  def season_nr(self):
    return self.tournament.season_nr

  @property
  def _sortkey(self):
    Ttimesortkeyf = cibblbibbl.tournament.tools.timesortkey()
    return (
        self.group_key,
        type(self).__name__.lower(),
        self.tournament,
        self.subjectId,
    )

  subject = field.instrep.keyigetterproperty(1)

  @property
  def subjectId(self):
    return self.subject.Id

  tournament = field.instrep.keyigetterproperty(0)

  @property
  def tournamentId(self):
    return self.tournament.Id

  @property
  def year(self):
    return self.tournament.year

  @property
  def year_nr(self):
    return self.tournament.year_nr

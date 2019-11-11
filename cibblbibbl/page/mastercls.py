from ..jsonfile import jsonfile

import cibblbibbl

from .. import field


class Page(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.CachedConfig()
  group = field.instrep.keyigetterproperty(0)

  def __init__(self, group, *args):
    pass

  def __delitem__(self, key):
    return self.config.__delitem__(key)

  def __getitem__(self, key):
    return self.config.__getitem__(key)

  def __setitem__(self, key, value):
    return self.config.__setitem__(key, value)

  @classmethod
  def collect(cls, group):
    agents = tuple(sorted((
        a for a in dir(cls) if a.startswith("agent")
    ), key=lambda a: int(a[-2:])))
    return {
        P
        for a in agents
        for P in getattr(cls, a)(group)
    }

  @property
  def args(self):
    return list(self._KEY[1:])

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.group.key
      / "page"
      / self.category
      / f'{"-".join(str(a) for a in self.args)}.json'
    )
    return p

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

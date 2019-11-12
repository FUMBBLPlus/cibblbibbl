from ..jsonfile import jsonfile

import cibblbibbl

from .. import field
from ..achievement.mastercls import Achievement


class Page(metaclass=cibblbibbl.helper.InstanceRepeater):

  __delitem__ = Achievement.__delitem__
  __getitem__ = Achievement.__getitem__
  __setitem__ = Achievement.__setitem__
  clskey = classmethod(Achievement.clskey.__func__)
  collect = classmethod(Achievement.collect.__func__)
  config = field.config.CachedConfig()
  defaultconfig = field.config.CachedConfig()
  defaultconfig_of_group = field.config.defcfg
  defaultconfigfilepath_of_group = field.config.defcfgfp("page")
  get = Achievement.get
  group = field.instrep.keyigetterproperty(0)

  def __init__(self, group, *args):
    pass

  @property
  def args(self):
    return list(self._KEY[1:])

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.group.key
      / "page"
      /  f'{self.clskey()}'
      / f'{"-".join(str(a) for a in self.args)}.json'
    )
    return p

  @classmethod
  def bbcodetemplatefilepath_of_group(cls, group):
    defcfgfp = cls.defaultconfigfilepath_of_group(group)
    return defcfgfp.parent / f'{defcfgfp.stem}.bbcode'

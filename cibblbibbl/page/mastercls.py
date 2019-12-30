import copy

from ..jsonfile import jsonfile

import cibblbibbl

from .. import field
from ..achievement.mastercls import Achievement


class Page(metaclass=cibblbibbl.helper.InstanceRepeater):

  __contains__ = Achievement.__contains__
  __delitem__ = Achievement.__delitem__
  __getitem__ = Achievement.__getitem__
  __setitem__ = Achievement.__setitem__
  clskey = classmethod(Achievement.clskey.__func__)
  collect = classmethod(Achievement.collect.__func__)
  config = field.config.CachedConfig()
  defaultconfig = field.config.CachedConfig()
  defaultconfig_of_group = field.config.defcfg
  defaultconfigfilepath = field.config.defcfgfp
  defaultconfigfilepath_of_group = field.config.defcfgfpofg(
      "page"
  )
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
    defcfgfpofg = cls.defaultconfigfilepath_of_group(group)
    return defcfgfpofg.parent / f'{defcfgfpofg.stem}.bbcode'

  def bbcode(self):
    templfp = self.bbcodetemplatefilepath_of_group(self.group)
    with templfp.open() as f:
      template = f.read()
    data = copy.deepcopy(self.defaultconfig._data)
    data.update(copy.deepcopy(self.config._data))
    data.update(self.pagedata())
    return template.format(**data)

  def publish_note(self):
    S = cibblbibbl.session
    if not S:
      raise Exception("fumbbl_session module was not imported")
    if not S.logged_in():
      raise Exception("fumbbl_session is not logged in")
    content_ = self.bbcode()
    content_ = content_.replace("\n", "\r\n")  # required
    note_kwargs = dict(
        note = content_,
        title = "",
        tags = str(self.group.config["notetagId"]),
        url = self.notelink(),
    )
    if "noteId" in self:
      S.note.edit(self["noteId"], **note_kwargs)
    else:
      self["noteId"] = S.note.create(**note_kwargs)

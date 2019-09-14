import pathlib

from .jsonfile import jsonfile

import cibblbibbl


dump_kwargs = dict(
    ensure_ascii = False,
    indent = "\t",
    sort_keys = True,
)


class Settings:

  def __init__(self, files):
    self.jsonfiles = []
    for fp in files:
      jf = jsonfile(fp,
          default_data = {},
          autosave = True,
          dump_kwargs = dump_kwargs,
      )
      self.jsonfiles.append(jf)

  def __delitem__(self, key):
    value, i = self._getitem_with_idx(key)
    if i is not None:
      del self.jsonfiles[i].data[key]
    else:
      raise KeyError(str(value))

  def __getitem__(self, key):
    value, i = self._getitem_with_idx(key)
    return value

  def __setitem__(self, key, value):
    self.jsonfiles[0].data[key] = value

  def _getitem_with_idx(self, key):
    for i, jf in enumerate(self.jsonfiles):
      try:
        return jf.data[key], i
      except KeyError:
        pass
    return None, None

  def refresh(self):
    for jf in self.jsonfiles:
      jf.reload()


def files(group_key=None):
  files_ = []
  if group_key is not None:
    files_.append(cibblbibbl.data.path / group_key / "settings.json")
  files_.append(cibblbibbl.data.path / "settings.json")
  return files_

def groupsettings(group_key):
  # looks for key in group settings only
  jf = jsonfile(
      cibblbibbl.data.path / group_key / "settings.json",
      default_data = {},
      autosave = True,
      dump_kwargs = dump_kwargs,
  )
  return jf.data

def settings(group_key=None):
  # looks for key in group settings first, then main settings
  files_ = files(group_key=group_key)
  s = Settings(files_)
  return s

def mainsettings():
  # looks for key in the main settings only
  jf = jsonfile(
      cibblbibbl.data.path / "settings.json",
      default_data = {},
      autosave = True,
      dump_kwargs = dump_kwargs,
  )
  return jf.data

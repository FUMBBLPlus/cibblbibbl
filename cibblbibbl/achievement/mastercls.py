import collections
import copy

from ..jsonfile import jsonfile

import cibblbibbl


class Achievement:

  default_config = {"status": "proposed"}
  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init__(self, tournament, subject):
    self.tournament = tournament
    self.subject = subject

  def __delitem__(self, key):
    return self.config.__delitem__(key, value)

  def __getitem__(self, key):
    try:
      return self.config.__getitem__(key)
    except KeyError:
      return self.defaultconfig.__getitem__(key)

  def __setitem__(self, key, value):
    return self.config.__setitem__(key, value)

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

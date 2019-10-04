import re

import pyfumbbl

from . import field

import cibblbibbl



@cibblbibbl.helper.idkey
class Coach(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.coach.get
  )

  def __init__(self, coachId: int, name: str=None):
    self._name = name
    if self._name:
      self._name = cibblbibbl.helper.norm_name(self._name)

  def __repr__(self):
    return f'Coach({self.Id}, {self.name})'

  def __str__(self):
    return self.name

  @classmethod
  def by_name(cls, name):
    term = name.lower()
    for d in pyfumbbl.coach.search(term):
      found_name = cibblbibbl.helper.norm_name(d["name"])
      if term == found_name.lower():
        return cls(int(d["id"]), name=found_name)
    else:
      raise ValueError("no matching coach")

  @property
  def name(self):
    if self._name is None:
      self._name = self.apiget["name"]
      self._name = cibblbibbl.helper.norm_name(self._name)
    return self._name



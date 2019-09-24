import re

import pyfumbbl

import cibblbibbl



@cibblbibbl.helper.idkey
class Coach(metaclass=cibblbibbl.helper.InstanceRepeater):

  def __init__(self, coachId: int, name: str=None):
    self._apiget = ...
    self._name = name
    if self._name:
      self._name = cibblbibbl.helper.norm_name(self._name)

  def __repr__(self):
    return f'Coach({self.Id}, {self.name})'

  def __str__(self):
    return self.name

  @property
  def apiget(self):
    if self._apiget is ...:
      self._apiget = pyfumbbl.coach.get(self.Id)
    return self._apiget

  @property
  def name(self):
    if self._name is None:
      self._name = self.apiget["name"]
      self._name = cibblbibbl.helper.norm_name(self._name)
    return self._name

  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.Id,
        "cache/api-match",
        pyfumbbl.match.get,
        reload=reload,
    )

  @classmethod
  def by_name(cls, name):
    term = name.lower()
    for d in pyfumbbl.coach.search(term):
      found_name = cibblbibbl.helper.norm_name(d["name"])
      if term == found_name.lower():
        return cls(int(d["id"]), name=found_name)
    else:
      raise ValueError("no matching coach")

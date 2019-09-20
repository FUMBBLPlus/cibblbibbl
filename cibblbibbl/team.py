import re

import pyfumbbl

import cibblbibbl

@cibblbibbl.helper.idkey
class Team(metaclass=cibblbibbl.helper.InstanceRepeater):

  def __init__(self, teamId: int):
    self._apiget = ...

  @property
  def apiget(self):
    if self._apiget is ...:
      self.reload_apiget()
    return self._apiget

  @property
  def name(self):
    s = self.apiget["name"]
    return cibblbibbl.helper.norm_name(s)

  @property
  def coach_name(self):
    s = self.apiget["coach"]["name"]
    return cibblbibbl.helper.norm_name(s)

  @property
  def rosterID(self):
    return self.apiget["roster"]["id"]

  @property
  def roster_name(self):
    s = self.apiget["roster"]["name"]
    s = re.sub('\s*\(.+$', '', s)
    return cibblbibbl.helper.norm_name(s)


  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.ID,
        "cache/api-team",
        pyfumbbl.team.get,
        reload=reload,
    )


class GroupOfTeams(tuple):

  def __repr__(self):
    return f'{self.__class__.__name__}{super().__repr__()}'

  @property
  def ID(self):
    return "\n".join(str(Te.ID) for Te in self)

  @property
  def name(self):
    return "\n".join(Te.name for Te in self)

  @property
  def coach_name(self):
    return "\n".join(Te.coach_name for Te in self)

  @property
  def rosterID(self):
    return "\n".join(str(Te.rosterID) for Te in self)

  @property
  def roster_name(self):
    return "\n".join(Te.roster_name for Te in self)

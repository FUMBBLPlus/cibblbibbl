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
  def roster_id(self):
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


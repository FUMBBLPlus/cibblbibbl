import re

import pyfumbbl

import cibblbibbl
import cibblbibbl._helper


class Team:

  def __init__(self, ID):
    self._ID = ID

  def __repr__(self):
    return f'Team({self._ID})'

  @property
  def ID(self):
    return self._ID

  @property
  def name(self):
    s = self.get_api_data()["name"]
    return cibblbibbl._helper.norm_name(s)

  @property
  def coach_name(self):
    s = self.get_api_data()["coach"]["name"]
    return cibblbibbl._helper.norm_name(s)

  @property
  def roster_id(self):
    return self.get_api_data()["roster"]["id"]

  @property
  def roster_name(self):
    s = self.get_api_data()["roster"]["name"]
    s = re.sub('\s*\(.+$', '', s)
    return cibblbibbl._helper.norm_name(s)


  def get_api_data(self, reload=False):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-team",
        pyfumbbl.team.get,
        reload=reload,
    )


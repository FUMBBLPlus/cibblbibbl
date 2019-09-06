import pyfumbbl

import cibblbibbl
import cibblbibbl._helper


class Match:

  def __init__(self, ID):
    self._ID = ID

  def __repr__(self):
    return f'Match({self._ID})'

  @property
  def ID(self):
    return self._ID

  def get_api_data(self):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-match",
        pyfumbbl.match.get,
    )

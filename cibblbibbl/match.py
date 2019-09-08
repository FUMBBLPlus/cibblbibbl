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

  @property
  def teams(self):
    d = self.get_api_data()
    tuple(d[f'team{n}']["id"] for n in range(1, 3))

  def get_api_data(self, reload=False):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-match",
        pyfumbbl.match.get,
        reload=reload,
    )

  def conceded(self):
    d = self.get_api_data()
    if d["conceded"] != "None":
      d2 = d[d["conceded"].lower()]
      return {k: d2[k] for k in ("id", "name")}

  def casualties(self):
    d = self.get_api_data()
    result = {}
    for n in range(1,3):
      d2 = d[f'team{n}']
      ID = d2["id"]
      cas = sum(d2["casualties"].values())
      result[ID] = cas
    return result

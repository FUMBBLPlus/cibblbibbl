import pyfumbbl

import cibblbibbl


@cibblbibbl.helper.idkey
class Match(metaclass=cibblbibbl.helper.InstanceRepeater):

  def __init__(self, matchId: int):
    self._apiget = ...

  @property
  def apiget(self):
    if self._apiget is ...:
      self.reload_apiget()
    return self._apiget

  @property
  def replayId(self):
    return self.apiget.get("replayId")

  @property
  def teams(self):
    d = self.apiget
    return tuple(
        cibblbibbl.team.Team(d[f'team{n}']["id"])
        for n in range(1, 3)
    )

  def conceded(self):
    d = self.apiget
    if d["conceded"] != "None":
      d2 = d[d["conceded"].lower()]
      return cibblbibbl.team.Team(d2["id"])

  def casualties(self):
    d = self.apiget
    result = {}
    for n in range(1,3):
      d2 = d[f'team{n}']
      Te = cibblbibbl.team.Team(d2["id"])
      cas = sum(d2["casualties"].values())
      result[Te] = cas
    return result

  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.Id,
        "cache/api-match",
        pyfumbbl.match.get,
        reload=reload,
    )

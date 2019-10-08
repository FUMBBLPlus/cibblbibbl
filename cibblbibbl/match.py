import fumbblreplay
import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Match(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.match.get, "cache/api-match"
  )
  replayId = field.common.AttrKey("apiget")

  def __init__(self, matchId: int):
    pass

  @property
  def matchup(self):
    return getattr(self, "_matchup", None)
  @matchup.setter
  def matchup(self, value):
    self._matchup = value
  @matchup.deleter
  def matchup(self):
    del self._matchup

  @property
  def replay(self):
    Re = cibblbibbl.replay.Replay(self.replayId)
    Re.match = self
    return Re

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
    result = {}
    d = self.apiget
    for n in range(1,3):
      d2 = d[f'team{n}']
      Te = cibblbibbl.team.Team(d2["id"])
      cas = sum(d2["casualties"].values())
      result[Te] = cas
    return result

  def scores(self):
    d = self.apiget
    r = {}
    for n in range(1, 3):
      Te = cibblbibbl.team.Team(int(d[f'team{n}']["id"]))
      score = int(d[f'team{n}']["score"])
      r[Te] = score
    return r


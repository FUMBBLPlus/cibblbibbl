import fumbblreplay
import pyfumbbl

import cibblbibbl


@cibblbibbl.helper.idkey
class Match(metaclass=cibblbibbl.helper.InstanceRepeater):

  def __init__(self, matchId: int):
    self._apiget = ...
    self._replaydata = ...
    self._replaygamedata = ...
    self._matchup = ...

  @property
  def apiget(self):
    if self._apiget is ...:
      self.reload_apiget()
    return self._apiget

  @property
  def replaydata(self):
    if self._replaydata is ...:
      self.reload_replaydata()
    return self._replaydata
  @replaydata.deleter
  def replaydata(self):
      # replaydata should be deleted to avoid huge memory
      # consumption
    self._replaydata = ...

  @property
  def replaygamedata(self):
    if self._replaygamedata is ...:
      for d in self.replaydata:
        try:
          self._replaygamedata = d["game"]
        except KeyError:
          pass
        else:
          break
    return self._replaygamedata
  @replaygamedata.deleter
  def replaygamedata(self):
    self._replaygamedata = ...

  @property
  def replaygameresult(self):
    d = self.replaygamedata
    return {
        s: d["gameResult"][f'teamResult{s}']._data
        for s in ("Home", "Away")
    }

  @property
  def replayId(self):
    return self.apiget.get("replayId")

  @property
  def replayteam(self):
    return {
        k: cibblbibbl.team.Team(int(d["teamId"]))
        for k, d in self.replayteamdata.items()
    }

  @property
  def replayteamside(self):
    return {
        cibblbibbl.team.Team(int(d["teamId"])): k
        for k, d in self.replayteamdata.items()
    }

  @property
  def replayteamdata(self):
    return {
        s: self.replaygamedata[f'team{s}']._data
        for s in ("Home", "Away")
    }

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

  def reload_replaydata(self, reload=False):
    filename = f'{self.replayId:0>8}.json'
    dir_path = "cache/replay"
    p = cibblbibbl.data.path / dir_path / filename
    jf = cibblbibbl.data.jsonfile(p)
    if reload or not p.is_file() or not p.stat().st_size:
      jf.dump_kwargs = cibblbibbl.settings.dump_kwargs
      print(f'REPLAY {self.Id} - {self.replayId}')
      jf.data = fumbblreplay.get_replay_data(self.replayId)
      jf.save()
    self._replaydata = jf.data

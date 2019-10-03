import fumbblreplay
import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Match(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.match.get, "cache/api-match"
  )
  replayId = field.common.DictAttrGetterNDescriptor("apiget")

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
  def replaydata(self):
    if not hasattr(self, "_replaydata"):
      self.reload_replaydata()
    return self._replaydata
  @replaydata.deleter
  def replaydata(self):
      # replaydata should be deleted to avoid huge memory
      # consumption
    if hasattr(self, "_replaydata"):
      self._replaydata.root._data = None
    del self._replaydata

  @property
  def replaygamedata(self):
    if not hasattr(self, "_replaygamedata"):
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
    del self._replaygamedata

  @property
  def replaygameresult(self):
    d = self.replaygamedata
    return {
        s: d["gameResult"][f'teamResult{s}']
        for s in ("Home", "Away")
    }

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

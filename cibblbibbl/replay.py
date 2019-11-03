import copy

import fumbblreplay
import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Replay(metaclass=cibblbibbl.helper.InstanceRepeater):

  config = field.config.CachedConfig()
  playerIdnorm = field.config.DDField(
      default=lambda i, d: i.calculate_playerIdnorm(),
      default_set_delete = False,
      delete_set_default = False,
  )

  def __init__(self, replayId: int, match=None):
    self.match = match
    pass

  def __enter__(self):
    self.reload_data()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
      del self.data

  @property
  def aliveplayers(self):
    return {
        Te: {
            cibblbibbl.player.player(playerId)
            for playerId
            in playerIds
        }
        for Te, playerIds in self.normaliveplayerIds.items()
    }

  @property
  def configfilepath(self):
    return (
        cibblbibbl.data.path
        / "replay"
        / f'{self.Id:0>8}.json'
    )

  @property
  def data(self):
    return self._data
  @data.deleter
  def data(self):
    del self._data
    self._data = ...

  @property
  def deadplayerIds(self):
    d = {}
    with self:
      for Te, d0 in self.gameresultdata.items():
        s = d[Te] = set()
        for d1 in d0["playerResults"]:
          if d1["seriousInjury"] == "Dead (RIP)":
            s.add(d1["playerId"])
    return d

  @property
  def deadplayers(self):
    return {
        Te: {
            cibblbibbl.player.player(playerId)
            for playerId
            in playerIds
        }
        for Te, playerIds in self.normdeadplayerIds.items()
    }

  @property
  def gamedata(self):
    if not hasattr(self, "_gamedata"):
      for d in self.data:
        try:
          self._gamedata = d["game"]
        except KeyError:
          pass
        else:
          break
    return self._gamedata
  @gamedata.deleter
  def gamedata(self):
    del self._gamedata

  @property
  def gameresultdata(self):
    d1 = self.gamedata
    return {
        self.teams[i]: d1["gameResult"][f'teamResult{s}']
        for i, s in enumerate(("Home", "Away"))
    }

  @property
  def normaliveplayerIds(self):
    dead = self.normdeadplayerIds
    return {
      Te: {
          playerId
          for playerId in S
          if playerId not in dead[Te]
      }
      for Te, S in self.normplayerIds.items()
    }

  @property
  def normdeadplayerIds(self):
    return {
        Te: {
            self.playerIdnorm.get(v, v) for v in deadplayerIds
        }
        for Te, deadplayerIds in self.deadplayerIds.items()
    }

  @property
  def normgameresultdata(self):
    data = copy.deepcopy(self.gameresultdata)
    for d0 in data.values():
        for d1 in d0["playerResults"]:
            for k in ("playerId", "sendToBoxByPlayerId"):
                v = d1[k]
                d1[k] = self.playerIdnorm.get(v, v)
    return data

  @property
  def normallplayerIds(self):
    return {
      self.playerIdnorm.get(playerId, playerId)
      for playerId in self.allplayerIds
    }

  @property
  def normplayerIds(self):
    return {
      Te: {
          self.playerIdnorm.get(playerId, playerId)
          for playerId in S
      }
      for Te, S in self.playerIds.items()
    }

  @property
  def normteamdata(self):
    data = copy.deepcopy(self.teamdata)
    for d0 in data.values():
        for d1 in d0["playerArray"]:
            for k in ("playerId",):
                v = playerId = d1[k]
                d1[k] = self.playerIdnorm.get(v, v)
    return data

  @property
  def allplayerIds(self):
    return {
      playerId
      for S in self.playerIds.values()
      for playerId in S
    }

  @property
  def playerIds(self):
    return {
        Te: {
            str(d1["playerId"])
            for d1 in d0["playerArray"]
        }
        for Te, d0 in self.teamdata.items()
    }

  @property
  def players(self):
    return {
        Te: {
            cibblbibbl.player.player(playerId)
            for playerId
            in playerIds
        }
        for Te, playerIds in self.normplayerIds.items()
    }

  @property
  def positiondata(self):
    d = {}
    for d0 in self.rosterdata.values():
      for d1 in d0["positionArray"]:
        positionId = d1["positionId"]
        d[positionId] = d1
    return d

  @property
  def rosterdata(self):
    d = {}
    for d0 in self.teamdata.values():
      roster = d0["roster"]
      d[roster["rosterId"]] = roster
    return d

  @property
  def teamdata(self):
    d = {}
    for s in ("Home", "Away"):
      d1 = self.gamedata[f'team{s}']
      Te = cibblbibbl.team.Team(int(d1["teamId"]))
      d[Te] = d1
    return d



  @property
  def teams(self):
    if not hasattr(self, "_teams"):
      self._teams = tuple(
          cibblbibbl.team.Team(
              int(self.gamedata[f'team{s}']["teamId"])
          )
          for s in ("Home", "Away")
      )
    return self._teams

  def reload_data(self, download=False):
    filename = f'{self.Id:0>8}.json'
    dir_path = "cache/replay"
    p = cibblbibbl.data.path / dir_path / filename
    jf = cibblbibbl.data.jsonfile(p)
    if download or not p.is_file() or not p.stat().st_size:
      jf.dump_kwargs = dict(field.config.dump_kwargs)
      print(f'Downloading REPLAY {self.Id}...')
      jf.data = fumbblreplay.get_replay_data(
          self.match.replayId
      )
      jf.save()
    self._data = jf._data

  def calculate_playerIdnorm(self):
    d = {}
    Id = self.Id
    with self:
      finished = self.gamedata["finished"]
      positiondata = self.positiondata
      for Te, d1 in self.teamdata.items():
        for d2 in d1["playerArray"]:
          playerId = normplayerId = d2["playerId"]
          playerName = d2["playerName"]
          playerType = d2["playerType"]
          positionId = d2["positionId"]
          if playerType in ("Regular", "Big Guy", "Irregular"):
            continue
          elif playerType == "Star":
            normplayerId = f'STAR-{playerName}'
          elif playerType == "Mercenary":
            normplayerId = f'MERC-{self.Id}-{playerId}'
          elif playerType == "RaisedFromDead":
            baseId = f'RAISED-{positionId}'
            aliveplayerId = playerId.split("R")[0]
            postplayerId = "UNKNOWN"
            found = Te.search_player(playerName,
                in_pastplayers = True,
            )
            if len(found) == 1:
              player = next(iter(found))
              postplayerId = player.Id
            else:
              postplayerId += f'{len(found)}'
            normplayerId = "_".join(
                (baseId, aliveplayerId, postplayerId)
            )
          else:
            raise NotImplementedError(
                "Unhandled playerType: "
                f'{playerType} (Replay: {self.Id})'
            )
          if playerId != normplayerId:
            d[playerId] = normplayerId
    return d

import cibblbibbl

from . import helper


class MatchupConfigMaker:

  callchain = (
      "Ids",
      "Excluded",
      "TeamCommon",
      "PlayerCommon",
      "PlayerPerformances",
      "DeadPlayers",
      "PlayerRetirements",
      "TeamCumPlayerPerformances",
      "TeamScores",
      "TeamCas",
      "TeamResults",
      "TeamPerformanceDiffs",
      "TeamMatchPrestiges",
  )

  diffkeys = {
      "cas",
      "score",
      "td",
  }

  spps = {
      "cas": 2,
      "comp": 1,
      "int": 2,
      "mvp": 5,
      "td": 3,
  }

  playerType_trans = {
      "Big Guy": "B",
      "Irregular": "I",
      "Journeyman": "J",  # not provided; only for reference
      "Mercenary": "M",
      "RaisedFromDead": "D",
      "Regular": "R",
      "Star": "S",
  }

  keytransPR = {
      "blocks": "blocks",
      "cas": "casualties",
      "comp": "completions",
      "fouls": "fouls",
      "int": "interceptions",
      "mvp": "playerAwards",
      "pass": "passing",
      "prespp": "currentSpps",
      "rush": "rushing",
      "td": "touchdowns",
      "turns": "turnsPlayed",
  }

  def __init__(self, matchup, *,
    direct = False,
    refresh_cache = True,
  ):
    self.Mu = matchup
    if refresh_cache:
      self.refresh_cache()
    if direct:
      self.d = matchup.config
    else:
      self.d = {
        "player": {},
        "team": {},
      }
    self.goto = "Ids"

  def refresh_cache(self):
    self.Ma = self.Mu.match
    self.G = self.Mu.group
    self.T = self.Mu.tournament
    self.SR = self.Mu.schedulerecord
    if self.Ma:
      self.teams = self.Ma.teams
      self.Re = self.Ma.replay
      with self.Re as Re:
        self.ReTD = self.Re.normteamdata
        self.ReGRD = self.Re.normgameresultdata
    else:
      self.teams = [
          cibblbibbl.team.Team(self.SR["teams"][i]["id"])
          for i in range(2)
      ]

  def __call__(self, callchain=None):
    if callchain is None:
      callchain = self.callchain
    for methodname in callchain:
      getattr(self, methodname)()
    return self.d

  def Ids(self):
    if self.Ma:
      self.d["matchId"] = str(self.Ma.Id)
      self.d["replayId"] = str(self.Ma.replayId)
    self.goto = "Excluded"

  def Excluded(self):
    excl = self.G.excluded_teams | self.T.excluded_teams
    if excl & self.Mu.teams:
      self.d["!excluded"] = "yes"
    else:
      self.d["!excluded"] = "no"

  def TeamCommon(self):
    dTe = self.d.setdefault("team", {})
    if self.Ma:
      for Te, d in self.ReTD.items():
        d1 = dTe.setdefault(str(Te.Id), {})
        d1["name"] = helper.norm_name(d["teamName"])
    else:
      for d0 in self.SR["teams"]:
        teamId = str(d0["id"])
        d1 = dTe.setdefault(teamId, {})
        d1["name"] = helper.norm_name(d0["name"])

  def PlayerCommon(self, keys=None):
    if not self.Ma:
      return
    pd = self.d["player"]
    for Te, TD in self.ReTD.items():
      ptd = pd.setdefault(str(Te.Id), {})
      for PD in TD["playerArray"]:
        playerId = str(PD["playerId"])
        ptpd = ptd.setdefault(playerId, {})
        if keys is None or "name" in keys:
          name = helper.norm_name(PD["playerName"])
          ptpd["name"] = name
        if keys is None or "type" in keys:
          ptpd["type"] = self.playerType_trans[PD["playerType"]]
          if 16 < PD["playerNr"] and ptpd["type"] == "R":
            ptpd["type"] = "J"  # must be a Journeyman

  def PlayerPerformances(self, keys=None):
    if not self.Ma:
      return
    Ks = set(self.keytransPR)
    if keys is not None:
      Ks &= set(keys)
    pd = self.d["player"]
    for Te, TGRD in self.ReGRD.items():
      ptd = pd.setdefault(str(Te.Id), {})
      for PR in TGRD["playerResults"]:
        playerId = PR["playerId"]
        ptpd = ptd.setdefault(playerId, {})
        for key in Ks:
          value = PR[self.keytransPR[key]]
          if value:
            ptpd[key] = value
        if keys is None or "spp" in keys:
          value = sum(
              ptpd.get(k, 0) * v
              for k, v in self.spps.items()
          )
          if value:
            ptpd["spp"] = value

  def DeadPlayers(self):
    if not self.Ma:
      return
    pd = self.d["player"]
    for Te, TGRD in self.ReGRD.items():
      ptd = pd.setdefault(str(Te.Id), {})
      for PR in TGRD["playerResults"]:
        playerId = PR["playerId"]
        ptpd = ptd.setdefault(playerId, {})
        if PR["seriousInjury"] == "Dead (RIP)":
          riprecord = [
              PR["sendToBoxHalf"],
              PR["sendToBoxTurn"],
              PR["sendToBoxReason"],
              PR["sendToBoxByPlayerId"],
          ]
          ptpd["dead"] = riprecord


  def PlayerRetirements(self):
    if not self.Ma:
      return
    for teamId, ptd in self.d["player"].items():
      for playerId, ptpd in ptd.items():
        playerId1 = playerId
        typ = ptpd["type"]
        if ptpd.get("dead") or typ in ("M", "S"):
          if "retired" in ptpd:
            del ptpd["retired"]
          continue
        elif typ == "D":
          playerId1 = playerId.split("_")[-1]
          if playerId1 == "0":
            ptpd["retired"] = True
            continue
        Te = cibblbibbl.team.Team(int(teamId))
        Ma = Te.next_match(self.Ma)
        if Ma:
          with Ma.replay as Re:
            if playerId1 not in Re.normallplayerIds:
              ptpd["retired"] = True
            elif "retired" in ptpd:
              del ptpd["retired"]
          continue
        elif playerId1.isdecimal():
          P = cibblbibbl.player.player(playerId1)
          status = P.status
          if P.status == "Retired":
            ptpd["retired"] = True
          elif P.status == "Retired Journeyman":
            ptpd["retired"] = True
            ptpd["type"] = "J"
          elif "retired" in ptpd:
            del ptpd["retired"]

  def TeamCumPlayerPerformances(self, keys=None):
    Ks = set(self.keytransPR) - {"cas",}
    if keys:
      Ks &= set(keys)
    for teamId, ptd in self.d["player"].items():
      d = self.d["team"].setdefault(teamId, {})
      for playerId, ptpd in ptd.items():
        for k in Ks:
          d.setdefault(k, 0)
          d[k] += ptpd.get(k, 0)

  def TeamScores(self):
    if self.Ma:
      scores = tuple(self.Ma.scores().items())
      for Te, score in scores:
        d = self.d["team"][str(Te.Id)]
        d["score"] = score
    else:
      winnerteamId = str(self.SR["result"]["winner"])
      for teamId, d in self.d["team"].items():
        if teamId == winnerteamId:
          d["score"] = 2
        else:
          d["score"] = 0

  def TeamCas(self):
    if self.Ma:
      casualties = self.Ma.casualties()
      for Te, cas_value in casualties.items():
        d = self.d["team"][str(Te.Id)]
        d["cas"] = cas_value
    else:
      for teamId, d in self.d["team"].items():
        d["cas"] = 0

  def TeamResults(self):
    if self.Ma:
      scores = tuple(
          (cibblbibbl.team.Team(int(teamId)), d["score"])
          for teamId, d in self.d["team"].items()
      )
      opposcores = {
        Te: scores[1-i][1]
        for i, (Te, score) in enumerate(scores)
      }
      conceded = self.Ma.conceded()
      for Te, score in scores:
        d = self.d["team"][str(Te.Id)]
        opposcore = opposcores[Te]
        if opposcore < score:
          d["r"] = "W"
        elif opposcore == score:
          d["r"] = "D"
        elif conceded is Te:
          d["r"] = "C"
        else:
          d["r"] = "L"
    else:
      winnerteamId = str(self.SR["result"]["winner"])
      for teamId, d in self.d["team"].items():
        if teamId == winnerteamId:
          d["r"] = "B"
        else:
          d["r"] = "F"

  def TeamPerformanceDiffs(self):
    teamIds = list(self.d["team"])
    for i, teamId in enumerate(teamIds):
      oppoteamId = teamIds[1-i]
      d = self.d["team"][teamId]
      oppod = self.d["team"][oppoteamId]
      for k in self.diffkeys:
        d[f'{k}diff'] = d.get(k, 0) - oppod.get(k, 0)

  def TeamMatchPrestiges(self):
    T = self.Mu.tournament
    for teamId, d in self.d["team"].items():
      for k in ("pts", "prestige"):
        dT = getattr(T, f'r{k}')
        d[k] = dT.get(d["r"], 0)

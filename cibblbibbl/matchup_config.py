import cibblbibbl

from . import helper


def Ids(G, T, R, Mu, D):
  Ma = Mu.match
  if Ma:
    yield "matchId", str(Ma.Id)
    yield "replayId", str(Ma.replayId)


def excluded(G, T, R, Mu, D):
  if (G.excluded_teams | T.excluded_teams) & Mu.teams:
    return "yes"
  else:
    return "no"


def player_performances(G, T, R, Mu, D):
  Ma = Mu.match
  if not Ma:
    return
  spps = {
    "cps": 1,
    "tds": 3,
    "int": 2,
    "cas": 2,
    "mvp": 5,
  }
  playerType_trans = {
    "Big Guy": "B",
    "Irregular": "I",
    "Mercenary": "M",
    "RaisedFromDead": "D",
    "Regular": "R",
    "Star": "S",
  }
  PD_k_trans = {
    "playerName": "name",
  }
  PR_k_trans = {
    "blocks": "blk",
    "casualties": "cas",
    "completions": "cps",
    "currentSpps": "prespp",
    "fouls": "fou",
    "interceptions": "int",
    "passing": "pas",
    "playerAwards": "mvp",
    "rushing": "rus",
    "touchdowns": "tds",
    "turnsPlayed": "tur"
  }
  GR = Ma.replaygameresult
  playerteam = {}
  for s_homeaway, DTE in Ma.replayteamsdata.items():
    DPD = {str(d["playerId"]): d for d in DTE["playerArray"]}
    teamId = str(DTE["teamId"])
    DGR = GR[s_homeaway]
    for PR in DGR["playerResults"]:
      playerId = PR["playerId"]
      PD = DPD[playerId]
      playerteam[playerId] = teamId
      d = {
          PR_k_trans[k]: PR[k] for k in (
              "blocks",
              "casualties",
              "completions",
              "currentSpps",
              "fouls",
              "interceptions",
              "passing",
              "playerAwards",
              "rushing",
              "touchdowns",
              "turnsPlayed",
          )
          if PR[k]
      }
      spp = sum(
          d.get(k, 0) * v
          for k, v in spps.items()
      )
      if spp:
        d["spp"] = spp
      d.update({
          PD_k_trans[k]: PD[k] for k in (
              "playerName",
          )
          if PD[k]
      })
      d["type"] = playerType_trans[PD["playerType"]]
      if PR["seriousInjury"] == "Dead (RIP)":
        riprecord = [
            PR["sendToBoxHalf"],
            PR["sendToBoxTurn"],
            PR["sendToBoxReason"],
            PR["sendToBoxByPlayerId"],
        ]
        d["died"] = riprecord
      yield teamId, playerId, d



def team_performances(G, T, R, Mu, D):
  """
  Generates the team performance dictionaries.
  """
  RR = R["result"]
  def subgen():
    if RR.get("id"):
        # having a positive Id value in a result means that
        # there was a match played
      M = cibblbibbl.match.Match(RR["id"])
      rd = {d["teamId"]: d for d in M.replayteamsdata.values()}
      conceded = M.conceded()
      casualties = M.casualties()
      for i in range(2):
        teamId = str(RR["teams"][i]["id"])
        PPL = list(D["player_performance"][teamId].values())
        Te = cibblbibbl.team.Team(int(teamId))
        d = {"name": helper.norm_name(rd[teamId]["teamName"])}
        oppo_teamId = str(RR["teams"][1-i]["id"])
        oppo_PPL = list(
            D["player_performance"][oppo_teamId].values()
        )
        oppo_Te = cibblbibbl.team.Team(int(oppo_teamId))
        score = d["score"] = RR["teams"][i]["score"]
        oppo_score = RR["teams"][1-i]["score"]
        scorediff = d["scorediff"] = score - oppo_score
        tds = d["tds"] = sum(d.get("tds", 0) for d in PPL)
        oppo_tds = sum(d.get("tds", 0) for d in oppo_PPL)
        tdsdiff = d["tdsdiff"] = tds - oppo_tds
        cas = d["cas"] = casualties[Te]
        oppo_cas = casualties[oppo_Te]
        casdiff = d["casdiff"] = cas - oppo_cas
        if 0 < scorediff:
          rsym = d["rsym"] = "W"
        elif scorediff == 0:
          rsym = d["rsym"] = "D"
        elif conceded is Te:
            # check for concessions on loosers first
          rsym = d["rsym"] = "C"
        else:
          rsym = d["rsym"] = "L"
        yield Te, d
    else:
        # a zero Id value in a result means that the game was
        # forfeited
      winner_Id = str(RR["winner"])
      teamname = {str(d["id"]): d["name"] for d in R["teams"]}
      for Te in Mu.teams:
        d = {"name": helper.norm_name(teamname[str(Te.Id)])}
        d["score"] = d["scorediff"] = 0
        d["tds"] = d["tdsdiff"] = 0
        d["cas"] = d["casdiff"] = 0
        if str(Te.Id) == winner_Id:
          rsym = d["rsym"] = "B"
        else:
          rsym = d["rsym"] = "F"
        yield Te, d
  for Te, d in subgen():
    teamId = str(Te.Id)
    for k in (
        "score",
        "scorediff",
        "tds",
        "tdsdiff",
        "cas",
        "casdiff",
      ):
      value = T.rsym.get(k, {}).get(d["rsym"], 0)
      d[k] += value
    yield teamId, d

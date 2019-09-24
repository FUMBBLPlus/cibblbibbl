import cibblbibbl


def excluded(G, T, R, Mu, D):
  if (G.excluded_teams | T.excluded_teams) & Mu.teams:
    return "yes"
  else:
    return "no"


def team_performances(G, T, R, Mu, D):
  """
  Generates the team performance dictionaries.
  """
  RR = R["result"]
  def subgen():
    if RR.get("id"):
        # having a positive ID value in a result means that
        # there was a match played
      M = cibblbibbl.match.Match(RR["id"])
      conceded = M.conceded()
      casualties = M.casualties()
      for i in range(2):
        ID = int(RR["teams"][i]["id"])
        Te = cibblbibbl.team.Team(ID)
        d = {}
        oppo_ID = int(RR["teams"][1-i]["id"])
        oppo_Te = cibblbibbl.team.Team(oppo_ID)
        score = d["score"] = RR["teams"][i]["score"]
        oppo_score = RR["teams"][1-i]["score"]
        scorediff = d["scorediff"] = score - oppo_score
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
        # a zero ID value in a result means that the game was
        # forfeited
      winner_ID = str(RR["winner"])
      for Te in Mu.teams:
        d = {}
        d["score"] = d["scorediff"] = 0
        d["cas"] = d["casdiff"] = 0
        if str(Te.ID) == winner_ID:
          rsym = d["rsym"] = "B"
        else:
          rsym = d["rsym"] = "F"
        yield Te, d
  for Te, d in subgen():
    for k in ("score", "scorediff", "cas", "casdiff"):
      value = T.rsym.get(k, {}).get(d["rsym"], 0)
      d[k] += value
    yield Te, d

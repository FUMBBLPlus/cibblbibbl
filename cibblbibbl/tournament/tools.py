import copy

import pytourney

import cibblbibbl


def iter_raw_results(T, *, follow_prev=True, from_next=False):
  C = T.get_config_data()
  if not from_next and C.get("next"):
    return
  if follow_prev and C.get("prev"):
      T2 = cibblbibbl.tournament.d_tournament[C["prev"]]
      yield from iter_raw_results(T2, from_next=True)
  filler_teams = set(cibblbibbl.data_settings["filler_teams"])
  li = []
  for S in T.get_api_schedule_data():
    team = {d["id"]: d["name"] for d in S["teams"]}
    if set(team) & filler_teams:
      continue
    R = S["result"]
    if R.get("id"):
      M = cibblbibbl.match.Match(R["id"])
      conceded = M.conceded()
      casualties = M.casualties()
      for i in range(2):
        ID = int(R["teams"][i]["id"])
        oppo_ID = int(R["teams"][1-i]["id"])
        name = team[ID]
        score = R["teams"][i]["score"]
        oppo_score = R["teams"][1-i]["score"]
        tdd = score - oppo_score
        cas = casualties[ID]
        oppo_cas = casualties[oppo_ID]
        casd = cas - oppo_cas
        if 0 < tdd:
          key = "W"
        elif tdd == 0:
          key = "D"
        elif conceded and ID == int(conceded["id"]):
          key = "C"
        else:
          key = "L"
        yield ID, name.strip(), key, tdd, casd
    else:
      winner_ID = int(R["winner"])
      tdd = 0
      casd = 0
      for ID, name in team.items():
        if ID == winner_ID:
          key = "B"
        else:
          key = "F"
        yield ID, name.strip(), key, tdd, casd


def results_for_hth(T):
  filler_teams = set(cibblbibbl.data_settings["filler_teams"])
  li = []
  for S in T.get_api_schedule_data():
    r_teams = S["result"]["teams"]
    if set(int(d["id"]) for d in r_teams) & filler_teams:
      continue
    if S["result"].get("id"):
      ID1 = int(r_teams[0]["id"])
      ID2 = int(r_teams[1]["id"])
      score1 = r_teams[0]["score"]
      score2 = r_teams[1]["score"]
      li.append({ID1: score1, ID2: score2})
  return li


def standings_base(T):
  key_point = T.key_point()
  d = {}
  for t in iter_raw_results(T):
    ID, name, key, tdd, casd = t
    if ID in d:
      d2 = d[ID]
      d2["perf"] += key
      d2["tdd"] += tdd
      d2["casd"] += casd
      d2["pts"] += key_point[key]
    else:
      d[ID] = d2 = {}
      d2["id"] = ID
      d2["name"] = name
      d2["perf"] = key
      d2["tdd"] = tdd
      d2["casd"] = casd
      d2["pts"] = key_point[key]
    d2["hth"] = -1
    d2["coin"] = -1
  # TODO:custom perf
  IDs = sorted(d, key=lambda id_: (
      -d[id_]["pts"], -d[id_]["tdd"], -d[id_]["casd"]
  ))
  return [d[ID] for ID in IDs]


def standings_tieb(T):
  r0_hth = results_for_hth(T)
  B = standings_base(T)
  B = copy.copy(B)
  if not B:
    return B
  rows = {d["id"]: d for d in B}
  hth = {}
  curr_hth_teams = set()
  pts0 = B[0]["pts"]
  def apply_hth():
    r1_hth = team_results_for_hth(r0_hth, *curr_hth_teams)
    hth = pytourney.tie.hth.calculate(r1_hth)
    for ID, hth_val in hth.items():
        rows[int(ID)]["hth"] = hth_val
  for r in B:
    pts1 = r["pts"]
    if pts1 == pts0:
      curr_hth_teams.add(r["id"])
    else:
      apply_hth()
      curr_hth_teams = {r["id"]}
      pts0 = pts1
  else:
    apply_hth()
  return sorted(B, key=T.standings_keyf)


def team_results_for_hth(results_for_hth, *team_IDs):
  team_IDs = set(team_IDs)
  li = [{str(ID): 0} for ID in team_IDs]  # ensure nodes
  for r0 in results_for_hth:
    r1 = {
        str(ID): score
        for ID, score in r0.items()
        if ID in team_IDs
    }
    if 1 < len(r1.keys()):
      li.append(r1)
  return li

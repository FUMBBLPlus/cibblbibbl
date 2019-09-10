import copy
import itertools

import pytourney

import cibblbibbl


def iter_raw_results(T, *, follow_prev=True, from_next=False):
  C = T.get_config_data()
  key_casd = T.key_casd()
  key_tdd = T.key_tdd()
  excluded_teams = T.excluded_teams(with_fillers=True)
  if not from_next and C.get("next"):
    return
  if follow_prev and C.get("prev"):
      T2 = cibblbibbl.tournament.d_tournament[C["prev"]]
      yield from iter_raw_results(T2, from_next=True)
  li = []
  for S in T.get_api_schedule_data():
    team = {d["id"]: d["name"] for d in S["teams"]}
    if set(team) & excluded_teams:
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
        tdd += key_tdd.get(key, 0)
        casd += key_casd.get(key, 0)
        yield ID, name.strip(), key, tdd, casd
    else:
      winner_ID = int(R["winner"])
      for ID, name in team.items():
        if ID == winner_ID:
          key = "B"
        else:
          key = "F"
        tdd = key_tdd.get(key, 0)
        casd = key_casd.get(key, 0)
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
  C = T.get_config_data()
  CS = C.get("standings", {})
  key_pts = T.key_pts()
  d = {}
  for t in iter_raw_results(T):
    ID, name, key, tdd, casd = t
    if ID in d:
      d2 = d[ID]
      d2["perf"] += key
      d2["tdd"] += tdd
      d2["casd"] += casd
    else:
      d[ID] = d2 = {}
      d2["id"] = ID
      d2["name"] = name
      d2["perf"] = key
      d2["tdd"] = tdd
      d2["casd"] = casd
    d2["hth"] = -1  # these are not yet resolved
    d2["coin"] = -1
  for ID, d2 in d.items():
    CST = CS.get(str(ID), {})
    # custom values override the calculated ones
    for k in ("perf", "tdd", "casd", "hth", "coin"):
      cst_val = CST.get(k)
      if cst_val is not None:
        d2[k] = cst_val
    cst_pts = CST.get("pts")
    if cst_pts is not None:
      d2["pts"] = cst_pts
    else:
      d2["pts"] = sum(key_pts.get(key, 0) for key in d2["perf"])
  IDs = C.get("order")
  if IDs is None:
    key_f = (lambda ID, d=d: T.standings_keyf(d, ID))
    IDs = sorted(d, key=key_f)
  return [d[ID] for ID in IDs]


def standings_tieb(T):
  C = T.get_config_data()
  CS = C.get("standings", {})
  r0_hth = results_for_hth(T)
  B = standings_base(T)
  B = copy.copy(B)
  if not B:
    return B
  d = {d_["id"]: d_ for d_ in B}
  hth = {}
  curr_hth_teams = set()
  pts0 = B[0]["pts"]
  def apply_hth():
    r1_hth = team_results_for_hth(r0_hth, *curr_hth_teams)
    hth = pytourney.tie.hth.calculate(r1_hth)
    for ID, hth_val in hth.items():
        CST = CS.get(str(ID), {})  # apply custom if set
        cst_hth = CST.get("hth")
        if cst_hth is not None:
          d[int(ID)]["hth"] = cst_hth
        else:
          d[int(ID)]["hth"] = hth_val
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
  IDs = C.get("order")
  if IDs is None:
    key_f = (lambda ID, d=d: T.standings_keyf(d, ID))
    IDs = sorted(d, key=key_f)
  return [d[ID] for ID in IDs]


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

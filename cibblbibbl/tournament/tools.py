import cibblbibbl


def iter_raw_results(T):
  li = []
  for S in T.get_api_schedule_data():
    team = {d["id"]: d["name"] for d in S["teams"]}
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
        yield ID, name, key, tdd, casd
    else:
      winner_ID = int(R["winner"])
      tdd = 0
      casd = 0
      for ID, name in team.items():
        if ID == winner_ID:
          key = "B"
        else:
          key = "F"
        yield ID, name, key, tdd, casd


def first_pass_standings(T):
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
  IDs = sorted(d, key=lambda id_: (
      -d[id_]["pts"], -d[id_]["tdd"], -d[id_]["casd"]
  ))
  return [d[ID] for ID in IDs]


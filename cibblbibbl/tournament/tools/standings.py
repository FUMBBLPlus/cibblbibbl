import collections
import copy
import itertools

import pytourney

import cibblbibbl


def base(T):
  R = cibblbibbl.tournament.tools.results
  d = {}
  for i, t in enumerate(R.individual(T)):
    if t.team in d:
      d2 = d[t.team.ID]
      d2["perf"] += t.rsym
      d2["matches"].append(t.match)
      d2["tdd"] += t.tdd
      d2["casd"] += t.casd
    else:
      d[t.team.ID] = d2 = {}
      d2["team"] = t.team
      d2["perf"] = t.rsym
      d2["matches"] = [t.match,]
      d2["tdd"] = t.tdd
      d2["casd"] = t.casd
    d2["hth"] = -1  # these are not yet resolved
    d2["coin"] = -1
  return list(d.values())


def base_revised(T):
  L = base(T)
  d = {d_["team"].ID: d_ for d_ in L}
  CS = T.config.get("standings", {})
  for ID, d2 in d.items():
    CST = CS.get(str(ID), {})
    # custom values override the calculated ones
    for k in ("perf", "tdd", "casd", "hth", "coin"):
      try:
        cst_val = CST[k]
      except KeyError:
        pass
      else:
        d2[k] = cst_val
    try:
      cst_matches = CST["matches"]
    except KeyError:
      pass
    else:
      d2["matches"] = [
          (None if m is None else cibblbibbl.match.Match(m))
          for m in cst_matches
      ]
    try:
      cst_pts = CST["pts"]
    except KeyError:
      d2["pts"] = sum(
          T.rsym_pts.get(rsym, 0) for rsym in d2["perf"]
      )
    else:
      d2["pts"] = cst_pts
  IDs = CS.get("order")
  if IDs is None:
    key_f = (lambda ID, d=d: T.standings_keyf(d, ID))
    IDs = sorted(d, key=key_f)
  return [d[ID] for ID in IDs]


def tiebroken(T):
  R = cibblbibbl.tournament.tools.results
  CS = T.config.get("standings", {})

  def apply_hth():
    r1_hth = list(R.hth_group(r0_hth, *curr_hth_teams))
    hth = pytourney.tie.hth.calculate(r1_hth)
    for ID, hth_val in hth.items():
        CST = CS.get(str(ID), {})  # apply custom if set
        cst_hth = CST.get("hth")
        if cst_hth is not None:
          d[int(ID)]["hth"] = cst_hth
        else:
          d[int(ID)]["hth"] = hth_val

  r0_hth = list(R.hth_all(T))
  L = base_revised(T)
  if not L:
    return L
  d = {d_["team"].ID: d_ for d_ in L}
  hth = {}
  curr_hth_teams = set()
  pts0 = L[0]["pts"]
  for r in L:
    pts1 = r["pts"]
    if pts1 == pts0:
      curr_hth_teams.add(r["team"].ID)
    else:
      apply_hth()
      curr_hth_teams = {r["team"].ID}
      pts0 = pts1
  else:
    apply_hth()
  # determine missing coin toss
  key_rows = collections.defaultdict(list)
  for ID, d2 in d.items():
    key_val = T.standings_keyf(d, ID)
    key_rows[key_val].append(d2)
  miscoin_keyv = {k for k in key_rows if 1 < len(key_rows[k])}
  for k in miscoin_keyv:
    for d2 in key_rows[k]:
      d2["coin"] = -112  # indicate missing
  # sort
  IDs = CS.get("order")
  if IDs is None:
    return [d2 for k in sorted(key_rows) for d2 in key_rows[k]]
  else:
    return [d[ID] for ID in IDs]
    retun
    key_f = (lambda ID, d=d: T.standings_keyf(d, ID))
    IDs = sorted(d, key=key_f)
  return [d[ID] for ID in IDs]


def export(standings):
  L = copy.deepcopy(standings)
  for d in L:
    d["id"] = d["team"].ID
    d["name"] = d["team"].name  # to help human admin
    del d["team"]
    if d.get("matches"):
      d["matches"] = [
          (None if M is None else M.ID) for M in d["matches"]
      ]
  return L


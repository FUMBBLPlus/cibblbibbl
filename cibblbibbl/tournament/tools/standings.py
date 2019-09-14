import copy
import itertools

import pytourney

import cibblbibbl


def base(T):
  S = T.config.get("standings", {})
  rsym_pts = T.rsym["pts"]

  d = {}
  for i, t in enumerate(individual(T)):
    if t.team in d:
      d2 = d[t.team.ID]
      d2["perf"] += t.rsym
      d2["tdd"] += t.tdd
      d2["casd"] += t.casd
    else:
      d[t.team.ID] = d2 = {}
      d2["team"] = t.team
      d2["perf"] = t.rsym
      d2["tdd"] = t.tdd
      d2["casd"] = t.casd

    d2["hth"] = -1  # these are not yet resolved
    d2["coin"] = -1


  for ID, d2 in d.items():
    CST = S.get(str(ID), {})
    # custom values override the calculated ones
    for k in ("perf", "tdd", "casd", "hth", "coin"):
      cst_val = CST.get(k)
      if cst_val is not None:
        d2[k] = cst_val
    cst_pts = CST.get("pts")
    if cst_pts is not None:
      d2["pts"] = cst_pts
    else:
      d2["pts"] = sum(rsym_pts.get(rsym, 0) for rsym in d2["perf"])
  IDs = C.get("order")
  if IDs is None:
    key_f = (lambda ID, d=d: T.standings_keyf(d, ID))
    IDs = sorted(d, key=key_f)
  return [d[ID] for ID in IDs]


def standings_tieb(T):
  C = T.get_config_data()
  CS = C.get("standings", {})
  r0_hth = hth_all(T)
  B = base(T)
  B = copy.copy(B)
  if not B:
    return B
  d = {d_["id"]: d_ for d_ in B}
  hth = {}
  curr_hth_teams = set()
  pts0 = B[0]["pts"]
  def apply_hth():
    r1_hth = hth_group(r0_hth, *curr_hth_teams)
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

import collections
import copy
import itertools

import pytourney

import cibblbibbl


def base(T):
  iter_pos = itertools.chain(T.ppos, itertools.repeat(0))
  S = T.standings
  P = []
  for Sr in S:
    Pr = {k: Sr[k] for k in ("team", "perf")}
    gam = 0
    if T.season.name != "Winter":
      for rsym in Pr["perf"]:
        gam += T.rsym_prestige.get(rsym, 0)
    Pr["gam"] = gam
    Pr["pos"] = next(iter_pos)
    if Sr["cto"] == -112:  # handle missing coin toss
      Pr["pos"] = "?"
      Pr["p"] = "?"
    else:
      Pr["p"] = sum(Pr[k] for k in ("gam", "pos"))
    P.append(Pr)
  return P

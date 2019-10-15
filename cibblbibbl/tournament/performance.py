import copy

import cibblbibbl


extraperformancekeys = {
    "Blocking Thrower",
    "Blocking Scorer",
    "Scoring Thrower",
    "Triple",
    "Allrounder",
}

performancekeytrans = {
    "Blocks": "blocks",
    "Casualties": "cas",
    "Completions": "comp",
    "Fouls": "fouls",
    "Interceptions": "int",
    "MVP": "mvp",
    "Pass": "pass",
    "Rush": "rush",
    "SPP": "spp",
    "Touchdowns": "td",
    "Turns": "turns",
}

performancekeytransback = {
    "blocks": "Blocks",
    "cas": "Casualties",
    "comp": "Completions",
    "fouls": "Fouls",
    "int": "Interceptions",
    "mvp": "MVP",
    "pass": "Pass",
    "rush": "Rush",
    "spp": "SPP",
    "td": "Touchdowns",
    "turns": "Turnms",
}

def bestperformers(performances, extraperformances_=None):
  if extraperformances_ is None:
    extraperformances_ = extraperformances(performances)
  d = {}
  perf = performances
  if perf:
    for K, k in performancekeytrans.items():
      topval = max(d[k] for d in perf.values())
      L = [Sj for Sj, d1 in perf.items() if d1[k] == topval]
      if len(L) == 1:
        d[K] = L[0]
      else:
        d[K] = None
  eperf = extraperformances_
  if eperf:
    for K in extraperformancekeys:
      topval = max(d[K] for d in eperf.values())
      L = [Sj for Sj, d1 in eperf.items() if d1[K] == topval]
      if len(L) == 1:
        d[K] = L[0]
      else:
        d[K] = None
  return d


def extraperformances(performances, join=False):
  d = {}
  for Subject, d0 in performances.items():
    if join:
      dt = d[Subject] = copy.deepcopy(d0)
    else:
      dt = d[Subject] = {}
    dt["Blocking Thrower"] = min(d0["cas"], d0["comp"])
    dt["Blocking Scorer"] = min(d0["cas"], d0["td"])
    dt["Scoring Thrower"] = min(d0["td"], d0["comp"])
    dt["Triple"] = min(d0["td"], d0["cas"], d0["comp"])
    dt["Allrounder"] = min(
        d0["td"], d0["cas"], d0["comp"], d0["int"]
    )
  return d


def trans(performances, transmap=None):
  if transmap is None:
    transmap = performancekeytransback
  perf = {}
  for Sj, d1 in performances.items():
    d2 = {
        transmap.get(key, key): value
        for key, value in d1.items()
    }
    perf[Sj] = d2
  return perf

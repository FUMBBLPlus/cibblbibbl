import collections
import json
import pathlib

import cibblbibbl


def filepath(T):
  root0 = cibblbibbl.settings["cibblbibbl-data.path"]
  root = pathlib.Path(root0)
  filepath0 = getattr(T, "filepath", None)
  if not filepath0:
    filename = f'{T.ID:0>8}.json'
    filepath0 = f'{T.group_key}/tournament/config/{filename}'
  filepath = root / filepath0
  return filepath



def init(T):
  p = filepath(T)
  if p.is_file() and p.stat().st_size:
    with p.open(encoding="utf8") as f:
      o = json.load(f)
    T.config = o
  else:
    return {}


def excluded_teams(T, with_fillers=False):
  C = T.config
  S = set(C.get("excluded", []))
  nextID = C.get("next")
  if nextID is not None:
    nextT = cibblbibbl.tournament.byID[nextID]
    S |= excluded_teams(nextT, with_fillers=with_fillers)
  if with_fillers:
    S |= set(cibblbibbl.settings.get("filler_teams", []))
  return S


def standings(T):
  C = T.config
  CS0 = C.get("standings", {})
  #CS = for sID, d in CS0.items() if sID.isdecimal()

import pathlib

import cibblbibbl
import pyfumbbl

from . import tools
from . import handler

tournament = {}
d_tournament = {}


def init(group_key):
  data_path = cibblbibbl.settings["cibblbibbl-data.path"]
  seasons = tuple(cibblbibbl.data_settings["seasons"])
  li = tournament[group_key] = []
  group_settings = getattr(
      cibblbibbl, f'data_{group_key}_settings'
  )
  _group_id = group_settings["groupId"]
  for d in pyfumbbl.group.tournaments(_group_id):
    ID = d["id"]
    handlervaluefile = f'group_key/tournament/handler/{ID}'
    p = pathlib.Path(data_path) / handlervaluefile
    p_exists = (p.is_file() and p.stat().st_size)
    if p_exists:
      with p.open(encoding="ascii") as f:
        handlername = f.read()
    else:
      handlername = "default"
    handler_ = getattr(handler, handlername)
    T = handler_.init(group_key, ID)
    li.append(T)
    d_tournament[ID] = T

import pathlib

import cibblbibbl
import pyfumbbl

from . import tools
from . import handler

tournament = {}


def init(groupname):
  data_path = cibblbibbl.settings["cibblbibbl-data.path"]
  seasons = tuple(cibblbibbl.settings["cibblbibbl.seasons"])
  li = tournament[groupname] = []
  _group_id = cibblbibbl.settings["cibbl.groupId"]
  for d in pyfumbbl.group.tournaments(_group_id):
    ID = d["id"]
    handlervaluefile = f'tournament/handler/{ID}'
    p = pathlib.Path(data_path) / handlervaluefile
    p_exists = (p.is_file() and p.stat().st_size)
    if p_exists:
      with p.open(encoding="ascii") as f:
        handlername = f.read()
    else:
      handlername = "default"
    handler_ = getattr(handler, handlername)
    li.append(handler_.init(ID))

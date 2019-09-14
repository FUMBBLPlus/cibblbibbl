import pathlib

import cibblbibbl
import pyfumbbl

from . import tools
from . import handler

byGroup = {}
byID = {}


def init(group_key):
  data_path = cibblbibbl.data.path
  S = cibblbibbl.settings.settings(group_key)
  G = cibblbibbl.settings.groupsettings(group_key)
  seasons = tuple(S["seasons"])
  gt = byGroup.setdefault(group_key, {})
  for groupId in G.get("groupIds", []):
    for d in pyfumbbl.group.tournaments(groupId):
      ID = d["id"]
      handlervaluefile = f'group_key/tournament/handler/{ID}'
      p = cibblbibbl.data.path / handlervaluefile
      p_exists = (p.is_file() and p.stat().st_size)
      if p_exists:
        handlername = cibblbibbl.data.jsonfile(p).data
      else:
        handlername = "default"
      handler_ = getattr(handler, handlername)
      T = handler_.init(group_key, ID)
      gt[ID] = T
      byID[ID] = T

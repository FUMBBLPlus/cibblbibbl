import pathlib

import cibblbibbl
import pyfumbbl

from . import tools
from . import handler
from . import export

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
      ID = str(d["id"])
      handler_ = handler.get_handler(group_key, ID)
      T = handler_.init(group_key, ID)
      gt[ID] = T
      byID[ID] = T
  for ID in S.get("Abstract Tournaments", []):
    handler_ = handler.get_handler(group_key, ID)
    T = handler_.init(group_key, ID)
    gt[ID] = T
    byID[ID] = T

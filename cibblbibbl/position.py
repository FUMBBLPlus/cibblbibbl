import re

import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Position(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.position.get, "cache/api-position"
  )
  name = field.common.AttrKey("apiget", "title")
  rosterId = field.common.AttrKey("apiget", "roster")

  def __init__(self, positionId: int):
    pass

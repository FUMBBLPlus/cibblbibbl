import re

import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Roster(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.roster.get, "cache/api-roster"
  )

  def __init__(self, rosterId: int):
    pass

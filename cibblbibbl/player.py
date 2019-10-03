import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Player(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.player.get,
  )

  def __init__(self, playerId: int):
    self.achievements = set()

  @property
  def status(self):
    return self.apiget()["status"]

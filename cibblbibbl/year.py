from . import field


import cibblbibbl


class Year(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  achievements = field.insts.self_tournament_achievements
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = field.insts.self_tournaments_matchups
  nr = field.instrep.keyigetterproperty(1)
  replays = field.insts.matches_replays

  def __init__(self, group_key, nr:int):
    self.seasons = set()
    self.tournaments = {}

  @property
  def next(self):
    key = (self.group_key, self.nr + 1)
    return self.__class__.__members__.get(key)

  @property
  def prev(self):
    key = (self.group_key, self.nr - 1)
    return self.__class__.__members__.get(key)

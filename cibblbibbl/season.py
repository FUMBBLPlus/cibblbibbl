from . import field


import cibblbibbl


class Season(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  achievements = field.insts.self_tournament_achievements
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = field.insts.self_tournaments_matchups
  nr = field.instrep.keyigetterproperty(2)
  replays = field.insts.matches_replays
  year = field.inst.year_by_self_group_key_and_year_nr
  year_nr = field.instrep.keyigetterproperty(1)

  def __init__(self, group_key, year_nr:int, nr:int):
    self.tournaments = {}

  @property
  def name(self):
    seasons = self.group.config["seasons"]
    return seasons[self.nr - 1]

  @property
  def next(self):
    key = (self.group_key, self.year_nr, self.nr + 1)
    next = self.__class__.__members__.get(key)
    if next is None and self.year.next:
      next = sorted(self.year.next.seasons)[0]
    return next

  @property
  def prev(self):
    key = (self.group_key, self.year_nr, self.nr - 1)
    prev = self.__class__.__members__.get(key)
    if prev is None and self.year.prev:
      prev = sorted(self.year.prev.seasons)[-1]
    return prev

  def since(self, season):
    """
    Returns how many seasons has been passed since the given
    season including itself. The result is positive if the
    given season was earlier.
    """
    c = 0
    if season._KEY[1:] < self._KEY[1:]:
      while season is not self:
        season = season.next
        c += 1
    elif self._KEY[1:] < season._KEY[1:]:
      while season is not self:
        season = season.prev
        c -= 1
    return c

  def until(self, season):
    """
    Returns how many seasons has been passed until the given
    season including itself. The result is positive if the
    given season was later.
    """
    return -self.since(season)


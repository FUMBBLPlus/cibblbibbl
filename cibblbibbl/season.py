import cibblbibbl


class Season(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, group_key, year_nr:int, nr:int):
    self._matchups = ...
    self.tournaments = {}

  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key
  matchups = cibblbibbl.group.Group.matchups

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
  def nr(self):
    return self._KEY[2]

  @property
  def prev(self):
    key = (self.group_key, self.year_nr, self.nr - 1)
    prev = self.__class__.__members__.get(key)
    if prev is None and self.year.prev:
      prev = sorted(self.year.prev.seasons)[-1]
    return prev

  @property
  def year(self):
    return cibblbibbl.year.Year(
        self.group_key, self.year_nr
  )

  @property
  def year_nr(self):
    return self._KEY[1]

  def since(self, season):
    """
    Returns how many seasons has been passed since the given
    season including itself. The result is positive if the
    given season was earlier.
    """
    c = 0
    if season.KEY[1:] < self._KEY[1:]:
      while season is not self:
        season = season.next
        c += 1
    elif self._KEY[1:] < season.KEY[1:]:
      while season is not self:
        season = season.prec
        c -= 1
    return c

  def until(self, season):
    """
    Returns how many seasons has been passed until the given
    season including itself. The result is positive if the
    given season was later.
    """
    return -self.since(season)


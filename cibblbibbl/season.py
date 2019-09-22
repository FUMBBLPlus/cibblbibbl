import cibblbibbl


class Season(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, group_key, year_nr:int, nr:int):
    self.tournaments = {}

  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key
  matchups = cibblbibbl.group.Group.matchups

  @property
  def name(self):
    seasons = self.group.settings["seasons"]
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

  itermatchups = cibblbibbl.group.Group.itermatchups

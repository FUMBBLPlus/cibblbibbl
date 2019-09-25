import cibblbibbl


class Year(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, group_key, nr:int):
    self._matchups = ...
    self.seasons = set()
    self.tournaments = {}

  @property
  def group(self):
    return cibblbibbl.group.Group(self.group_key,
      register_tournaments=False,  # avoid infinite loop
    )

  @property
  def group_key(self):
    return self._KEY[0]

  matchups = cibblbibbl.group.Group.matchups

  @property
  def next(self):
    key = (self.group_key, self.nr + 1)
    return self.__class__.__members__.get(key)

  @property
  def nr(self):
    return self._KEY[1]

  @property
  def prev(self):
    key = (self.group_key, self.nr - 1)
    return self.__class__.__members__.get(key)

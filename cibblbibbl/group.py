import pyfumbbl

import cibblbibbl


class Group(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, key: str, init_tournaments=True):
    self.years = set()
    self.seasons = set()
    self.tournaments = set()
    if init_tournaments:
       self.reload_tournaments()

  def __repr__(self):
    return (self.__class__.__name__ + "(" +
        ", ".join(f'{a!r}' for a in self._KEY) + ")")

  @property
  def key(self):
    return self._KEY[0]

  @property
  def season_names(self):
    return tuple(self.settings["seasons"])

  @property
  def settings(self):
    return cibblbibbl.settings.groupsettings(self.key)

  def reload_tournaments(self):
    GS = self.settings
    seasons = tuple(GS["seasons"])
    get_handler_f = cibblbibbl.tournament.handler.get_handler
    for groupId in GS.get("groupIds", []):
      for d in pyfumbbl.group.tournaments(groupId):
        ID = str(d["id"])
        handler_ = get_handler_f(self.key, ID)
        T = handler_.init(self.key, ID)
        self.tournaments.add(T)
        self.years.add(T.year)
        self.seasons.add(T.season)
    for ID in GS.get("abstract_tournaments", []):
      handler_ = get_handler_f(self.key, ID)
      T = handler_.init(self.key, ID)
      self.tournaments.add(T)
      self.years.add(T.year)
      self.seasons.add(T.season)

import pyfumbbl

import cibblbibbl

from .. import tools



class BaseTournament:

  def __init__(self, group_key, ID):
    self._config = None

  @property
  def config(self):
    if self._config is None:
      self.reload_config()
    return self._config

  @property
  def group_key(self):
    return self._KEY[0]

  @property
  def ID(self):
    return self._KEY[1]

  @property
  def next(self):
    ID = self.config.get("next")
    if ID is not None:
      return cibblbibbl.tournament.byGroup[self.group_key][ID]
  @next.setter
  def next(self, T):
    assert T.group_key == self.group_key
    assert T.ID != self.ID
    self.config["next"] = T.ID
    T.config["prev"] = self.ID
  @next.deleter
  def next(self):
    T = cibblbibbl.tournament.byGroup[self.group_key][self.next]
    assert T.group_key == self.group_key
    assert T.config["prev"] == self.ID
    del self.config["next"], T.config["prev"]

  ppos = tools.config.field("ppos")

  @property
  def prev(self):
    ID = self.config.get("prev")
    if ID is not None:
      return cibblbibbl.tournament.byGroup[self.group_key][ID]
  @prev.setter
  def prev(self, T):
    T.next = self
  @prev.deleter
  def prev(self):
    T = cibblbibbl.tournament.byGroup[self.group_key][self.prev]
    del T.next

  def filepath(self, key):
    if isinstance(self.ID, int):
      filename = f'{self.ID:0>8}.json'
    else:
      filename = f'{self.ID}.json'
    p = cibblbibbl.data.path
    p /= f'{self.group_key}/tournament/{key}/{filename}'
    return p

  def reload_config(self):
    dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf = cibblbibbl.data.jsonfile(
        self.filepath("config"),
        default_data = {},
        autosave=True,
        dump_kwargs=dump_kwargs
    )
    self._config = jf.data

  def standings_keyf(self, d, ID):
    row = d[ID]
    return (
      -row["pts"],
      +row["hth"],
      -row["tdd"],
      -row["casd"],
      -row["coin"]
  )



class AbstractTournament(BaseTournament):

  name = tools.config.field("name")

  @property
  def season(self):
    s = self.config["season"]
    if s and isinstance(s, list) and len(s) == 2:
      t = cibblbibbl.tournament.tools.types.Season
      return t(s)
  season = season.setter(tools.config.setter("season"))
  season = season.deleter(tools.config.deleter("season"))

  year = tools.config.field("year")




class Tournament(
    BaseTournament,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self, group_key, ID):
    super().__init__(group_key, ID)
    self._apiget = None
    self._apischedule = None
    self._season = None
    self._standings = None

  def __repr__(self):
    return f'Tournament({self.group_key!r},{self.ID!r})'

  @property
  def apiget(self):
    if self._apiget is None:
      self.reload_apiget()
    return self._apiget

  @property
  def apischedule(self):
    if self._apischedule is None:
      self.reload_apischedule()
    return self._apischedule

  @property
  def season(self):
    if self._season is None:
      self.reload_season()
    return self._season

  @property
  def status(self):
    return self.apiget["status"]

  @property
  def style(self):
    style_idx = int(self.apiget["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year(self):
    return self.config.get("year") or int(self.apiget["season"])
  year = year.setter(tools.config.setter("year"))
  year = year.deleter(tools.config.deleter("year"))

  @property
  def schedule(self):
    return self.apischedule

  @property
  def standings(self):
    if self._standings is None:
      self.reload_standings()
    return self._standings

  def excluded_teams(self, with_fillers=False):
    s = set(self.config.get("excluded", []))
    nextID = self.config.get("next")
    if nextID is not None:
      gt = cibblbibbl.tournament.byGroup[self.group_key]
      nextT = gt[nextID]
      s |= nextT.excluded_teams()
    if with_fillers:
      S = cibblbibbl.settings.settings(self.group_key)
      s |= set(S.get("filler_teams", []))
    return s

  @property
  def name(self):
    return self.config.get("name") or self.apiget["name"]
  name = name.setter(tools.config.setter("name"))
  name = name.deleter(tools.config.deleter("name"))


  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.ID,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
        reload=reload,
    )

  def reload_apischedule(self, reload=False):
    self._apischedule = cibblbibbl.helper.get_api_data(
        self.ID,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
        reload=reload,
    )

  def reload_season(self):
    t = cibblbibbl.tournament.tools.types.Season
    if self.config.get("season"):
      self._season = t(*self.config["season"])
      return
    S = cibblbibbl.settings.settings(self.group_key)
    seasons = tuple(S["seasons"])
    lowname = self.name.lower()
    for n, s in reversed(list(enumerate(seasons, 1))):
      if s.lower() in lowname:
        self._season = t(n, s)
        return
    self._season = t(None, "")

  rsym_casd = tools.config.field("rsym_casd", {
      "B": 0,
      "b": 0,
      "F": 0,
  })

  def reload_standings(self):
    self._standings = tools.standings.tiebroken(self)
    dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf = cibblbibbl.data.jsonfile(
        self.filepath("standings"),
        data = tools.standings.export(self._standings),
        default_data = {},
        autosave=True,
        dump_kwargs=dump_kwargs
    )

  @property
  def rsym_pts(self):
    rsym_pts_ = self.config.get("rsym_pts")
    if not rsym_pts_:
      if self.season.name == "Summer":
        rsym_pts_ = {
          "W": 2,
          "D": 1,
          "B": 2,
        }
      else:
        rsym_pts_ = {
          "W": 3,
          "D": 1,
          "B": 3,
        }
    return rsym_pts_
  rsym_pts = rsym_pts.setter(tools.config.setter("rsym_pts"))
  rsym_pts = rsym_pts.deleter(tools.config.deleter("rsym_pts"))

  rsym_prestige = tools.config.field("rsym_prestige", {
      "W": 3,
      "B": 3,
      "D": 1,
      "C": -10,
  })

  rsym_tdd = tools.config.field("rsym_tdd", {
      "B": 2,
      "b": -2,
      "F": -2,
  })





def init(group_key, ID):
  return Tournament(group_key, ID)

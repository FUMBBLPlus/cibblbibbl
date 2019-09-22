import copy

import pyfumbbl

import cibblbibbl

from .. import tools



class BaseTournament:

  def __init__(self, group_key, ID):
    self._config = None

  def __repr__(self):
    clsname = self.__class__.__name__
    return f'{clsname}({self.group_key!r},{self.ID!r})'

  @property
  def config(self):
    if self._config is None:
      self.reload_config()
    return self._config

  @property
  def group(self):
    return cibblbibbl.group.Group(self.group_key,
      init_tournaments=False,  # avoid infinite loop
    )

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
      d = cibblbibbl.tournament.byGroup[self.group_key]
      return d[str(ID)]
  @next.setter
  def next(self, T):
    assert T.group_key == self.group_key
    assert T.ID != self.ID
    self.config["next"] = T.ID
    T.config["prev"] = self.ID
  @next.deleter
  def next(self):
    d = cibblbibbl.tournament.byGroup[self.group_key]
    T = d[str(self.next)]
    assert T.group_key == self.group_key
    assert T.config["prev"] == self.ID
    del self.config["next"], T.config["prev"]

  ppos = tools.config.field("ppos")

  @property
  def prev(self):
    ID = self.config.get("prev")
    if ID is not None:
      d = cibblbibbl.tournament.byGroup[self.group_key]
      return d[str(ID)]
  @prev.setter
  def prev(self, T):
    T.next = self
  @prev.deleter
  def prev(self):
    d = cibblbibbl.tournament.byGroup[self.group_key]
    T = d[str(self.prev)]
    del T.next

  @property
  def sortID(self):
    return self.config.get("sortID") or int(self.ID)
  sortID = sortID.setter(tools.config.setter("sortID"))
  sortID = sortID.deleter(tools.config.deleter("sortID"))

  @property
  def season(self):
    season_name = self.config["season"]
    season_nr = self.group.season_names.index(season_name) + 1
    return cibblbibbl.season.Season(
        self.group.key, self.year.nr, season_nr
    )
  @season.setter
  def season(self, season):
    if hasattr(season, "nr"):
      assert season.group is self.group
      assert season.year is self.year
    else:
      season_lownames = tuple(
          s.lower() for s in self.group.season_names
      )
      if hasattr(season, "isdecimal") and season.isdecimal():
        assert season <= len(season_lownames)
        season = cibblbibbl.season.Season(
          self.group.key, self.year.nr, int(season)
        )
      elif hasattr(season, "lower"):
        season = season.lower()
        try:
          season_i = season_lownames.index(season)
        except ValueError:
          raise ValueError(f'season not found: {season!r}')
        else:
          season_nr = season_i + 1
        season = cibblbibbl.season.Season(
          self.group.key, self.year.nr, season_nr
        )
      else:
        raise ValueError(f'season not found: {season!r}')
    self.config["season"] = season.name
  season = season.deleter(tools.config.deleter("season"))

  @property
  def year(self):
    yearnr = self.config["year"]
    return cibblbibbl.year.Year(self.group.key, int(yearnr))
  @year.setter
  def year(self, year_or_yearnr):
    Y = year_or_yearnr
    if hasattr(Y, "nr"):
      assert Y.group is self.group
      yearnr = Y.nr
    else:
      yearnr = int(Y)
    self.config["year"] = yearnr
  year = year.deleter(tools.config.deleter("year"))



  def filepath(self, key):
    if self.ID.isdecimal():
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
      -row["cad"],
      -row["cto"]
  )



class AbstractTournament(BaseTournament):

  name = tools.config.field("name")



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
  def name(self):
    return self.config.get("name") or self.apiget["name"]
  name = name.setter(tools.config.setter("name"))
  name = name.deleter(tools.config.deleter("name"))

  @property
  def schedule(self):
    return self.apischedule

  @property
  def season(self):
    season_name = self.config.get("season")
    season_names = self.group.season_names
    if season_name is None:
      tournament_name = self.name.lower()
      gen = reversed(list(enumerate(season_names, 1)))
          # I go reversed as I want a Spring/Summer tournament
          # to be handled as Summer
      for season_nr, season_name in gen:
        if season_name.lower() in tournament_name:
          self.season = season_name
              # I want to save it in the config
          return self.season  # will be returned from the config
      else:
        raise Exception(f'season not found for {self}')
    else:
      season_nr = season_names.index(season_name) + 1
      return cibblbibbl.season.Season(
          self.group.key, self.year.nr, season_nr
      )
  season = season.setter(BaseTournament.season.fset)
  season = season.deleter(BaseTournament.season.fdel)

  @property
  def standings(self):
    if self._standings is None:
      self.reload_standings()
    return self._standings

  @property
  def status(self):
    return self.apiget["status"]

  @property
  def style(self):
    style_idx = int(self.apiget["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year(self):
    yearnr = (self.config.get("year") or self.apiget["season"])
    return cibblbibbl.year.Year(self.group_key, int(yearnr))
  year = year.setter(BaseTournament.year.fset)
  year = year.deleter(BaseTournament.year.fdel)


  def excluded_teams(self, with_fillers=False):
    s = set(self.config.get("excluded", []))
    nextID = self.config.get("next")
    if nextID is not None:
      gt = cibblbibbl.tournament.byGroup[self.group_key]
      nextT = gt[str(nextID)]
      s |= nextT.excluded_teams()
    if with_fillers:
      S = cibblbibbl.settings.settings(self.group_key)
      s |= set(S.get("filler_teams", []))
    return s

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

  rsym_cad = tools.config.field("rsym_cad", {
      "B": 0,
      "b": 0,
      "F": 0,
  })

  @property
  def rsym_prestige(self):
    rsym_prestige_ = self.config.get("rsym_prestige")
    if rsym_prestige_ is None:
      rsym_prestige_ = {}
      if self.season.name != "Winter":
        rsym_prestige_ = {
            "W": 3,
            "B": 3,
            "D": 1,
            "C": -10,
        }
    return rsym_prestige_
  rsym_prestige = rsym_prestige.setter(
      tools.config.setter("rsym_prestige")
  )
  rsym_prestige = rsym_prestige.deleter(
      tools.config.deleter("rsym_prestige")
  )

  @property
  def rsym_pts(self):
    rsym_pts_ = self.config.get("rsym_pts")
    if rsym_pts_ is None:
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

  rsym_tdd = tools.config.field("rsym_tdd", {
      "B": 2,
      "b": -2,
      "F": -2,
  })





def init(group_key, ID):
  return Tournament(group_key, ID)

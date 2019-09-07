import json
import pathlib

import pyfumbbl

import cibblbibbl
import cibblbibbl._helper


class BaseTournament:

  def __init__(self, ID):
    self._ID = ID

  def __repr__(self):
    return f'Tournament({self._ID})'

  @property
  def ID(self):
    return self._ID

  @property
  def name(self):
    return self.get_api_data()["name"]

  @property
  def season(self):
    name = self.name.lower()
    seasons = tuple(cibblbibbl.settings["cibblbibbl.seasons"])
    for s in seasons:
      if s.lower() in name:
        return s
    return ""

  @property
  def season_nr(self):
    seasons = tuple(cibblbibbl.settings["cibblbibbl.seasons"])
    season = self.season
    if season:
      return seasons.index(season) + 1

  @property
  def status(self):
    return self.get_api_data()["status"]

  @property
  def style(self):
    style_idx = int(self.get_api_data()["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year(self):
    return int(self.get_api_data()["season"])

  def get_api_data(self):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
    )

  def get_api_schedule_data(self):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
    )

  def get_config_data(self):
    p = self._config_data_path()
    if p.is_file() and p.stat().st_size:
      with p.open(encoding="utf8") as f:
        o = json.load(f)
      return o
    else:
      return {}

  def set_config_data(self, o):
    p = self._config_data_path()
    with p.open("w", encoding="utf8") as f:
      json.dump(
        o,
        f,
        ensure_ascii = False,
        indent = "\t",
        sort_keys = True,
      )

  def _config_data_path(self):
    filename = f'{self.ID:0>8}.json'
    data_path = cibblbibbl.settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= f'tournament/config/{filename}'
    return p


class Tournament(BaseTournament):

  default_key_point = {
    "W": 3,
    "D": 1,
    "L": 0,
    "C": 0,
    "B": 3,
    "F": 0,
  }

  default_key_prestige = {
    "W": 3,
    "D": 1,
    "L": 0,
    "C": -10,
    "B": 0,
    "F": 0,
  }

  def matches(self):
    return tuple(
      cibblbibbl.match.Match(S["result"]["id"])
      for S in self.get_api_schedule_data()
      if S["result"].get("id")
    )

  def key_point(self):
    c = self.get_config_data()
    return c.get("key_point") or self.default_key_point

  def key_prestige(self):
    c = self.get_config_data()
    return c.get("key_prestige") or self.default_key_prestige

def init(ID):
  return Tournament(ID)

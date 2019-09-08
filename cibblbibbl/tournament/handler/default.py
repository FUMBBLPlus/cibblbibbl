import json
import pathlib
import warnings

from tabulate import tabulate

import pyfumbbl

import cibblbibbl
import cibblbibbl._helper


class BaseTournament:

  def __init__(self, group_key, ID):
    self._group_key = group_key
    self._ID = ID

  def __repr__(self):
    return f'Tournament({self._group_key},{self._ID})'

  @property
  def group_key(self):
    return self._group_key

  @property
  def ID(self):
    return self._ID

  @property
  def name(self):
    return self.get_api_data()["name"]

  @property
  def season(self):
    name = self.name.lower()
    seasons = tuple(cibblbibbl.data_settings["seasons"])
    for s in reversed(seasons):
      if s.lower() in name:
        return s
    return ""

  @property
  def season_nr(self):
    seasons = tuple(cibblbibbl.data_settings["seasons"])
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

  def calculate_standings(self):
    return cibblbibbl.tournament.tools.standings_tieb(self)

  def get_api_data(self, reload=False):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
        reload=reload,
    )

  def get_api_schedule_data(self, reload=False):
    return cibblbibbl._helper.get_api(
        self.ID,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
        reload=reload,
    )

  def get_config_data(self):
    p = self._config_data_path()
    if p.is_file() and p.stat().st_size:
      with p.open(encoding="utf8") as f:
        o = json.load(f)
      return o
    else:
      return {}

  def get_standings_data(self, reload=False, save=True):
    p = self._standings_data_path()
    if not reload and p.is_file() and p.stat().st_size:
      with p.open(encoding="utf8") as f:
        S = json.load(f)
      return S
    else:
      S = self.calculate_standings()
      if save:
        self.set_standings_data(S)
      return S

  def matches(self):
    return tuple(
      cibblbibbl.match.Match(S["result"]["id"])
      for S in self.get_api_schedule_data()
      if S["result"].get("id")
    )

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

  def set_standings_data(self, S):
    p = self._standings_data_path()
    with p.open("w", encoding="utf8") as f:
      json.dump(
        S,
        f,
        ensure_ascii = False,
        indent = "\t",
        sort_keys = True,
      )

  def standings(self, check_for_coin_toss=True):
    S = self.get_standings_data()
    if check_for_coin_toss:
      li = self._coin_toss_missing(S)
      for IDs in li:
        s = "Coin toss missing for "
        s += f'{self.name}: {", ".join(str(ID) for ID in IDs)}'
        warnings.warn(s)
      p = self._cointoss_data_path()
      if li:
        with p.open("w", encoding="utf8") as f:
          json.dump(
            li,
            f,
            ensure_ascii = False,
            indent = "\t",
            sort_keys = True,
          )
      elif p.is_file():
        p.unlink()
    return S

  def _coin_toss_missing(self, S):
    li = []
    key_rows = {}
    for d in S:
      key_rows.setdefault(self.standings_keyf(d), []).append(d)
    for li2 in key_rows.values():
      if 1 < len(li2):
        li.append(sorted(r["id"] for r in li2))
    return li

  def _cointoss_data_path(self):
    filename = f'{self.ID:0>8}.cointoss.json'
    data_path = cibblbibbl.settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= f'{self.group_key}/tournament/standings/{filename}'
    return p

  def _config_data_path(self):
    filename = f'{self.ID:0>8}.json'
    data_path = cibblbibbl.settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= f'{self.group_key}/tournament/config/{filename}'
    return p

  def _standings_data_path(self):
    filename = f'{self.ID:0>8}.json'
    data_path = cibblbibbl.settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= f'{self.group_key}/tournament/standings/{filename}'
    return p


class Tournament(BaseTournament):

  @staticmethod
  def standings_keyf(row):
    d = row
    return (
      -d["pts"], d["hth"], -d["tdd"], -d["casd"], -d["coin"]
  )

  def key_point(self):
    c = self.get_config_data()
    key_point = c.get("key_point")
    if not key_point:
      if self.season == "Summer":
        key_point = {
          "W": 2,
          "D": 1,
          "L": 0,
          "C": 0,
          "B": 2,
          "b": 0,
          "F": 0,
        }
      else:
        key_point = {
          "W": 3,
          "D": 1,
          "L": 0,
          "C": 0,
          "B": 3,
          "b": 0,
          "F": 0,
        }
    return key_point

  def key_prestige(self):
    c = self.get_config_data()
    key_prestige = c.get("key_prestige")
    if not key_prestige:
      key_prestige = {
        "W": 3,
        "D": 1,
        "L": 0,
        "C": -10,
        "B": 0,
        "F": 0,
      }
    return key_prestige

  def standings_text(self, tablefmt=None):
    S = self.standings()
    if not S:
      return ""
    hth_trans = {-1: "", 0: "--"}
    coin_trans = {-1: ""}
    cointoss_team_IDs = {
        ID
        for li in self._coin_toss_missing(S)
        for ID in li
    }
    rows = []
    headers = (
        "Name",
        "Roster",
        "Coach",
        "Perf.",
        "PTS",
        "HTH",
        "TDD",
        "CASD",
        "COIN",
    )
    colalign=(
      "left",
      "left",
      "left",
      "left",
      "right",
      "right",
      "right",
      "right",
      "right",
    )
    for r in S:
      Te = cibblbibbl.team.Team(r["id"])
      ct_str = ("(!) " if r["id"] in cointoss_team_IDs else "")
      row = [
          ct_str + Te.name,
          Te.roster_name,
          Te.coach_name,
          r["perf"],
          r["pts"],
          hth_trans.get(r["hth"], r["hth"]),
          r["tdd"],
          r["casd"],
          coin_trans.get(r["coin"], r["coin"]),
      ]
      rows.append(row)
    tabulate_s = tabulate(
        rows,
        colalign=colalign,
        headers=headers,
        tablefmt=tablefmt,
    )
    return f'Standings of {self.name} (#{self.ID})' \
        f'\n\n{tabulate_s}'


def init(group_key, ID):
  return Tournament(group_key, ID)

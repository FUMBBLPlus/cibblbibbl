import datetime

import pyfumbbl

import cibblbibbl


class Matchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  dump_kwargs = cibblbibbl.group.Group.dump_kwargs

  def __init__(self,
      group_key: str,
      tournamentID: str,
      round: int,
      low_teamID:int,
      high_teamID:int,
  ):
    self._config = None

  @property
  def apischedulerecord(self):
    this_team_ids = self._KEY[3:5]
    for d in self.tournament.apischedule:
      team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
      if team_ids == this_team_ids:
        return d

  @property
  def config(self):
    if self._config is None:
      self.reload_config()
    if not self._config:
      self.update_config()
    return self._config

  @property
  def created(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["created"], fmt)

  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key

  @property
  def highlightedteam(self):
    d = self.apischedulerecord
    teamID = d.get("result", {}).get("winner")
    if teamID:
      return cibblbibbl.team.Team(teamID)

  @property
  def match(self):
    d = self.apischedulerecord
    matchID = d.get("result", {}).get("id")
    if matchID:
      return cibblbibbl.match.Match(matchID)

  @property
  def modified(self):
    fmt = "%Y-%m-%d %H:%M:%S"
    d = self.apischedulerecord
    return datetime.datetime.strptime(d["modified"], fmt)

  @property
  def position(self):
    return self.apischedulerecord["position"]

  @property
  def round(self):
    return self._KEY[2]

  @property
  def season(self):
    return self.tournament.season

  @property
  def teams(self):
    return frozenset(
        cibblbibbl.team.Team(teamID)
        for teamID in self._KEY[3:5]
    )

  @property
  def tournament(self):
    return self.group.tournaments[str(self._KEY[1])]

  @property
  def year(self):
    return self.tournament.year

  def calculate_config(self):
    D = {}
    G = self.group
    T = self.tournament
    d = self.apischedulerecord
    if (G.excluded_teams | T.excluded_teams) & self.teams:
      D["excluded"] = "yes"
    else:
      D["excluded"] = "no"
    def subgen():  # generates the team performance dictionaries
      if d["result"].get("id"):
          # having a positive ID value in a result means that
          # there was a match played
        M = cibblbibbl.match.Match(d["result"]["id"])
        conceded = M.conceded()
        casualties = M.casualties()
        for i in range(2):
          ID = int(d["result"]["teams"][i]["id"])
          D2 = D[str(ID)] = {}
          Te = cibblbibbl.team.Team(ID)
          oppo_ID = int(d["result"]["teams"][1-i]["id"])
          oppo_Te = cibblbibbl.team.Team(oppo_ID)
          score = D2["score"] = d["result"]["teams"][i]["score"]
          oppo_score = d["result"]["teams"][1-i]["score"]
          scorediff = score - oppo_score
          cas = D2["cas"] = casualties[Te]
          oppo_cas = casualties[oppo_Te]
          casdiff = cas - oppo_cas
          if 0 < scorediff:
            rsym = D2["rsym"] = "W"
          elif scorediff == 0:
            rsym = D2["rsym"] = "D"
          elif conceded is Te:
              # check for concessions on loosers first
            rsym = D2["rsym"] = "C"
          else:
            rsym = D2["rsym"] = "L"
          yield D2
      else:
          # a zero ID value in a result means that the game was
          # forfeited
        winner_ID = str(d["result"]["winner"])
        for Te in self.teams:
          D2 = D[str(Te.ID)] = {"score": 0, "cas": 0}
          if str(Te.ID) == winner_ID:
            rsym = D2["rsym"] = "B"
          else:
            rsym = D2["rsym"] = "F"
          yield D2
    for D2 in subgen():
      scorediff = T.rsym_scorediff.get(D2["rsym"], 0)
      D2["scorediff"] = scorediff
      D2["score"] += scorediff
      casdiff = T.rsym_casdiff.get(D2["rsym"], 0)
      D2["casdiff"] = casdiff
      D2["cas"] += casdiff
    return D

  def reload_config(self):
    filename = (
        f'{self.round:0>2}'
        f'-{self._KEY[3]:0>7}'
        f'-{self._KEY[4]:0>7}'
        ".json"
    )
    tournamentID = str(self._KEY[1])
    if tournamentID.isdecimal():
      tournament_dir = f'{tournamentID:0>8}'
    else:
      tournament_dir = tournamentID
    filepath = (
        cibblbibbl.data.path
        / "matchup"
        / tournament_dir
        / filename
    )
    jf = cibblbibbl.data.jsonfile(
        filepath,
        default_data = {},
        autosave=True,
        dump_kwargs=dict(self.dump_kwargs)
    )
    self._config = jf.data

  def update_config(self):
    if self._config is None:
      self.reload_config()
    self._config.root.data.update(self.calculate_config())

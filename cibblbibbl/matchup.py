import datetime

import pyfumbbl

import cibblbibbl


class Matchup(metaclass=cibblbibbl.helper.InstanceRepeater):

  def __init__(self,
      group_key: str,
      tournamentID: str,
      round: int,
      low_teamID:int,
      high_teamID:int,
  ):
    pass

  @property
  def apischedulerecord(self):
    this_team_ids = self._KEY[3:5]
    for d in self.tournament.apischedule:
      team_ids = tuple(sorted(d2["id"] for d2 in d["teams"]))
      if team_ids == this_team_ids:
        return d

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
    return tuple(
        cibblbibbl.team.Team(teamID)
        for teamID in self._KEY[3:5]
    )

  @property
  def tournament(self):
    return self.group.tournaments[str(self._KEY[1])]

  @property
  def year(self):
    return self.tournament.year

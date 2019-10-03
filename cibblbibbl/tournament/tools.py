import cibblbibbl

DEFAULT_TIMESORTKEY_STATUSMAP = {
    "Completed": 0,
    "In Progress": 10,
    "Unknown": 100,
}

def exclude_team(tournament, team):
  if not hasattr(team, "Id"):
    team = cibblbibbl.team.Team(int(team))

  for Mu in tournament.matchups:
    if team in Mu.teams:
      Mu.excluded = "yes"


def timesortkey(statusmap=None):
  if statusmap is None:
    statusmap = DEFAULT_TIMESORTKEY_STATUSMAP
  return (
      lambda inst, statusmap=statusmap:
      (statusmap[inst.status], inst.end, inst.Id)
  )

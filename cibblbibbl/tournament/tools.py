import cibblbibbl

def exclude_team(tournament, team):
  if not hasattr(team, "Id"):
    team = cibblbibbl.team.Team(int(team))

  for Mu in tournament.matchups:
    if team in Mu.teams:
      Mu.excluded = "yes"

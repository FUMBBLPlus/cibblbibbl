import cibblbibbl


reasontrans = {
    "bomb": "bombed",
    "chainsaw": "sawed",
    "dodgeFail": "tackled",
}


def alreadyearned(A, season=None):
  season = season or A.season
  As = sorted(
      A1 for A1 in A.subject.achievements
      if type(A1) is type(A)
  )
  i = As.index(A)
  if 0 < i:
    return " (Achievement already earned)"
  else:
    return ""


def idpart(A, show_Ids):
  if show_Ids:
    return f'[{A.subject.Id}] '
  else:
    return ""


def oppoteam(A, *, team_=None):
  team_ = team_ or team(A)
  if not hasattr(team_, "Id"):
    return ""
  else:
    return [Te1 for Te1 in A.match.teams if Te1 is not team_][0]


def reason(reason):
  return reasontrans.get(reason, reason)


def team(A, Pl=None):
  Pl = Pl or A.subject
  if isinstance(Pl, cibblbibbl.player.StarPlayer):
    return "Star Player"
  elif isinstance(Pl, cibblbibbl.player.MercenaryPlayer):
    return "Mercenary"
  dRPP = A.tournament.rawplayerperformances()
  return dRPP[Pl]["team"]

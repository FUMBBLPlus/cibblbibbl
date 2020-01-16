import cibblbibbl


reasontrans = {
    "ballAndChain": " hit {0} with a ball and chain",
    "bitten": " has bitten {0}",
    "blocked": " blocked {0}",
    "bomb": " hit {0} with a bomb",
    "chainsaw": " hit {0} with a chainsaw",
    "crowdPushed": " pushed {0} into the crowd",
    "dodgeFail": " tackled {0}",
    "eaten": " ate {0}",
    "fireball": " hit {0} with a fireball",
    "fouled": " fouled {0}",
    "hitByThrownPlayer": " hit {0} with self",
    "lightning": " hit {0} with a lightning",
    "piledOn":  " piled upon {0}",
    "stabbed": " stabbed {0}",
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
  elif Pl.team:
    return Pl.team
  rootA = A
  exc = None
  while rootA is not None:
    dRPP = rootA.tournament.rawplayerperformances()
    try:
      return dRPP[Pl]["team"]
    except Exception as exc_:
      exc = exc_
      rootA = A.prev
  raise exc


def teamofmatch(A, Pl=None):
  Pl = Pl or A.subject
  return A.match.matchup.team_of_player(Pl)

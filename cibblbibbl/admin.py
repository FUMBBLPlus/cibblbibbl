import cibblbibbl

missingkiller_map = {
    ("ballAndChain", False): True,
    ("ballAndChain", True): False,
    ("blocked", True): False,
    ("bomb", False): True,
    ("chainsaw", False): True,
    ("chainsaw", True): False,
    ("crowdPushed", False): True,
    ("dodgeFail", False): False,
    ("eaten", False): True,
    ("fireball", False): False,
    ("fouled", True): False,
    ("gfiFail", False): False,
    ("hitByRock", False): False,
    ("landingFail", False): False,
    ("leapFail", False): False,
    ("lightning", False): False,
    ("secretWeaponBan", False): True,
    ("stabbed", True): False,
  }

def missingkiller():
  n = 1
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    for Mu in G.matchups:
      for t in Mu.iterdead():
        teamId, playerId, dpp = t
        dead = dpp["dead"]
        half, turn, reason, killerId = dead
        key = (reason, bool(killerId))
        if not missingkiller_map[key]:
          continue
        matchId = Mu.match.Id
        replayId = Mu.match.replayId
        T = Mu.tournament
        Te = cibblbibbl.team.Team(int(teamId))
        teamName = Te.name
        playerName = dpp["name"]
        print(
            f'{n}.  '
            f'{Mu.configdir.stem}/{Mu.configfilename}  '
            f'Team-{teamId} Player-{playerId} '
            f'H{half}T{turn} {reason}'
        )
        n += 1

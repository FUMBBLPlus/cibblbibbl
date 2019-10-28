import cibblbibbl

missingkiller_map = {
    "ballAndChain": True,
    "bomb": True,
    "chainsaw": True,
    "crowdPushed": True,
    "dodgeFail": False, # historically awarded
    "eaten": True,
    "fireball": False,
    "gfiFail": False,
    "hitByRock": False,
    "landingFail": False,
    "leapFail": False,
    "lightning": False,
    "secretWeaponBan": True,
  }

def missingkiller():
  n = 1
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    for Mu in G.matchups:
      for t in Mu.iterdead():
        teamId, playerId, dpp = t
        dead = dpp["dead"]
        half, turn, reason, killerId = dead._data
        if bool(killerId):
          continue
        if not missingkiller_map[reason]:
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

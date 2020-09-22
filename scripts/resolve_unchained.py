import cibblbibbl


def chain_player(playerId, Mu, Te):
  print("UNCHAINED PLAYER!")
  print(f'PlayerID: {playerId}')
  print(f'Team: {Te}')
  T = Mu.group.tournaments[Mu.tournamentId]
  Ma = Mu.match
  Re = Ma.replay
  d1_found = False
  with Re:
    invplayerIdnorm = {
      k2: k1 for k1, k2 in Re.playerIdnorm.items()
    }
    try:
      orig_playerId1 = invplayerIdnorm[playerId]
    except KeyError:
      print(
        f'WARNING! Not in Replay ID norm config: {playerId}'
      )
    else:
      orig_playerId2 = orig_playerId1.split("R")[0]
      for OrigTe, d0 in Re.teamdata.items():
        for d1 in d0["playerArray"]:
          if d1["playerId"] == orig_playerId2:
            d1_found = True
            break
        if d1_found:
          break
  if d1_found:
    print(
      f'Original Player: [{orig_playerId1}] {d1["playerName"]}'
    )
    print(f'Original Team = {OrigTe}')
  print(f'Tournament: {T};  Round: {Mu.keys[0]}')
  print(f'MatchId: {Ma.Id}')
  print(f'ReplayId: {Re.Id}')
  newplayerId = input(f'Next Player Id (0 if none): ')
  newplayerId1 = "_".join(
    playerId.split("_")[:-1] + [newplayerId,]
  )
  print(f'New PlayerID: {newplayerId1}')
  if d1_found:
    Re.playerIdnorm[orig_playerId1] = newplayerId1
  d0 = Mu.config["player"][str(Te.Id)][playerId]
  del Mu.config["player"][str(Te.Id)][playerId]
  if newplayerId == "0":
    d0["retired"] = True
  Mu.config["player"][str(Te.Id)][newplayerId1] = d0
  print()


def main():
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    G.register_tournaments()

    for Mu in G.matchups:
      self = Mu # method part copied below
      # COPY of Mu.players
      RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
      PP_items = self.config["player"].items()
      S = set()
      for teamId, d0 in PP_items:
        Te = cibblbibbl.team.Team(int(teamId))
        for playerId, d1 in list(d0.items()):
          try:
            Pl = cibblbibbl.player.player(playerId)
          except cibblbibbl.player.UnchainedPlayerException:
            chain_player(playerId, Mu, Te)


if __name__ == "__main__":
  main()

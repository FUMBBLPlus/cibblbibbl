import cibblbibbl


def main():
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    print()
    G.register_tournaments()
    G.register_matchups()
    Se = max(G.seasons)
    n = 1
    for Mu in Se.matchups:
      Ma = Mu.match
      if not Ma:
        continue
      for teamId, d0 in Mu.config["player"].items():
        Te = cibblbibbl.team.Team(teamId)
        for playerId, d1 in d0.items():
          if not playerId.startswith("STAR-"):
            continue
          name = d1["name"]
          li_dead = d1.get("dead")
          if not li_dead:
            continue
          half, turn, reason, killerId = li_dead
          print(f'=== {n}. ===')
          n += 1
          print(f'Star Player: {name}')
          print(f'Team: {Te}')
          print(f'Matchup: {Mu}')
          print(f'Match: https://fumbbl.com/p/match?id={Ma.Id}')
          healed = "x"
          while healed.lower() not in ("", "y", "n"):
            healed = input(
              "Was the Star Player healed? "
              "(Y/N; ENTER to pass) "
            )
          if healed.lower() == "y":
            del Mu.config["player"][teamId][playerId]["dead"]
          print()

if __name__ == "__main__":
  main()

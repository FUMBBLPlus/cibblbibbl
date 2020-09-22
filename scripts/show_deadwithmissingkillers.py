import cibblbibbl

PASS_REASONS = (
  # "ballAndChain",
  # "blocked",
  # "bomb",
  # "chainsaw",
  # "crowdPushed",
  "dodgeFail",
  # "eaten",
  "fireball",
  # "fouled",
  "gfiFail",
  "hitByRock",
  "landingFail",
  "leapFail",
  "lightning",
  # "secretWeaponBan",
  # "stabbed",
)

def main():
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
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
          name = d1["name"]
          li_dead = d1.get("dead")
          if not li_dead:
            continue
          half, turn, reason, killerId = li_dead
          if killerId is not None:
            continue
          if reason in PASS_REASONS:
            continue
          print(f'**{n}.** Dead Player: *{name}*  ({Te.name})')
          n += 1
          #print(f'Matchup: {Mu}')
          print(f'Match: https://fumbbl.com/p/match?id={Ma.Id}')
          #print(
          #  "Replay: https://fumbbl.com/ffblive.jnlp?replay="
          #  f'{Ma.replayId}'
          #)
          if reason != "secretWeaponBan":
            print(
                f'Half: {half}; Turn: {turn}; Reason: {reason}'
            )
          print()

if __name__ == "__main__":
  main()

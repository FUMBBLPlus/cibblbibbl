import cibblbibbl

REASONS = (
  "ballAndChain",
  "blocked",
  "bomb",
  "chainsaw",
  "crowdPushed",
  "dodgeFail",
  "eaten",
  "fireball",
  "fouled",
  "gfiFail",
  "hitByRock",
  "landingFail",
  "leapFail",
  "lightning",
  "secretWeaponBan",
  "stabbed",
)

PASSREASONS = (
  "dodgeFail",
  "fireball",
  "gfiFail",
  "hitByRock",
  "landingFail",
  "leapFail",
  "lightning",
)

KILLERREASONS = (
  "ballAndChain",
  "blocked",
  "bomb",
  "chainsaw",
  "crowdPushed",
  "eaten",
  "fouled",
  "stabbed",
)


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
          name = d1["name"]
          li_dead = d1.get("dead")
          if not li_dead:
            continue
          half, turn, reason, killerId = li_dead
          if killerId is not None:
            continue
          if reason in PASSREASONS:
            continue
          print(f'=== {n}. ===')
          n += 1
          print(f'Player: {name}')
          print(f'Team: {Te}')
          print(f'Matchup: {Mu}')
          print(f'Match: https://fumbbl.com/p/match?id={Ma.Id}')
          print(
            "Replay: https://fumbbl.com/ffblive.jnlp?replay="
            f'{Ma.replayId}'
          )
          if reason != "secretWeaponBan":
            print(f'Half: {half}; Turn: {turn}')
            print(f'Reason: {reason}')
            print()
          else:
            print()
            a = "x"
            while a not in ("", "1", "2"):
              a = input("Half (1/2; ENTER to pass): ")
            if a:
              li_dead[0] = int(a)
              a = "x"
              while a not in (
                  "1", "2", "3", "4", "5", "6", "7", "8",
              ):
                a = input("Turn (1..8): ")
              li_dead[1] = int(a)
              print("Possible reasons: ")
              for n, s in enumerate(REASONS, 1):
                print(f'[{n}] {s}')
              a = "x"
              accepted = {
                str(x) for x in range(1, len(REASONS)+1)
              }
              while a not in accepted:
                a = input("Reason number: ")
              reason = REASONS[int(a) - 1]
              li_dead[2] = reason
          reason = li_dead[2]
          if reason in KILLERREASONS:
            print("Killer candidates:")
            players = []
            accepted = {"0",}
            for teamId2, d02 in Mu.config["player"].items():
              Te2 = cibblbibbl.team.Team(teamId2)
              print(f'= {Te2} =')
              for playerId2 in sorted(d02,
                  key=lambda k: (d02[k]["name"], k)
              ):
                players.append(playerId2)
                accepted.add(str(len(players)))
                d12 = d02[playerId2]
                print(
                    f'{len(players):>2} '
                    f'[{playerId2}] {d12["name"]}'
                )
            print()
            killernr = "x"
            while killernr and killernr not in accepted:
              killernr = input(
                f'Killer Player Nr (0 if none; ENTER to pass): '
              )
            if killernr:
              if killernr == "0":
                li_dead[3] = None
              else:
                li_dead[3] = players[int(killernr) - 1]
          print()


if __name__ == "__main__":
  main()

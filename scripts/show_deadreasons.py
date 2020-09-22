import cibblbibbl


def main():
  set_reasons = set()
  for G in cibblbibbl.group.Group.__members__.values():
    G.register_tournaments()
    G.register_matchups()
    for Mu in G.matchups:
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
          set_reasons.add(reason)
  for s in sorted(set_reasons):
    print(s)


if __name__ == "__main__":
  main()

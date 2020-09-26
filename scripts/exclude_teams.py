import cibblbibbl


def main():
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    print()
    G.register_tournaments()
    G.register_matchups()
    Se = max(G.seasons).prev ### TODO
    for T in Se.tournaments.values():
      teams_with_match = set()
      teams_with_forfeits = set()
      teams_with_unplayed = set()
      for Mu in T.matchups:
        c = Mu.config
        Ma = Mu.match
        for Te in Mu.teams:
          d = c["team"][str(Te.Id)]
          r = d.get("r")
          if not r:
            teams_with_unplayed.add(Te)
          elif r == "F":
            teams_with_forfeits.add(Te)
          elif Ma:
            teams_with_match.add(Te)
      S = (
          teams_with_forfeits
          - teams_with_match
          - teams_with_unplayed
          - T.excluded_teams
          - T.group.excluded_teams
      )
      for Te in S:
        print(f'Tournament: {T}')
        print(
           "https://fumbbl.com/FUMBBL.php?page=group&op=view"
           "&p=tournaments&showallrounds=1&at=1"
           f'&group={T.group.config["groupIds"][0]}'
           f'&show={T.Id}'
        )
        print(f'Team: {Te}')
        print()
        a = "x"
        while a.lower() not in ("", "y", "n"):
          a = input("Exclude team? (Y/N; Enter to pass) ")
        if a.lower() == "y":
          T.exclude_teams(Te)
          #curr_excl = T.excluded_teamIds
          #for Mu in T.matchups:
          #  if Te in Mu.teams:
          #    Mu.excluded = "yes"
        print()


if __name__ == "__main__":
  main()

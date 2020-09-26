import copy
import re

import cibblbibbl


NUMNAMES = "one", "two", "three", "four",

EXTRA_STRIP = ' ⠀'
TEAMNAMEREP = '\s*\(.+$'

PASSPLAYERSTATUSES = (
  "Journeyman",
  "Retired Journeyman",
)

CASES = {
  "Daemons of Tzeentch": {
      "focus": "dead",
      "playerconfig": {
          "prevachievmul": 0.5,
          "prevreason": "splitted",
      },
      "source_position_name": "Pink Horror",
      "target_position_name": "Blue Horror",
      "target": 2,
  },
  "Numas": {
      "focus": "dead",
      "playerconfig": {
          "prevreason": "skeletonized",
      },
      "source_position_name": "Dervish",
      "target_position_name": "Skeleton Dervish",
      "target": 1,
  },
  "Malal": {
      "focus": "killed",
      "playerconfig": {
          "prevreason": "malalized",
      },
      "target": 1,
  },
}

def trim_roster_name(name):
  name = re.sub(TEAMNAMEREP, '', name)
  name = name.strip(EXTRA_STRIP)
  return name


def get_new_players_from_team_sheet(Te, position_name=None):
  players = Te.players
  for Pl in players:
    try:
      apiget = Pl.apiget
    except AttributeError:
      continue
    else:
      if apiget["status"] in PASSPLAYERSTATUSES:
        continue
    this_position_name = apiget["position"]["name"].strip()
    if position_name and this_position_name != position_name:
      continue
    games = apiget["statistics"]["games"]
    if games != 0:
      continue
    name = Pl.getname
    yield (Pl, name, Te, this_position_name)

def get_new_target_players(Te, Ma, Re, case):
  pn = case.get("target_position_name")
  prevMa = Te.prev_match(Ma)
  if prevMa:
    with prevMa.replay as prevRe:
      prev_players = prevRe.players[Te]
  else:
    prev_players = set()
  players = Re.players[Te] - prev_players
  for Pl in players:
    try:
      apiget = Pl.apiget
    except AttributeError:
      continue
    else:
      if apiget["status"] in PASSPLAYERSTATUSES:
        continue
    name = Pl.getname
    position = Pl.position
    #print("T", name, position)
    if position:
      this_position_name = position.name.strip()
    else:
      continue
    #print((this_position_name, pn))
    if pn and this_position_name != pn:
      continue
    #print(("T", Ma, Pl, name, Te, this_position_name))
    yield (Pl, name, Te, this_position_name)

def get_source_players(Te, Ma, Re, case):
  pn = case.get("source_position_name")
  players = Re.deadplayers # calculated despite being a property
  if case["focus"] == "dead":
    players = players[Te]
    playersTe = Te
  else:
    del players[Te]
    playersTe = tuple(players)[0]
    players = players[playersTe]
  for Pl in players:
    # print("S", Pl)
    position = Pl.position
    if position:
      this_position_name = position.name.strip()
    else:
      continue
    if pn and this_position_name != pn:
      continue
    name = Pl.getname
    # print(("S", Ma, Pl, name, playersTe, this_position_name))
    yield (Pl, name, playersTe, this_position_name)


def chain(targetPl, sourcePl, Ma, case):
  c = targetPl.config
  c["prevId"] = sourcePl.Id
  c["prevdeadmatchId"] = Ma.Id
  for k, v in case.get("playerconfig", {}).items():
    c[k] = v
  print(f'Chained {targetPl} to {sourcePl}')


def main():
  for G in cibblbibbl.group.Group.__members__.values():
    print(f'********** {G.key.upper()} **********')
    print()
    G.register_tournaments()
    G.register_matchups()
    Se = max(G.seasons).prev ### TODO
    #for Te in Se.teams(with_match=True):  ##TODO: filter teams
    for Te in G.teams:
      raw_roster_name = Te.roster.apiget["name"]
      roster_name = trim_roster_name(raw_roster_name)
      if roster_name not in CASES:
        continue
      print()
      print(f'Team: {Te}')
      print(f'Roster: {roster_name}')
      case = CASES[roster_name]
      spn = case.get("source_position_name")
      tpn = case.get("target_position_name")
      T = case.get("target", 1)
      s = (
        f'{case["focus"].title()} '
        f'{spn + " " if spn else ""}'
        "players are "
        f'{case["playerconfig"]["prevreason"]}'
      )
      if tpn:
        s += f' to {NUMNAMES[T-1]} {tpn} players each.'
      else:
        s += "."
      print(s)
      a = "x"
      while a not in ("", "y", "Y", "n", "N"):
        a = input(
            "Resolve chains for this team? "
            "(Y/N, ENTER to pass) "
        )
      if a not in ("y", "Y"):
        continue
      targets = sorted(get_new_players_from_team_sheet(Te, tpn))
      for n, (Pl, name, pTe, pn) in enumerate(targets, 1):
        print(f'TARGET {n}: [{Pl.Id}] {name} ({pn})')
        if Pl.prev:
          print(
            f'---> Already chained to '
            f'[{Pl.prev.Id}] {Pl.prev.getname} '
            f'({Pl.prev.position.name})'
          )
      matches = Te.matches  ## TODO filter matches
      for Ma in reversed(matches):
        print(f'Match: https://fumbbl.com/p/match?id={Ma.Id}')
        with Ma.replay as Re:
          new_sources = sorted(
              get_source_players(Te, Ma, Re, case)
          )
          new_targets = sorted(
              get_new_target_players(Te, Ma, Re, case)
          )
        for Pl, name, pTe, pn in new_sources:
          ptes = (f' of {pTe}' if pTe != Te else "")
          print(f'SOURCE: [{Pl.Id}] {name} ({pn}{ptes})')
          a = "x"
          chained = 0
          nrss = {str(x) for x in range(1, len(targets)+1)}
          while a and chained < case["target"]:
            a = input(
              "Chain TARGET Nr to this SOURCE "
              "(ENTER to pass): "
            )
            if a in nrss:
              chain(targets[int(a)-1][0], Pl, Ma, case)
              chained += 1
        for t in new_targets:
          Pl, name, pTe, pn = t
          targets.append(t)
          print(
              f'TARGET {len(targets)}: '
              f'[{Pl.Id}] {name} ({pn})'
          )
          if Pl.prev:
            print(
              f'---> Already chained to '
              f'[{Pl.prev.Id}] {Pl.prev.getname} '
              f'({Pl.prev.position.name})'
            )


if __name__ == "__main__":
  main()

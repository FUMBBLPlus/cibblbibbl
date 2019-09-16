import collections

import cibblbibbl


IndividualResult = collections.namedtuple(
    "IndividualResult",
    ("team", "match", "rsym", "tdd", "casd")
)


def individual(T, *, follow_prev=True, from_next=False):
  """
  Generate individual results of teams.

  Thus, every matchup yield two namedtuples as values.
  Every tuple has the following fields:
    - team : the Team instance of the team involved
    - match : the Match instance or None if fortfeited
    - rsym : the one character result symbol which can be:
                W : win
                D : draw
                L : loss
                C : conceded (loss)
                B : bye
                F : forfeit
    - tdd : touchdown difference
    - casd : casualties difference
  """
  excluded_teams = T.excluded_teams(with_fillers=True)
  if not from_next and T.next:
    return
  if follow_prev and T.prev:
      yield from individual(T.prev, from_next=True)
  for S in T.schedule:
    team = {d["id"]: d["name"] for d in S["teams"]}
    if set(team) & excluded_teams:
        # ignore matchups with excluded and filler teams
      continue
    R = S["result"]
    if R.get("id"):
        # having a positive ID value in a result means that
        # there was a match played
      M = cibblbibbl.match.Match(R["id"])
      conceded = M.conceded()
      casualties = M.casualties()
      for i in range(2):
        ID = int(R["teams"][i]["id"])
        Te = cibblbibbl.team.Team(ID)
        oppo_ID = int(R["teams"][1-i]["id"])
        oppo_Te = cibblbibbl.team.Team(oppo_ID)
        score = R["teams"][i]["score"]
        oppo_score = R["teams"][1-i]["score"]
        tdd = score - oppo_score
        cas = casualties[Te]
        oppo_cas = casualties[oppo_Te]
        casd = cas - oppo_cas
        if 0 < tdd:
          rsym = "W"
        elif tdd == 0:
          rsym = "D"
        elif conceded is Te:
            # check for concessions on loosers first
          rsym = "C"
        else:
          rsym = "L"
        tdd += T.rsym_tdd.get(rsym, 0)
        casd += T.rsym_casd.get(rsym, 0)
        yield IndividualResult(Te, M, rsym, tdd, casd)
    else:
        # a zero ID value in a result means that the game was
        # forfeited
      winner_ID = int(R["winner"])
      for ID, name in team.items():
        Te = cibblbibbl.team.Team(ID)
        if ID == winner_ID:
          rsym = "B"
        else:
          rsym = "F"
        tdd = T.rsym_tdd.get(rsym, 0)
        casd = T.rsym_casd.get(rsym, 0)
        yield IndividualResult(Te, None, rsym, tdd, casd)


def hth_all(T):
  """
  Generate all result objects which are compatible with the
  pytourney.tie.hth.calculate() function.

  However, these objects should be gruped by same scores earned
  and then passing those rows of groups separately to the
  function. Thus, the purpose of this function is to provide
  data which should be cached by the caller like this:

  hth_all_ = list(hth_all(T))

  Then, once a group of equally scored teams is known, the
  cached value along with the team IDs of the teams in the group
  should be used to call the group function which return the
  object nicely prepared for the HTH calculator function:

  o = list(hth_group(hth_all_, team_ID_1, team_ID_2, ...))
  hth = pytourney.tie.hth.calculate(o)
  """
  excluded_teams = T.excluded_teams(with_fillers=True)
  for S in T.schedule:
    r_teams = S["result"]["teams"]
    if set(int(d["id"]) for d in r_teams) & excluded_teams:
      continue
    if S["result"].get("id"):  # there was a match
      ID1 = int(r_teams[0]["id"])
      ID2 = int(r_teams[1]["id"])
      score1 = r_teams[0]["score"]
      score2 = r_teams[1]["score"]
      yield {ID1: score1, ID2: score2}


def hth_group(hth_all_, *team_IDs):
  """
  Filter the results of a group of teams from the passed object
  generated by hth_all().

  For more info, see the docstring of hth_all().
  """
  for ID in team_IDs:
      # generate objects which will ensure that all nodes will
      # be made; as there could be a member which played none of
      # the other equally scored members, this is necessary
    yield {str(ID): 0}
        # pytourney.tie.hth.calculate requires string keys
  for r0 in hth_all_:
      # then, generate edges by passing results of the group
      # members within the group
    r1 = {
        str(ID): score
        for ID, score in r0.items()
        if ID in team_IDs
    }
    if 1 < len(r1):
        # I do not want to pas empty dictionaries nor nodes as
        # those were ensured before
      yield r1

import texttable

import cibblbibbl


def export(T, *,
    show_team_id = False,
):
  multiline = False
  params = [
      (" #", "a", "r", 2,),
      ("Team ID", "i", "r", 7,),
      ("Name", "t", "l", 30,),
      ("Roster", "t", "l", 19,),
      ("Coach", "t", "l", 19,),
      ("Perf.", "t", "l", 7,),
      ("GAM", "i" , "r", 3,),
      (" CV", "t", "r", 2,),
      ("POS", "t", "r", 3,),
      (" P", "i", "r", 3,),
  ]
  if not show_team_id:
    del params[1]
  table = texttable.Texttable()
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  standings = T.standings()
  for nr, r in enumerate(standings, 1):
    Te = r["team"]
    if isinstance(Te, cibblbibbl.team.GroupOfTeams):
      multiline = True
      key = (T, Te[0])  # all members has same values
      perf = "\n".join(
          "".join(rsym for rsym, matchId in seq)
          for seq in r["perfs"]
      )
    else:
      key = (T, Te)
      perf = "".join(rsym for rsym, matchId in r["perf"])
    pgamcls = cibblbibbl.achievement.tp_match.cls
    pgama = pgamcls.getmember(*key)
    pgam = (pgama["prestige"] if pgama else 0)
    pposcls = cibblbibbl.achievement.tp_standings.cls
    pposa = pposcls.getmember(*key)
    ppos = (pposa["prestige"] if pposa else 0)
    pcvcls = cibblbibbl.achievement.ta_crushingvictory.cls
    pcva = pcvcls.getmember(*key)
    pcv = (pcva["prestige"] if pcva else 0)
    ptot = pgam + pcv + ppos
    row = [
        f'{nr}',
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        perf,
        (str(pgam) if pgam else ""),
        (str(pcv) if pcv else ""),
        (str(ppos) if ppos else ""),
        (str(ptot) if ptot else ""),
    ]
    if not show_team_id:
      del row[1]
    rows.append(row)
  rows.insert(0, [t[0] for t in params])
  table.add_rows(rows)
  table.set_deco(
      texttable.Texttable.HEADER
      #| texttable.Texttable.VLINES
      | (texttable.Texttable.HLINES if multiline else 0)
  )
  return table.draw()

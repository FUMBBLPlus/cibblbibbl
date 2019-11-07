import texttable

import cibblbibbl


def export(T, *,
    show_Ids = False,
):
  cto_trans = {-1: "", -112: "???", -999: ""}
      # -112: missing; -999: no performance
  hth_trans = {-1: "", 0: "--"}
  nr_trans = {None: "--"}
  multiline = False
  params = [
      (" #", "a", "r", 2,),
      ("Team ID", "i", "r", 7,),
      ("Name", "t", "l", 30,),
      ("Roster", "t", "l", 19,),
      ("Coach", "t", "l", 19,),
      ("Perf.", "t", "l", 7,),
      ("PTS", "i" , "r", 3,),
      ("HTH", "t", "r", 3,),
      ("TDD", "i", "r", 3,),
      ("CAD", "i", "r", 3,),
      ("CTO", "i", "r", 3,),
  ]
  if not show_Ids:
    del params[1]
  table = texttable.Texttable()
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  standings = T.standings()
  prev_nr = ...
  for r in standings:
    nr = r["nr"]
    if nr is None:
      nrstr = "--"
    elif nr == prev_nr:
      nrstr = ""
    else:
      nrstr = str(nr)
    Te = r["team"]
    if isinstance(Te, cibblbibbl.team.GroupOfTeams):
      multiline = True
      perf = "\n".join(
          "".join(r for r, matchId in seq)
          for seq in r["perfs"]
      )
    else:
      perf = "".join(r for r, matchId in r["perf"])
    pts = r["pts"]
    if 1000000 <= pts:
      pts = f'W{pts-1000000}'
    row = [
        nrstr,
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        perf,
        (pts if perf else ""),
        hth_trans.get(r["hth"], r["hth"]),
        (r["tddiff"] if perf else ""),
        (r["casdiff"] if perf else ""),
        cto_trans.get(r["cto"], r["cto"]),
    ]
    if not show_Ids:
      del row[1]
    rows.append(row)
    prev_nr = nr
  rows.insert(0, [t[0] for t in params])
  table.add_rows(rows)
  table.set_deco(
      texttable.Texttable.HEADER
      #| texttable.Texttable.VLINES
      | (texttable.Texttable.HLINES if multiline else 0)
  )
  return table.draw()

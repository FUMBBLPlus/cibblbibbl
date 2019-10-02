import texttable


def default(prestiges_obj, *,
    show_team_id = False,
):
  P = prestiges_obj
  params = [
      (" #", "a", "r", 2,),
      ("Team Id", "i", "r", 7,),
      ("Name", "t", "l", 30,),
      ("Roster", "t", "l", 19,),
      ("Coach", "t", "l", 19,),
      ("Perf.", "t", "l", 7,),
      ("GAM", "i" , "r", 3,),
      ("POS", "t", "r", 3,),
      ("P", "i", "r", 3,),
  ]
  if not show_team_id:
    del params[1]
  table = texttable.Texttable()
  multiline = any(("\n" in r["team"].name) for r in P)
  table.set_deco(
      texttable.Texttable.HEADER
      | texttable.Texttable.VLINES
      | (texttable.Texttable.HLINES if multiline else 0)
  )
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  for nr, r in enumerate(P, 1):
    Te = r["team"]
    row = [
        f'{nr}',
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        r["perf"],
        r["gam"],
        (r["pos"] if r["pos"] else ""),
        r["p"],
    ]
    if not show_team_id:
      del row[1]
    rows.append(row)
  table.add_rows([[t[0] for t in params]] + rows)
  return table.draw()

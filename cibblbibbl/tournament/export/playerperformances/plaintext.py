import texttable

import cibblbibbl

from ... import performance


columntrans = {
    "Casualties": "Cs",
    "Completions": "Cp",
    "Fouls": "Fo",
    "Interceptions": "It",
    "SPP": "SPP",
    "Touchdowns": "Td",
    "Blocking Scorer": "BS",
    "Blocking Thrower": "BT",
    "Scoring Thrower": "ST",
    "Triple": "Tr",
    "Allrounder": "Ar",
}

default_order = (
    "SPP",
    "Touchdowns",
    "Casualties",
    "Interceptions",
    "Completions",
    "Fouls",
    "Blocking Scorer",
    "Blocking Thrower",
    "Scoring Thrower",
    "Triple",
    "Allrounder",
)


def export(T, order = None):
  params = [
      ("Name", "t", "l", 30,),
      ("Team", "t", "l", 30,),
      #("Roster", "t", "l", 19,),
      #("Position", "t", "l", 19,),  # TODO
      #("Coach", "t", "l", 19,),
  ]
  order = order or default_order
  params += [
      (columntrans[name], "t", "r", len(columntrans[name]),)
      for name in order
  ]
  table = texttable.Texttable()
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])

  rows = []
  performances0 = T.extraplayerperformances(join=True)
  if not performances0:
    raise cibblbibbl.tournament.export.NoExport(f'{T.Id}')
  performances = performance.trans(performances0)
  ordered = sorted(performances,
      key=lambda Sj: tuple(
          performances[Sj][name]
          for name in list(order) + ["name",]
      ),
      reverse=True,
  )
  for Sj in ordered:
    name = Sj.name
    if 30 < len(name):
      parts = name.split(" ")
      while 1 < len(parts) and 30 < len(" ".join(parts)):
        parts = parts[:-1]
      name = " ".join(parts)
      if 30 < len(name):
        name = f'{name[:28]}..'
    Te = Sj.team
    if Te is ...:
      teamname, roster_name, coach_name = "", "", ""
    elif Te and not isinstance(Te, str):
      teamname = Te.name
      roster_name = Te.roster_name
      coach_name = Te.coach_name
    else:
      teamname, roster_name, coach_name = Te, "", ""
    d = performances[Sj]
    names = [
        name,
        teamname,
        #roster_name,
        #coach_name,
    ]
    vals = [
      (str(d[k]) if d[k] else "")
      for k in order
    ]
    if not any(vals):
      break
    rows.append(names + vals)
  rows.insert(0, [t[0] for t in params])
  table.add_rows(rows)
  table.set_deco(
      texttable.Texttable.HEADER
  )
  return table.draw()

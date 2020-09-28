import itertools

N = "\n"


EMSPACE = " "
ENSPACE = " "
FOURPEREMSPACE = " "
HAIRSPACE = " "
NOBREAKSPACE = " "
SIXPEREMSPACE = " "
THINSPACE = " "
THREEPEREMSPACE = " "
ZEROWIDTHNOBREAKSPACE = "﻿"
ZEROWIDTHSPACE = "​"


NAMENORMS = {
    " ": " ",
    "ă": "a",
    "ā": "a",
    "ō": "o",
    " ": " ",
}


def b(text):
  return f'__{str(text)}__'

def br():
  return "%%%"

def center(content):
  return f'{{center\n{content}\n}}'

def dualcolumn(content1, content2):
  return (
      f'<<<\n\n{str(content1)}\n\n'
      f'|||\n\n{str(content2)}\n\n>>>'
  )

def i(text):
  return f"''{str(text)}''"

def hr():
  return "----"

def img(href):
  return f'[img]{href}[/img]'

def left(text):
  return f'{str(text)}'

def list_(items):
  if not items:
    return ""
  return "* " + "\n* ".join(str(x) for x in items)

def url(url, name=None):
  if name is None:
    return f'[{url}]'
  return f'[{name} | {url}]'

def coach(coach_name):
  return url(f'/~{coach_name}', coach_name)

def match(Ma, name):
  return url(f'https://fumbbl.com/p/match?id={Ma.Id}', name)

def namenorm(s):
    return "".join(NAMENORMS.get(c, c) for c in s).strip()

def notepage(P, name, owner="SzieberthAdam"):
  return url(f'https://fumbbl.com/note/{owner}/{P.notelink()}', name)

def player(Pl):
  playerId = Pl.Id
  if playerId.isdecimal():
    return url(f'https://fumbbl.com/p/player?player_id={Pl.Id}', namenorm(Pl.name))
  else:
    return namenorm(Pl.name)

def table(
    rows,
    *,
    align=None,
    header=None,
    header_align=None,
):
  if align is None:
    columns = max(len(row) for row in rows)
    align = 'L' * columns
  if header is not None and header_align is None:
    header_align = "C" * len(header)
  waligntr = {"L": "<", "R": ">", "C": "^"}
  align = ''.join(s.upper() for s in align)
  walign = "".join(waligntr[c] for c in align)
  if header or header_align:
    if header_align is not None:
        header_align = ''.join(s.upper() for s in header_align)
    else:
        headed_align = align
    wheader_align = "".join(waligntr[c] for c in header_align)
  else:
    wheader_align = None
  waligns = itertools.cycle([walign])
  if header is not None:
    rows = itertools.chain([header], rows)
    waligns = itertools.chain([wheader_align], waligns)
  parts = []
  for r, row in enumerate(rows):
    rowparts = []
    _a = next(waligns)
    for i, record in enumerate(row):
      s = (f' {record}' if record is not None else "")
      rowparts.append(f'|{_a[i]}{s}')
    parts.append(" ".join(rowparts))
  return "\n".join(parts)

def team(Te):
  if isinstance(Te, str):
    return namenorm(Te)
  else:
    return url(f'https://fumbbl.com/p/team?team_id={Te.Id}', namenorm(Te.name))

def tournament(T, name="<long>"):
  if name in ("<long>", "<short>"):
    name = getattr(T, f'{namelength[1:-1]}name')
  groupId = 10455  # TODO: hardcoded
  url_ = (
      "https://fumbbl.com/FUMBBL.php?page=group&op=view&showallrounds=1&at=1"
      f'&group={groupId}'
      f'&p=tournaments&show={T.Id}'
  )
  return url(url_, name)

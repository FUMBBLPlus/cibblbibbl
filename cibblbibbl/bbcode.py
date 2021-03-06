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


def b(text):
  return f'[b]{str(text)}[/b]'

def center(text):
  return f'[block=center]{str(text)}[/block]'

def font(text, family):
  return f'[font={family}]{str(text)}[/font]'

def i(text):
  return f'[i]{str(text)}[/i]'

def hr():
  return "[block=automargin blackborder width=100%][/block]"

def img(href):
  return f'[img]{href}[/img]'

def left(text):
  return f'{str(text)}'

def list_(items, itemnr=None):
  if not items:
    return ""
  if itemnr:
    assert itemnr in "aAiI1"
    otag = f'[list={itemnr}]'
    ctag = "[/list]"
  else:
    otag = "[ulist]"
    ctag = "[/ulist]"
  itemstr = (f'[li]').join([""] + list(items))
  return f'{otag}{itemstr}{N}{ctag}'

def monospace(text):
  return font(text, "monospace")

def right(text):
  return f'[block=right]{str(text)}[/block]'

def size(content, size=10):
  return f'[size={size}]{content}[/size]'

def sub(text):
  return (
      "[size=7][block display=inline position=relative]"
      "[block display=inline position=absolute top=1.5ex]"
      f'{str(text)}'
      "[/block][/block][/size]"
  )

def table(
    rows,
    *,
    align=None,
    header=None,
    header_align=None,
    header_style="bg=black fg=white",
    style="blackborder border2",
    tr_styles=("bg=#e6ddc7", "bg=#d6cdb7"),
    width="100%",
    widths=None,
    indent="\t",
):
  if align is None:
    columns = max(len(row) for row in rows)
    align = 'L' * columns
  if header is not None and header_align is None:
    header_align = "C" * len(header)
  align = ''.join(s.upper() for s in align)
  if header_align:
    header_align = ''.join(s.upper() for s in header_align)
  def subgen():
    nonlocal rows
    d_table = style2dict(style)
    if width:
      d_table["width"] = width
    tablestyle = dict2style(d_table)
    yield otag("table", tablestyle)
    td_aligns = itertools.cycle([align])
    tr_styles_ = itertools.cycle(tr_styles)
    if header is not None:
      rows = itertools.chain([header], rows)
      td_aligns = itertools.chain([header_align], td_aligns)
      tr_styles_ = itertools.chain([header_style], tr_styles_)
    for r, row in enumerate(rows):
      d_tr = style2dict(next(tr_styles_))
      if hasattr(row, "style"):
        d_tr.update(style2dict(row.style))
      trstyle = dict2style(d_tr)
      yield indent + otag("tr", trstyle)
      align_ = next(td_aligns)
      for c, record in enumerate(row):
        f = {"C": center, "L": left, "R": right}[align_[c]]
        d_td = {}
        if r == 0 and widths is not None:
          if widths[c] is not None:
            d_td["width"] = widths[c]
        if hasattr(record, "style"):
          d_td.update(style2dict(record.style))
        tdstyle = dict2style(d_td)
        yield (
            2 * indent
            + f'{otag("td", tdstyle)}{f(record)}[/td]'
        )
      yield indent + f'[/tr]'
    yield f'[/table]'
  return "".join(subgen())

def url(url, name=None):
  if name is None:
    return f'[url]{url}[/url]'
  return f'[url={url}]{name}[/url]'

def otag(name, style=None):
  if style:
    return f'[{name} {style}]'
  else:
    return f'[{name}]'

def ctag(name):
  return f'[/{name}]'

def dict2style(d):
  parts = []
  for k in sorted(d, key=lambda k: (bool(d[k]), k)):
    v = str(d[k])
    if v:
      parts.append(f'{k}={v}')
    else:
      parts.append(k)
  s = " ".join(parts)
  return s

def style2dict(style):
  d = {}
  for s in style.split(" "):
    s = s.strip().lower()
    k, _, v = [s2.strip() for s2 in s.partition("=")]
    d[k] = v
  return d



def coach(coach_name):
  return url(f'/~{coach_name}', coach_name)

def match(Ma, name):
  return url(f'/p/match?id={Ma.Id}', name)

def notepage(P, name, owner="SzieberthAdam"):
  return url(f'/note/{owner}/{P.notelink()}', name)

def player(Pl):
  playerId = Pl.Id
  if playerId.isdecimal():
    return url(f'/p/player?player_id={Pl.Id}', Pl.name)
  else:
    return Pl.name

def team(Te):
  if isinstance(Te, str):
    return Te
  else:
    return url(f'/p/team?team_id={Te.Id}', Te.name)

def tournament(T, namelength="long"):
  name = getattr(T, f'{namelength}name')
  groupId = 10455  # TODO: hardcoded
  url_ = (
      "/FUMBBL.php?page=group&op=view&showallrounds=1&at=1"
      f'&group={groupId}'
      f'&p=tournaments&show={T.Id}'
  )
  return url(url_, name)


def move(moveval):
  if moveval and isinstance(moveval, str):
    return size(moveval, 8)
  elif not moveval:
    return ""
  elif 0 < moveval:
    return f'↑{size(moveval, 8)}'
  elif moveval < 0:
    return f'↓{size(abs(moveval), 8)}'


def tooltip(tooltipId, content):
  return f'[block=tooltip id={tooltipId}]{content}[/block]'

def tooltiped(tooltipId, content):
  return f'[block tooltip={tooltipId}]{content}[/block]'

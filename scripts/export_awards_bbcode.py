
import cibblbibbl
from cibblbibbl import bbcode

from export_awards import parse_ids


def tournament_name(T):
  s = bbcode.tournament(T)
  if T.status != "Completed":
    s += f' /{T.status.upper()}/'
  return s


if __name__ == "__main__":
  import sys
  G = cibblbibbl.CIBBL
  G.init()
  Tids = parse_ids(G, sys.argv)
  for Tid in Tids:
    T = G.tournaments[Tid]
    if not T.ismain:
      continue
    if T.posonly == "yes":
      continue
    try:
      s0 = T.export_awards_bbcode()
    except:
      print(f'[{T.Id}] {T.name}')
      raise
    tournament_title = tournament_name(T)
    s1 = ""
    logo = T.config.get("image744")
    if logo:
      s1 = bbcode.img(logo) + "\n\n"
    s2 = f'{tournament_title}\nAward Ceremony'
    s2 = bbcode.size(bbcode.b(bbcode.i(s2)), 14)
    text = f'[block=center]\n{s1}{s2}\n[/block]\n\n\n{s0}'
    f_filename = cibblbibbl.field.filepath.idfilename.fget
    filename = f_filename(T, ".bbcode")
    p = cibblbibbl.data.path
    p /= f'{G.key}/tournament/awards/bbcode/{filename}'
    with p.open("w", encoding="utf8") as f:
      f.write(text)
    print(text)
    print("\n" * 3)


import cibblbibbl

from export_standings import tournament_name


def parse_ids(group, argv):
  D = group.tournaments
  if len(argv) == 1:
    return sorted(D, key=D.__getitem__)
  else:
    s = set()
    for a in argv[1:]:
      if a.upper() == "<STR>":
        s |= {i for i in D if not i.isdecimal()}
        continue
      sa = a.split("-")
      assert len(sa) in {1, 2}
      if len(sa) == 1:
        s.add(a)
      else:
        assert all(i.isdecimal() for i in sa)
        r = range(int(sa[0]), int(sa[1])+1)
        s |= set(str(i) for i in r)
    s &= set(D)
    return sorted(s, key=D.__getitem__)


if __name__ == "__main__":
  import sys
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  Tids = parse_ids(G, sys.argv)
  for Tid in Tids:
    T = G.tournaments[Tid]
    if not T.ismain:
      continue
    if T.posonly == "yes":
      continue
    if T.status != "Completed":
      continue
    try:
      s0 = T.export_awards_plaintext(show_Ids=show_Ids)
    except:
      print(f'[{T.Id}] {T.name}')
      raise
    tournament_title = tournament_name(T, show_Ids)
    s1 = f'Awards of {tournament_title}'
    text = f'{s1}\n\n{s0}'
    f_filename = cibblbibbl.field.filepath.idfilename.fget
    filename = f_filename(T, ".txt")
    p = cibblbibbl.data.path
    p /= f'{G.key}/tournament/awards/{filename}'
    with p.open("w", encoding="utf8") as f:
      f.write(text)
    print(text)
    print("\n" * 3)

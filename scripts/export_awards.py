
import cibblbibbl

if __name__ == "__main__":
  import sys
  if len(sys.argv) == 1:
    targ = None
  else:
    targ = sys.argv[1]
    starg = targ.split("-")
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  if targ is None:
    Ts1 = Ts = sorted(G.tournaments.values())
  elif targ.upper() == "STR":
    Ts = sorted(G.tournaments.values())
    Ts1 = [T for T in Ts if not T.Id.isdecimal()]
  elif len(starg) == 2:
    r = range(int(starg[0]), int(starg[1])+1)
    Ts = sorted(G.tournaments.values())
    Ts1 = [
        T for T in Ts
        if T.Id.isdecimal() and (int(T.Id) in r)
    ]
  else:
    Ts1 = [G.tournaments[targ],]
  for T in Ts1:
    if not T.ismain:
      continue
    if T.posonly == "yes":
      continue
    try:
      s0 = T.export_awards_plaintext(show_Ids=show_Ids)
    except:
      print(f'[{T.Id}] {T.name}')
      raise
        # TODO: handler matching standings func
    s1 = ""
    if not T.abstract:
      ids, styles_ = [T.Id,], [T.style,]
      t = T
      while t.prev:
        ids.insert(0, t.prev.Id)
        styles_.insert(0, t.prev.style)
        t = t.prev
      styles, s_styles = [], set()
      for s in styles_:
        if s not in s_styles:
          styles.append(s)
          s_styles.add(s)
      idstr = ", ".join(str(x) for x in ids)
      stylestr = ", ".join(styles)
      s1 = f' ({idstr} • {stylestr})'
    text = f'Awards of {T.name}{s1}\n\n{s0}'
    f_filename = cibblbibbl.field.filepath.idfilename.fget
    filename = f_filename(T, ".txt")
    p = cibblbibbl.data.path
    p /= f'{G.key}/tournament/awards/{filename}'
    with p.open("w") as f:
      f.write(text)
    print(text)
    print("\n" * 3)

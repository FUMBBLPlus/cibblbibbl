
import cibblbibbl

if __name__ == "__main__":
  G = cibblbibbl.CIBBL
  G.init()
  show_id = True
  Ts = sorted(G.tournaments.values())
  m_exp = cibblbibbl.tournament.export.standings.plaintext
  f_exp = m_exp.export
  texts = []
  for T in Ts:
    if not T.ismain:
      continue
    s0 = f_exp(T, show_id=show_id)
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
    s2 = f'Standings of {T.name}{s1}\n\n{s0}'
    texts.append(s2)
  p = cibblbibbl.data.path
  p /= f'{G.key}/tournament/standings.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w") as f:
      f.write(text)
  print(text)


import cibblbibbl

from export_standings import tournament_name

if __name__ == "__main__":
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  Ts = sorted(G.tournaments.values())
  m_exp0 = cibblbibbl.tournament.export
  m_exp = m_exp0.playerperformances.plaintext
  f_exp = m_exp.export
  texts = []
  for T in Ts:
    if not T.ismain:
      continue
    try:
      s0 = f_exp(T)
    except cibblbibbl.tournament.export.NoExport:
      continue
    tournament_title = tournament_name(T, show_Ids)
    s1 = f'Player Performances of {tournament_title}'
    texts.append(f'{s1}\n\n{s0}')
  p = cibblbibbl.data.path
  p /= f'{G.key}/tournament/playerperformances.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w", encoding="utf8") as f:
      f.write(text)
  print(text)

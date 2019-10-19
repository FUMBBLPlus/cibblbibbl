import copy
import math

import cibblbibbl

from .. import field


def iterexisting(cls, group_key):
  G = cibblbibbl.group.Group(group_key)
  directory = (
    cibblbibbl.data.path
    / group_key
    / "achievement"
    / f'{cls.__name__.lower()}'
  )
  for p in directory.glob("**/*.json"):
    tournamentId = p.parent.name
    if tournamentId.isdecimal():
      tournamentId = tournamentId.lstrip("0")
    tournament = G.tournaments[tournamentId]
    subjectId = cls.subjectIdcast(p.stem)
    subject = cls.subject_factory(subjectId)
    A = cls(tournament, subject)
    yield A

def iterprevs(cls, group_key):
  G = cibblbibbl.group.Group(group_key)
  players = sorted(Pl for Pl in G.players if Pl.prev)
  for Pl in players:
    prevPl = Pl.prev
    prevachievmul = Pl.prevachievmul
    for A0 in prevPl.achievements:
      if A0.group_key != group_key:
        continue
      if A0.clskey() != cls.clskey():
        continue
      tournament = A0.tournament
      subject = Pl
      A = cls(tournament, subject)
      if not A.config:
        A.config = copy.deepcopy(A0.config._data)
        v = A0.baseprestige * prevachievmul
        A.baseprestige = math.floor(v)
      yield A

import pyfumbbl

class Player:

  def __init__(self, playerId: int):
    self._Id = int(playerId)
    self.achievements = set()

  def __eq__(self, other):
    return (hash(self) == hash(other))

  def __hash__(self):
    return hash(("PLAYER", self._Id, "PLAYER"))
        # minimize the chance of unintended match

  def __repr__(self):
    return f'{self.__class__.__name__}({self._Id})'

  @property
  def Id(self):
    return self._Id

  @property
  def status(self):
    return self.apiget()["status"]

  def apiget(self):
    return pyfumbbl.player.get(self.Id)

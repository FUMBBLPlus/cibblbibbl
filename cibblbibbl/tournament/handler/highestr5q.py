import copy

from . import default

from ... import field


class HighestR5QualifierTournament(default.Tournament):

  posonly = field.config.yesnofield(
      "!posonly", default="yes"
  )


def init(group_key, Id):
  return HighestR5QualifierTournament(group_key, Id)

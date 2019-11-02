import cibblbibbl


@property
def group_by_self_group_key(self):
  return cibblbibbl.group.Group(self.group_key,
    register_tournaments=False,  # avoid infinite loop
  )


@property
def position_by_self_positionId(self):
  return cibblbibbl.position.Position(self.positionId)


@property
def tournament(self):
  return self.group.tournaments[self.tournamentId]


@property
def year_by_self_group_key_and_year_nr(self):
    return cibblbibbl.year.Year(
        self.group_key, self.year_nr
  )

@property
def year_of_self_tournament(self):
  return self.tournament.year


@property
def year_nr_of_self_tournament(self):
  return self.tournament.year_nr


def id_and_name_str(self):
  return f'[{self.Id}] {self.name}'

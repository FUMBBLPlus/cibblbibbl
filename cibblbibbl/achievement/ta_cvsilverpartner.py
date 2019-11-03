import collections
import cibblbibbl

from .. import field
from . import exporttools
from .mastercls import TeamAchievement
from .ta_cvgoldpartner import TA_CVGoldPartner


class TA_CVSilverPartner(TeamAchievement):

  rank = 25
  sortrank = 40

  f_partners = lambda S: S.silver_partner_teams()

  agent01 = classmethod(TA_CVGoldPartner.agent01.__func__)



cls = TA_CVSilverPartner

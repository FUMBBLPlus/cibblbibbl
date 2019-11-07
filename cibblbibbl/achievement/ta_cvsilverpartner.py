import collections
import cibblbibbl

from . import agent
from .. import field
from . import exporttools
from .mastercls import TeamAchievement
from .ta_cvgoldpartner import TA_CVGoldPartner


class TA_CVSilverPartner(TeamAchievement):

  rank = 25
  sortrank = 40

  f_partners = lambda S: S.silver_partner_teams()

  agent01 = classmethod(TA_CVGoldPartner.agent01.__func__)
  agent50 = classmethod(agent.iterpostponed)

  nexttournament = TA_CVGoldPartner.nexttournament

cls = TA_CVSilverPartner

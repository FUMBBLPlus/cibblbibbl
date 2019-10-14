import collections
import os
import pkgutil

import cibblbibbl

__all__ = list(
    module for _, module, _
    in pkgutil.iter_modules([os.path.dirname(__file__)])
)

from . import *


Achievement = mastercls.Achievement


def collect(group_key):
  return {
      a
      for cls in sorted(
          Achievement.registry.values(),
          key = lambda c: c.rank
      )
      for a in cls.collect(group_key)
  }


def collectall():
  return {
      a
      for key in cibblbibbl.group.Group.__members__
      for a in collect(key[0])
  }


del pkgutil
del os

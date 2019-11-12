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


def collect(group, rank=None):
  return {
      a
      for cls in sorted(
          Achievement.registry.values(),
          key = lambda c: c.rank
      )
      for a in cls.collect(group)
      if (True if rank is None else (a.rank == rank))
  }


def collectall(rank=None):
  return {
      a
      for group in cibblbibbl.group.Group.__members__.values()
      for a in collect(group, rank=rank)
  }


del pkgutil
del os

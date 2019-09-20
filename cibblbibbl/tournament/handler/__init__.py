import os
import pkgutil

import cibblbibbl

__all__ = list(
    module for _, module, _
    in pkgutil.iter_modules([os.path.dirname(__file__)])
)

from . import *

def get_handler(group_key, ID):
  if str(ID).isdecimal():
    filename = f'{ID:0>8}'
  else:
    filename = str(ID)
  handlerfile = f'{group_key}/tournament/handler/{filename}'
  p = cibblbibbl.data.path / handlerfile
  p_exists = (p.is_file() and p.stat().st_size)
  if p_exists:
    handlername = cibblbibbl.data.jsonfile(p).data
  else:
    handlername = "default"
  handler = globals()[handlername]
  return handler

del pkgutil
del os

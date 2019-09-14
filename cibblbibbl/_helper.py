import json
import pathlib
import re

import cibblbibbl

EXTRA_STRIP = " ⠀"
IGNORE = "\xad"


def norm_name(s):
  s = s.strip(EXTRA_STRIP)
  s = re.sub(f'[{IGNORE}]', "", s)
  return s


def get_api_data(ID, dir_path, api_func, *, reload=False):
  filename = f'{ID:0>8}.json'
  p = cibblbibbl.data.path / dir_path / filename
  jf = cibblbibbl.data.jsonfile(p)
  if reload or not p.is_file() or not p.stat().st_size:
    jf.dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf.data = api_func(ID)
    jf.save()
  return jf.data

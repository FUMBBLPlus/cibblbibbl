import json
import pathlib

try:
  import fumbbl_session
except ImportError:
  fumbbl_session = None


if fumbbl_session:
  rootpath = pathlib.Path(__file__).parent
  with open(rootpath / 'login.json') as f:
      _login = json.load(f)
  fumbbl_session.log_in(**_login)

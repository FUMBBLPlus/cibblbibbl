import json
import pathlib


class BaseSettings:

  def __init__(self):
    self._settings = {p: dict() for p in self.files}
    self.refresh()

  def __getitem__(self, key):
    exc = None
    if hasattr(self, "prefix") and self.prefix:
      key = f'{self.prefix}.{key}'
    for p in self.files:
      try:
        return self._settings[p][key]
      except KeyError as exc_:
        exc = exc_

  def __setitem__(self, key, value):
    p = self.files[0]
    if hasattr(self, "prefix") and self.prefix:
      key = f'{self.prefix}.{key}'
    self._settings[p][key] = value
    p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
    with p.open("w", encoding="utf8") as f:
      json.dump(
          self._settings[p],
          f,
          indent="\t",
          ensure_ascii=False,
          sort_keys=True,
      )

  def refresh(self):
    for p in self.files:
      if p.is_file():
        with p.open(encoding="utf8") as f:
          self._settings[p] = json.load(f)


class Settings(BaseSettings):

  files = (
      (
          pathlib.Path.home()
          / ".fumbblplus/cibblbibblsettings.json"
      ),
      (
          pathlib.Path(__file__).parent
          / "cibblbibblsettings.default.json"
      ),
  )
settings = Settings()  # singleton

class LoginSettings(BaseSettings):

  files = (
      pathlib.Path.home() / ".fumbblplus/login.json",
  )
loginsettings = LoginSettings()  # singleton


class DataSettings(BaseSettings):

  @property
  def files(self):
    data_path = settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= "settings.json"
    return (p,)

data_settings = DataSettings()  # singleton


class DataBIBBLSettings(BaseSettings):

  @property
  def files(self):
    data_path = settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= "bibbl"
    p /= "settings.json"
    return (p,)

data_bibbl_settings = DataBIBBLSettings()  # singleton


class DataCIBBLSettings(BaseSettings):

  @property
  def files(self):
    data_path = settings["cibblbibbl-data.path"]
    p = pathlib.Path(data_path)
    p /= "cibbl"
    p /= "settings.json"
    return (p,)

data_cibbl_settings = DataCIBBLSettings()  # singleton

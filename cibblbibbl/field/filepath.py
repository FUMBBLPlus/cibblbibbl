from . import base

@property
def idfilename(self, extension=None):
  if extension is None:
    extension = ".json"
  if self.Id.isdecimal():
    return f'{self.Id:0>8}{extension}'
  else:
    return f'{self.Id}{extension}'

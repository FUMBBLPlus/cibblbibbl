from . import base

@property
def idfilename(self):
  if self.Id.isdecimal():
    return f'{self.Id:0>8}.json'
  else:
    return f'{self.Id}.json'

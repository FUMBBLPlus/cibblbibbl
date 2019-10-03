
def keyigetterproperty(keyi, doc=None):
  return property(
    lambda self, keyi=keyi: self._KEY[keyi],   # fget
    None,  # fset
    None,  # fdel
    doc
  )

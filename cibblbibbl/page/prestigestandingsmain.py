from .mastercls import Page

import cibblbibbl

from .. import field
from .prestigestandings import PrestigeStandings


class PrestigeStandingsMain(Page):

  rank = 20
  season = field.instrep.keyigetterproperty(1)
  year = field.common.DiggedAttr("season", "year")

  @classmethod
  def agent01(cls, group):
    yield from (cls(group),)

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.group.key
      / "page"
      /  f'{self.clskey()}.json'
    )
    return p

  def bbcodecontent(self):
    subnotepages = self.subnotepages()
    years = list(reversed(sorted(subnotepages)))
    currP = sorted(subnotepages[years[0]])[-1]
    currPbbcode = bbcode.notepage(
        currP,
        f'Year {currP.year.nr} {currP.season.name}'
    )
    parts = []
    parts.append(bbcode.center(bbcode.size(bbcode.b(
        f'Current: {currPbbcode}'
    ), 16)))
    parts.append("")
    for Y in years:
        parts.append(bbcode.center(bbcode.size(bbcode.b(
            f'Year {Y.nr}'
        ),16)) + "\\")
        parts.append(bbcode.center(
            "\\\n"
            + "\\\n • \\\n".join(
                bbcode.notepage(P, P.season.name)
                for P in sorted(subnotepages[Y])
            )
            + "\\\n"
        ))
    return "\n".join(parts)

  def notelink(self):
    return "-".join([
        self.group.config["name"],
        "Standings",
    ])

  def pagedata(self, ensure_titleimgurl=True):
    d = {
      "content": self.bbcodecontent()
    }
    if ensure_titleimgurl and "titleimgurl" not in self:
      path = self.titleimgfilepath(ensure=True)
      S = cibblbibbl.session
      if not S:
        msg = "fumbbl_session module was not imported"
        raise Exception(msg)
      if not S.logged_in():
        msg = "fumbbl_session is not logged in"
        raise Exception(msg)
      folder_id = self.get("galleryfolderId", 0)
      S.gallery.upload_image_file(path, folder_id)
      L = sorted(
        I for I in S.gallery.get_image_list(folder_id)
        if I.status is S.gallery.ImageStatus.new
      )
      assert L
      imageId = L[-1].id
      d["titleimgurl"] = self["titleimgurl"] = f'/i/{imageId}'
    return d

  def subnotepages(self):
    d = collections.defaultdict(set)
    for PS in PrestigeStandings.__members__.values():
      if not (PS.group is self.group):
        continue
      if PS.season.status() != "Completed":
        continue
      d[PS.year].add(PS)
    return d

  def titleimgfilepath(self, ensure=True):
    p = self.configfilepath
    fp = p.parent / f'{p.stem}.png'
    if not fp.is_file():
      cibblbibbl.pagetitle.generate(
          "squealer",
          self.titleimgtext(),
          fp,
      )
    return fp

  def titleimgtext(self):
    return f'{self.group.config["name"]} Standings'


cls = PrestigeStandingsMain

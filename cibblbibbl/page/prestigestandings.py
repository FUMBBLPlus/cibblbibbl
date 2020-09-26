from .mastercls import Page

import cibblbibbl

from .. import field


class PrestigeStandings(Page):

  rank = 10
  season = field.instrep.keyigetterproperty(1)
  year = field.common.DiggedAttr("season", "year")

  @classmethod
  def agent01(cls, group):
    yield from (cls(group, season) for season in group.seasons)

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.group.key
      / "page"
      /  f'{self.clskey()}'
      / f'y{self.season.year.nr}s{self.season.nr}.json'
    )
    return p

  @property
  def next(self):
    S = self.season.next
    if S:
      return self.__class__.__members__[(self.group, S)]

  @property
  def prev(self):
    S = self.season.prev
    if S:
      return self.__class__.__members__[(self.group, S)]

  @property
  def staticstandingsdata(self):
    if not hasattr(self, "_staticstandingsdata"):
      d = {
          Te: (a, nr, pr, tprs, Te)
          for a, (nr, pr, tprs, Te)
          in enumerate(self.season.prestigestandings(), 1)
      }
      setattr(self, "_staticstandingsdata", d)
    return getattr(self, "_staticstandingsdata")

  def bbcodetable(self):
    BC = cibblbibbl.bbcode
    L = sorted(self.dynamicstandingsdata().values())
    tooltipset = {t[5] for t in L}
    tooltips = {
        tprs: i
        for i, tprs in enumerate(sorted(tooltipset))
    }
    golds = self.season.gold_partner_teams()
    silvers = self.season.silver_partner_teams()
    rows = []
    prev_nr = None
    for a, nr, move, Te, pr, tprs, prdelta in L:
      roster = Te.roster_name
      coach = Te.coach_name
      teambbcode = BC.team(Te)
      if Te in golds:
        img = self["goldpartnerimg"]
        teambbcode = f'{BC.img(img)} {teambbcode}'
      elif Te in silvers:
        img = self["silverpartnerimg"]
        teambbcode = f'{BC.img(img)} {teambbcode}'
      prstr = BC.tooltiped(f'tprs{tooltips[tprs]}', str(pr))
      if nr == prev_nr:
          nrstr = ""
      else:
          nrstr = str(nr)
          prev_nr = nr
      row = [
          nrstr,
          BC.move(move),
          teambbcode,
          roster,
          BC.coach(coach),
          prstr,
          ("" if prdelta is None else str(prdelta)),
      ]
      rows.append(row)
    s_table = cibblbibbl.bbcode.table(rows,
        align = self["tablealign"],
        header = self["tableheader"],
        width = self["tablewidth"],
    )
    s_tooltips = f'\\{BC.N}'.join([
        BC.tooltip(
            f'tprs{tooltips[tprs]}',
            (
                "Team prestiges (tiebreaker): "
                f'{", ".join(str(x) for x in tprs)}'
            )
        )
        for tprs in sorted(tooltipset)
    ])
    return f'{s_table}\\{BC.N}{s_tooltips}'


  def dynamicstandingsdata(self):
    prev = self.prev
    if prev:
      prevstd = prev.staticstandingsdata
    else:
      prevstd = {}
    d = {}
    for t in self.staticstandingsdata.values():
      a, nr, pr, tprs, Te = t
      prevr = prevstd.get(Te)
      if prevr:
        move = prevr[1] - nr
        prdelta = pr - prevr[2]
      else:
        move = "NEW"
        prev_ = prev
        while prev_ and prev_.prev:
          prev_ = prev_.prev
          if prev_.staticstandingsdata.get(Te):
            move = "RET"
            break
        prdelta = None
      d[Te] = [a, nr, move, Te, pr, tprs, prdelta]
    return d

  def notelink(self):
    return "-".join([
        self.group.config["name"],
        "Standings",
        f'Y{self.year.nr}',
        self.season.name,
    ])

  def pagedata(self, ensure_titleimgurl=True):
    d = {
      "table": self.bbcodetable()
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
    return " • ".join([
        f'{self.group.config["name"]} Standings',
        f'Year {self.year.nr} {self.season.name}',
    ])


cls = PrestigeStandings

# Sunday 22 November 2026: 37 dated stories, 7 regions — COP31 deal nears, Iran strikes US bases in Bahrain, Peru quake, Sinaloa kingpin seized

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/jontumpil/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/jontumpil/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One day's world news summed up in a single image: a classic broadsheet
front page, drawn programmatically, carrying 37 stories that happened or
were first reported on Sunday 22 November 2026 across 7 regions.

## The front page

- **Masthead** — "THE WORLD IN ONE DAY", with the date in a red band:
  SUNDAY 22 NOVEMBER 2026.
- **Lead story** — Antalya, Türkiye: COP31 nears a final deal as the
  climate talks run into overtime, drawn with a sun over the conference
  dome.
- **Twelve story cards**, each with a bold drawn icon, a place tag, a
  headline and a one-line summary: Iran strikes US bases in Bahrain,
  Russian missiles hit Poland, a 6.9 quake shakes Peru, the Sparta II
  ablaze in the Gulf of Finland, kingpin 'El Chapo Isidro' seized in
  Sinaloa, a mass drone barrage on Kyiv, UN 'killer robot' rules, the
  Basra power-plant fire, Nepal's PM beginning his India visit,
  Eisenkot's coalition talks in Jerusalem, the hacked FBI crime
  database, and the EU–Indonesia trade deal after ten years.
- **The Day in Briefs** — 24 more one-line stories in three tight
  columns, from Riyadh and Hormuz to the G20 Florida summit and three
  EU reset deals signed in London.

## Run it

- `python3 draw_frontpage.py` — regenerates `entry.png` (build-time
  only; needs Pillow).
- `python3 main.py` — copies `entry.png` into the output directory
  (`$MAKEFUN_OUTPUT_DIR`, default `/output`). Standard library only,
  no network, deterministic: two runs produce identical bytes.

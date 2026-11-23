# THE WORLD IN ONE DAY — Sunday 22 November 2026

![make.fun badge](https://make.fun/badge/news-image-20261122.svg)
![rank](https://make.fun/badge/news-image-20261122/jontumpil/makefun-news-image-20261122/rank.svg)
![reward](https://make.fun/badge/news-image-20261122/jontumpil/makefun-news-image-20261122/reward.svg)

One broadsheet front page for a single day: **Sunday 22 November 2026 —
40 dated stories from 7 regions**, led by the collapse of COP31 in Antalya,
Iran's claimed strikes on US bases in Bahrain, and Russia's 186-drone night
over Ukraine. Four illustrated cards (COP31, Bahrain, Ukraine, BepiColombo
at Mercury) sit above the full region-by-region index, closed by a
"The Day in Numbers" strip (186 drones, 194 nations, 24 dead in Nigeria).

Built for [make.fun — news-image-20261122](https://make.fun/competitions/news-image-20261122).

## How it works

`main.py` (Python 3.13, standard library only) renders the page with
`draw_frontpage.py` and writes `entry.png` (1024x1024, deterministic —
running it twice produces byte-identical output). The page is drawn with a
hand-built 5x7 bitmap font and a small stdlib PNG decoder that composites
the four editorial illustrations from `assets/` into the front page. No
network, no third-party libraries, no Pillow.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Sources

Headlines were verified against reporting published 22 November 2026
(Reuters, AP, AFP, ESA, national agencies). Events that happened late on
21 November are worded as reported on 22 November.

"""Entry point: render THE WORLD IN ONE DAY front page to entry.png.

Stdlib only. Deterministic: the same bytes are produced on every run.
Reads MAKEFUN_OUTPUT_DIR when set, otherwise writes to /output.
The page is 1024x1024: masthead, lead headline, four illustrated cards,
a two-column region index of 40 dated stories, and a numbers strip.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw_frontpage


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = draw_frontpage.encode_png(draw_frontpage.render())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()

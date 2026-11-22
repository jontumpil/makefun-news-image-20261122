#!/usr/bin/env python3
"""Render entry.png: one day of world news as a broadsheet front page.

Sunday 22 November 2026 -- a lead story, twelve drawn story cards and a
briefs column, 37 dated stories in total. Build-time only: this script
uses Pillow, while the shipped main.py is standard library only.

Run:  python3 draw_frontpage.py   (writes entry.png next to this file)
"""

import glob
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = 1024
MARGIN = 28
INNER = W - 2 * MARGIN

PAPER = (246, 241, 227)
CARD_BG = (253, 250, 242)
INK = (20, 18, 14)
RED = (140, 29, 24)
GRAY = (92, 85, 73)
RULE = (178, 166, 140)
GOLD = (178, 128, 36)


def find_font(pattern):
    hits = sorted(glob.glob(pattern, recursive=True))
    if not hits:
        raise SystemExit("font not found: " + pattern)
    return hits[0]


SERIF_BOLD = find_font("/usr/share/fonts/**/DejaVuSerif-Bold.ttf")
SANS_BOLD = find_font("/usr/share/fonts/**/DejaVuSans-Bold.ttf")
SANS = find_font("/usr/share/fonts/**/DejaVuSans.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def fit(d, s, path, size, max_w, min_size=10):
    """Largest font (starting at size) that keeps s within max_w."""
    while size > min_size and d.textlength(s, font=font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(d, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def wrap_rich(d, segments, max_w):
    """Greedy wrap for mixed-font lines.

    segments: list of (text, font, color). Returns a list of lines, each a
    list of (word, font, color) tokens.
    """
    tokens = []
    for text, f, c in segments:
        for wd in text.split(" "):
            if wd:
                tokens.append((wd, f, c))
    lines, cur, cur_w = [], [], 0.0
    for wd, f, c in tokens:
        w = d.textlength(wd, font=f)
        add = w if not cur else w + d.textlength(" ", font=f)
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(wd, f, c)], w
        else:
            cur.append((wd, f, c))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich_line(d, x, y, line):
    cx = x
    for wd, f, c in line:
        d.text((cx, y), wd, font=f, fill=c)
        cx += d.textlength(wd, font=f) + d.textlength(" ", font=f)
    return cx


def wave(d, x0, y, length, amp, waves, color, width=3):
    pts = []
    steps = 28
    for i in range(steps + 1):
        px = x0 + length * i / steps
        py = y + amp * math.sin(i / steps * math.pi * 2 * waves)
        pts.append((px, py))
    d.line(pts, fill=color, width=width)


def flame(d, cx, top, h, w):
    d.polygon([(cx, top), (cx - w / 2, top + h * 0.62),
               (cx - w * 0.22, top + h), (cx + w * 0.22, top + h),
               (cx + w / 2, top + h * 0.62)], fill=RED)
    d.polygon([(cx, top + h * 0.36), (cx - w * 0.24, top + h * 0.72),
               (cx, top + h * 0.94), (cx + w * 0.24, top + h * 0.72)],
              fill=GOLD)


# ---------------------------------------------------------------- icons
# Each icon draws inside the box (x, y, s) with bold flat shapes.

def icon_missile(d, x, y, s):
    d.line([x + 0.22 * s, y + 0.78 * s, x + 0.66 * s, y + 0.34 * s],
           fill=INK, width=13)
    d.ellipse([x + 0.63 * s, y + 0.09 * s, x + 0.91 * s, y + 0.37 * s],
              fill=INK)
    d.line([x + 0.26 * s, y + 0.62 * s, x + 0.10 * s, y + 0.80 * s],
           fill=INK, width=5)
    d.line([x + 0.38 * s, y + 0.74 * s, x + 0.52 * s, y + 0.90 * s],
           fill=INK, width=5)
    d.ellipse([x + 0.02 * s, y + 0.78 * s, x + 0.22 * s, y + 0.98 * s],
              fill=RED)
    d.ellipse([x + 0.07 * s, y + 0.83 * s, x + 0.17 * s, y + 0.93 * s],
              fill=GOLD)


def icon_burst(d, x, y, s):
    cx, cy = x + 0.5 * s, y + 0.5 * s
    for k in range(8):
        a = k * math.pi / 4
        d.line([cx + 0.20 * s * math.cos(a), cy + 0.20 * s * math.sin(a),
                cx + 0.46 * s * math.cos(a), cy + 0.46 * s * math.sin(a)],
               fill=INK, width=5)
    d.ellipse([cx - 0.17 * s, cy - 0.17 * s, cx + 0.17 * s, cy + 0.17 * s],
              fill=RED)
    d.ellipse([cx - 0.07 * s, cy - 0.07 * s, cx + 0.07 * s, cy + 0.07 * s],
              fill=GOLD)


def icon_quake(d, x, y, s):
    d.rectangle([x + 0.10 * s, y + 0.30 * s, x + 0.42 * s, y + 0.82 * s],
                outline=INK, width=4)
    d.rectangle([x + 0.56 * s, y + 0.16 * s, x + 0.90 * s, y + 0.82 * s],
                outline=INK, width=4)
    d.line([x + 0.73 * s, y + 0.20 * s, x + 0.64 * s, y + 0.40 * s,
            x + 0.75 * s, y + 0.56 * s, x + 0.66 * s, y + 0.74 * s],
           fill=RED, width=3)
    wave(d, x + 0.06 * s, y + 0.92 * s, 0.88 * s, 0.035 * s, 3, INK, 3)


def icon_ship(d, x, y, s):
    d.polygon([(x + 0.06 * s, y + 0.58 * s), (x + 0.94 * s, y + 0.58 * s),
               (x + 0.80 * s, y + 0.80 * s), (x + 0.20 * s, y + 0.80 * s)],
              fill=INK)
    d.rectangle([x + 0.30 * s, y + 0.44 * s, x + 0.60 * s, y + 0.58 * s],
                fill=INK)
    d.line([x + 0.72 * s, y + 0.58 * s, x + 0.72 * s, y + 0.28 * s],
           fill=INK, width=4)
    flame(d, x + 0.45 * s, y + 0.04 * s, 0.36 * s, 0.30 * s)
    wave(d, x + 0.04 * s, y + 0.90 * s, 0.92 * s, 0.03 * s, 3, INK, 3)


def icon_cuffs(d, x, y, s):
    d.ellipse([x + 0.06 * s, y + 0.32 * s, x + 0.52 * s, y + 0.80 * s],
              outline=INK, width=5)
    d.ellipse([x + 0.48 * s, y + 0.32 * s, x + 0.94 * s, y + 0.80 * s],
              outline=INK, width=5)
    d.ellipse([x + 0.40 * s, y + 0.06 * s, x + 0.60 * s, y + 0.24 * s],
              outline=RED, width=4)
    d.ellipse([x + 0.24 * s, y + 0.14 * s, x + 0.42 * s, y + 0.30 * s],
              outline=RED, width=4)
    d.ellipse([x + 0.58 * s, y + 0.14 * s, x + 0.76 * s, y + 0.30 * s],
              outline=RED, width=4)


def icon_drone(d, x, y, s):
    d.line([x + 0.18 * s, y + 0.18 * s, x + 0.82 * s, y + 0.82 * s],
           fill=INK, width=5)
    d.line([x + 0.82 * s, y + 0.18 * s, x + 0.18 * s, y + 0.82 * s],
           fill=INK, width=5)
    for cx, cy in [(0.14, 0.14), (0.86, 0.14), (0.14, 0.86), (0.86, 0.86)]:
        r = 0.13 * s
        d.ellipse([x + cx * s - r, y + cy * s - r,
                   x + cx * s + r, y + cy * s + r], outline=INK, width=4)
    d.rectangle([x + 0.37 * s, y + 0.37 * s, x + 0.63 * s, y + 0.63 * s],
                fill=INK)
    d.ellipse([x + 0.44 * s, y + 0.44 * s, x + 0.56 * s, y + 0.56 * s],
              fill=RED)


def icon_robot(d, x, y, s):
    d.line([x + 0.5 * s, y + 0.28 * s, x + 0.5 * s, y + 0.10 * s],
           fill=INK, width=4)
    d.ellipse([x + 0.43 * s, y + 0.02 * s, x + 0.57 * s, y + 0.16 * s],
              fill=RED)
    d.rectangle([x + 0.20 * s, y + 0.28 * s, x + 0.80 * s, y + 0.84 * s],
                fill=INK)
    d.rectangle([x + 0.11 * s, y + 0.46 * s, x + 0.20 * s, y + 0.66 * s],
                fill=INK)
    d.rectangle([x + 0.80 * s, y + 0.46 * s, x + 0.89 * s, y + 0.66 * s],
                fill=INK)
    for cx in (0.38, 0.62):
        d.ellipse([x + (cx - 0.07) * s, y + 0.44 * s,
                   x + (cx + 0.07) * s, y + 0.58 * s], fill=PAPER)
    d.line([x + 0.36 * s, y + 0.70 * s, x + 0.64 * s, y + 0.70 * s],
           fill=PAPER, width=3)


def icon_factory(d, x, y, s):
    d.rectangle([x + 0.62 * s, y + 0.32 * s, x + 0.77 * s, y + 0.58 * s],
                fill=INK)
    d.rectangle([x + 0.08 * s, y + 0.58 * s, x + 0.92 * s, y + 0.86 * s],
                fill=INK)
    d.polygon([(x + 0.08 * s, y + 0.58 * s), (x + 0.34 * s, y + 0.44 * s),
               (x + 0.60 * s, y + 0.58 * s)], fill=INK)
    flame(d, x + 0.695 * s, y + 0.0 * s, 0.30 * s, 0.26 * s)
    for wx in (0.24, 0.44, 0.64):
        d.rectangle([x + wx * s, y + 0.66 * s, x + (wx + 0.09) * s,
                     y + 0.76 * s], fill=GOLD)


def icon_flags(d, x, y, s):
    d.line([x + 0.08 * s, y + 0.90 * s, x + 0.92 * s, y + 0.90 * s],
           fill=INK, width=3)
    d.line([x + 0.28 * s, y + 0.10 * s, x + 0.28 * s, y + 0.90 * s],
           fill=INK, width=4)
    d.polygon([(x + 0.28 * s, y + 0.12 * s), (x + 0.60 * s, y + 0.20 * s),
               (x + 0.28 * s, y + 0.30 * s)], fill=RED)
    d.line([x + 0.64 * s, y + 0.10 * s, x + 0.64 * s, y + 0.90 * s],
           fill=INK, width=4)
    d.polygon([(x + 0.64 * s, y + 0.12 * s), (x + 0.94 * s, y + 0.20 * s),
               (x + 0.64 * s, y + 0.30 * s)], fill=INK)


def icon_columns(d, x, y, s):
    d.polygon([(x + 0.06 * s, y + 0.30 * s), (x + 0.50 * s, y + 0.06 * s),
               (x + 0.94 * s, y + 0.30 * s)], fill=INK)
    d.rectangle([x + 0.10 * s, y + 0.32 * s, x + 0.90 * s, y + 0.40 * s],
                fill=INK)
    for cx in (0.24, 0.50, 0.76):
        d.line([x + cx * s, y + 0.44 * s, x + cx * s, y + 0.74 * s],
               fill=INK, width=7)
    d.rectangle([x + 0.10 * s, y + 0.76 * s, x + 0.90 * s, y + 0.84 * s],
                fill=INK)


def icon_shield_bug(d, x, y, s):
    d.polygon([(x + 0.50 * s, y + 0.05 * s), (x + 0.88 * s, y + 0.15 * s),
               (x + 0.88 * s, y + 0.48 * s), (x + 0.50 * s, y + 0.95 * s),
               (x + 0.12 * s, y + 0.48 * s), (x + 0.12 * s, y + 0.15 * s)],
              outline=INK, width=5)
    d.ellipse([x + 0.37 * s, y + 0.34 * s, x + 0.63 * s, y + 0.68 * s],
              fill=RED)
    d.ellipse([x + 0.43 * s, y + 0.22 * s, x + 0.57 * s, y + 0.36 * s],
              fill=RED)
    d.line([x + 0.38 * s, y + 0.42 * s, x + 0.24 * s, y + 0.33 * s],
           fill=INK, width=3)
    d.line([x + 0.37 * s, y + 0.56 * s, x + 0.24 * s, y + 0.60 * s],
           fill=INK, width=3)
    d.line([x + 0.62 * s, y + 0.42 * s, x + 0.76 * s, y + 0.33 * s],
           fill=INK, width=3)
    d.line([x + 0.63 * s, y + 0.56 * s, x + 0.76 * s, y + 0.60 * s],
           fill=INK, width=3)


def icon_deal(d, x, y, s):
    d.line([x + 0.24 * s, y + 0.08 * s, x + 0.24 * s, y + 0.88 * s],
           fill=INK, width=4)
    d.polygon([(x + 0.24 * s, y + 0.10 * s), (x + 0.56 * s, y + 0.18 * s),
               (x + 0.24 * s, y + 0.28 * s)], fill=RED)
    d.line([x + 0.58 * s, y + 0.08 * s, x + 0.58 * s, y + 0.88 * s],
           fill=INK, width=4)
    d.polygon([(x + 0.58 * s, y + 0.10 * s), (x + 0.90 * s, y + 0.18 * s),
               (x + 0.58 * s, y + 0.28 * s)], fill=INK)
    d.ellipse([x + 0.60 * s, y + 0.52 * s, x + 0.92 * s, y + 0.84 * s],
              outline=GOLD, width=5)
    d.ellipse([x + 0.71 * s, y + 0.63 * s, x + 0.81 * s, y + 0.73 * s],
              fill=RED)


ICONS = {
    "missile": icon_missile,
    "burst": icon_burst,
    "quake": icon_quake,
    "ship": icon_ship,
    "cuffs": icon_cuffs,
    "drone": icon_drone,
    "robot": icon_robot,
    "factory": icon_factory,
    "flags": icon_flags,
    "columns": icon_columns,
    "shield": icon_shield_bug,
    "deal": icon_deal,
}

CARDS = [
    ("missile", "MANAMA, BAHRAIN", "IRAN STRIKES US BASES",
     "Missiles and drones hit al-Riffa and Awali; plant ablaze on Sitra, "
     "no injuries"),
    ("burst", "POLAND / NATO", "RUSSIAN MISSILES HIT POLAND",
     "Alliance calls it a violation; jets scramble over Estonia"),
    ("quake", "LIMA, PERU", "6.9 QUAKE SHAKES PERU",
     "Residents flee their homes as tremor strikes the capital"),
    ("ship", "GULF OF FINLAND", "SPARTA II ABLAZE",
     "Drones hit Russian cargo ship; fire drifts into Finnish waters"),
    ("cuffs", "SINALOA, MEXICO", "KINGPIN 'EL CHAPO ISIDRO' SEIZED",
     "FBI top-10 boss taken in military raid; violence erupts"),
    ("drone", "KYIV, UKRAINE", "MASS DRONE BARRAGE",
     "Bridges over the Dnipro struck; three killed"),
    ("robot", "UNITED NATIONS", "'KILLER ROBOT' RULES BY 2028",
     "States agree UN talks on a pact for AI weapons"),
    ("factory", "BASRA, IRAQ", "POWER PLANT FIRE KILLS 4",
     "Blast at Al-Haritha station; PM orders swift probe"),
    ("flags", "KATHMANDU", "NEPAL PM BEGINS INDIA VISIT",
     "Balendra Shah opens two-day state visit"),
    ("columns", "JERUSALEM", "EISENKOT OPENS COALITION TALKS",
     "Bennett backs unity government, rules out Netanyahu bloc"),
    ("shield", "WASHINGTON", "FBI CRIME DATABASE HACKED",
     "Breach lands amid a week of US tech outages"),
    ("deal", "BRUSSELS / JAKARTA", "EU–INDONESIA DEAL AFTER 10 YEARS",
     "Trade pact finally reached after a decade of talks"),
]

BRIEFS = [
    ("RIYADH", "blasts heard after air-threat alert"),
    ("HORMUZ", "two ships attacked, one hit near Khasab"),
    ("GAZA", "strike kills 3 in aid car"),
    ("FRANCE", "living-cost marches calm, turnout falls"),
    ("SUDAN", "rebels seize Bau as toll passes 2,230"),
    ("SOUTH SUDAN", "200,000-tonne food stockpile plan"),
    ("NIGERIA", "24 mourners die as funeral boat capsizes"),
    ("PAKISTAN", "7 killed in tribal firefight"),
    ("INDIA", "11 die from tainted liquor in Manipur"),
    ("ESTONIA", "closes all road borders with Russia for 6 months"),
    ("SOUTH AFRICA", "ANC fights to hold big cities"),
    ("YEMEN", "Taiz services collapse under siege"),
    ("OIL", "crude rises on Iran war worries"),
    ("CHINA", "Beijing to bar young 'red-chip' offshore listings"),
    ("NEW YORK", "Mamdani unveils plan to close Rikers by 2032"),
    ("HAITI", "signs prison deal with El Salvador"),
    ("MALAYSIA", "confusion over 10,000 Rohingya resettlement plan"),
    ("JAPAN", "PM Takaichi gets scaled-down welcome in China"),
    ("PEACE TALKS", "Zelenskyy: timing hinges on US coordinating all sides"),
    ("G20", "Trump says all top-20 leaders bound for Florida summit"),
    ("BRAZIL", "severe storm batters southern city"),
    ("CAMEROON", "decade of war leaves families displaced"),
    ("DENMARK", "urges EU curbs on Russian visas after foiled plot"),
    ("LONDON", "Burnham signs three EU reset deals"),
]


def draw_lead_scene(d, sx, sy, sw, sh):
    """Sun over a conference dome with small flags."""
    basey = sy + sh - 18
    cx = sx + sw // 2
    # sun with rays, top right
    sunx, suny, sunr = sx + sw - 42, sy + 26, 19
    for k in range(8):
        a = k * math.pi / 4
        d.line([sunx + (sunr + 3) * math.cos(a), suny + (sunr + 3) * math.sin(a),
                sunx + (sunr + 11) * math.cos(a), suny + (sunr + 11) * math.sin(a)],
               fill=INK, width=3)
    d.ellipse([sunx - sunr, suny - sunr, sunx + sunr, suny + sunr], fill=GOLD)
    # dome
    rx, ry = 86, 62
    d.pieslice([cx - rx, basey - ry, cx + rx, basey + ry], 180, 360, fill=INK)
    d.rectangle([cx - rx - 10, basey, cx + rx + 10, basey + 8], fill=INK)
    d.rectangle([cx - 9, basey - 24, cx + 9, basey], fill=PAPER)
    # flags along the dome curve
    for dx in (-52, 0, 52):
        top = basey - ry * math.sqrt(max(0.0, 1 - (dx / rx) ** 2))
        px = cx + dx
        d.line([px, top, px, top - 17], fill=INK, width=3)
        d.polygon([(px, top - 17), (px + 14, top - 12), (px, top - 7)],
                  fill=RED)
    d.line([sx + 6, basey + 16, sx + sw - 6, basey + 16], fill=INK, width=3)


def render():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.line([MARGIN, 6, W - MARGIN, 6], fill=INK, width=3)
    d.line([MARGIN, 11, W - MARGIN, 11], fill=INK, width=1)
    title = "THE WORLD IN ONE DAY"
    tf = fit(d, title, SERIF_BOLD, 66, INNER)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 16), title, font=tf, fill=INK)

    band_y, band_h = 86, 46
    d.rectangle([MARGIN, band_y, W - MARGIN, band_y + band_h], fill=RED)
    date = "SUNDAY 22 NOVEMBER 2026"
    df = fit(d, date, SANS_BOLD, 33, INNER - 40)
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, band_y + (band_h - 33) / 2 - 2), date,
           font=df, fill=(255, 255, 255))

    strap = "37 dated stories · 7 regions · one front page"
    sf = font(SANS, 18)
    swd = d.textlength(strap, font=sf)
    d.text(((W - swd) / 2, 138), strap, font=sf, fill=GRAY)
    d.line([MARGIN, 164, W - MARGIN, 164], fill=INK, width=2)

    # ---- lead panel
    lead_y, lead_h = 172, 152
    d.rectangle([MARGIN, lead_y, W - MARGIN, lead_y + lead_h],
                fill=CARD_BG, outline=INK, width=2)
    lx = MARGIN + 16
    text_right = 688
    d.text((lx, lead_y + 12), "ANTALYA, TÜRKIYE",
           font=font(SANS_BOLD, 13), fill=RED)
    lead_head = "COP31 NEARS FINAL DEAL"
    hf = fit(d, lead_head, SANS_BOLD, 46, text_right - lx)
    d.text((lx, lead_y + 32), lead_head, font=hf, fill=INK)
    sub = ("Climate talks run into overtime; approval session set for "
           "Sunday morning after fossil-fuel row")
    subf = font(SANS, 18)
    yy = lead_y + 86
    for line in wrap(d, sub, subf, text_right - lx):
        d.text((lx, yy), line, font=subf, fill=INK)
        yy += 24
    draw_lead_scene(d, 700, lead_y + 8, 284, lead_h - 16)

    # ---- story cards, 3 columns x 4 rows
    grid_y = 332
    card_w = (INNER - 16) // 3
    card_h, gap = 106, 7
    tagf = font(SANS_BOLD, 12)
    headf = font(SANS_BOLD, 19)
    subf2 = font(SANS, 11)
    for i, (icon, place, head, subline) in enumerate(CARDS):
        r, c = divmod(i, 3)
        x = MARGIN + c * (card_w + 8)
        y = grid_y + r * (card_h + gap)
        d.rectangle([x, y, x + card_w, y + card_h], fill=CARD_BG,
                    outline=RULE, width=1)
        d.rectangle([x, y, x + card_w, y + 3], fill=RED)
        ICONS[icon](d, x + 9, y + 26, 52)
        tx = x + 70
        tw2 = card_w - 70 - 8
        d.text((tx, y + 8), place, font=tagf, fill=RED)
        yy = y + 23
        for line in wrap(d, head, headf, tw2)[:2]:
            d.text((tx, yy), line, font=headf, fill=INK)
            yy += 21
        yy = y + 67
        for line in wrap(d, subline, subf2, tw2)[:3]:
            d.text((tx, yy), line, font=subf2, fill=GRAY)
            yy += 13

    # ---- briefs
    briefs_y = grid_y + 4 * card_h + 3 * gap + 14
    bf = font(SANS_BOLD, 17)
    d.text((MARGIN, briefs_y), "THE DAY IN BRIEFS", font=bf, fill=INK)
    bw = d.textlength("THE DAY IN BRIEFS", font=bf)
    d.line([MARGIN + bw + 12, briefs_y + 10, W - MARGIN, briefs_y + 10],
           fill=RULE, width=1)
    body_y = briefs_y + 26
    placef = font(SANS_BOLD, 11)
    restf = font(SANS, 11)
    col_w = (INNER - 36) // 3
    wrapped = []
    for place, rest in BRIEFS:
        segs = [("• ", placef, RED), (place + " ", placef, INK),
                (rest, restf, INK)]
        wrapped.append(wrap_rich(d, segs, col_w))
    columns = [[], [], []]
    heights = [0, 0, 0]
    for lines in wrapped:
        k = heights.index(min(heights))
        columns[k].append(lines)
        heights[k] += len(lines)
    for ci, col in enumerate(columns):
        cx = MARGIN + ci * (col_w + 18)
        yy = body_y
        for lines in col:
            for line in lines:
                draw_rich_line(d, cx, yy, line)
                yy += 13
            yy += 2

    # ---- footer
    foot = ("Every story above happened or was first reported on "
            "Sunday 22 November 2026.")
    ff = font(SANS, 13)
    fw = d.textlength(foot, font=ff)
    d.line([MARGIN, 980, W - MARGIN, 980], fill=INK, width=1)
    d.text(((W - fw) / 2, 988), foot, font=ff, fill=GRAY)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    render()

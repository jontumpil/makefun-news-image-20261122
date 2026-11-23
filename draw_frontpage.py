"""Render THE WORLD IN ONE DAY front page for Sunday 22 November 2026.

Stdlib only. Deterministic: no time, no randomness, no set iteration.
Draws a 1024x1024 broadsheet: masthead, lead headline, four illustrated
cards (PNG assets decoded with a small stdlib decoder), and 40 dated
stories grouped under 7 region headers.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 244, 230)
INK = (18, 18, 18)
RED = (158, 24, 24)
BLUE = (24, 58, 110)
GREY = (110, 104, 92)
LIGHT = (232, 224, 208)
GOLD = (176, 132, 40)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells ('#' = ink).
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def center(self, y, s, scale, color):
        self.text((self.w - self.text_width(s, scale)) // 2, y, s, scale, color)

    def wrap(self, s, max_chars):
        words = s.split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = wd if not cur else cur + ' ' + wd
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(path):
    """Decode an 8-bit non-interlaced PNG (colour types 0, 2, 4, 6)."""
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG: ' + path
    pos = 8
    width = height = None
    bitdepth = ctype = None
    interlace = 0
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        ctype4 = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if ctype4 == b'IHDR':
            width, height, bitdepth, ctype, _, _, interlace = struct.unpack(
                '>IIBBBBB', chunk)
        elif ctype4 == b'IDAT':
            idat += chunk
        elif ctype4 == b'IEND':
            break
        pos += 12 + length
    assert bitdepth == 8 and interlace == 0, 'unsupported PNG: ' + path
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    out = bytearray(width * height * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                line[i] = (line[i] + _paeth(a, b, c)) & 255
        for x in range(width):
            base = (y * width + x) * 3
            src = x * channels
            if channels == 1:
                g = line[src]
                out[base:base + 3] = bytes((g, g, g))
            elif channels == 2:
                g = line[src]
                out[base:base + 3] = bytes((g, g, g))
            elif channels == 3:
                out[base:base + 3] = line[src:src + 3]
            else:
                alpha = line[src + 3]
                if alpha == 0:
                    out[base:base + 3] = bytes(PAPER)
                else:
                    out[base:base + 3] = line[src:src + 3]
        prev = line
    return width, height, bytes(out)


def draw_image(cv, path, x, y, w, h):
    try:
        iw, ih, px = decode_png(path)
    except Exception:
        cv.rect(x, y, w, h, LIGHT)
        cv.rect(x, y, w, 4, RED)
        return
    for yy in range(h):
        sy = min(ih - 1, yy * ih // h)
        for xx in range(w):
            sx = min(iw - 1, xx * iw // w)
            i = (sy * iw + sx) * 3
            cv.set(x + xx, y + yy, (px[i], px[i + 1], px[i + 2]))


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack('>I', len(payload)) + tag + payload
        out += struct.pack('>I', zlib.crc32(tag + payload) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


def base_dir():
    return os.path.dirname(os.path.abspath(__file__))


# ---- The day's news: 40 dated stories, 7 regions -------------------------
# Headlines verified against reporting published 22 November 2026.
# Events that happened late on 21 Nov are worded as reported on 22 Nov.

LEAD = ("COP31 COLLAPSES IN ANTALYA: NO DEAL AS EU REJECTS PACT "
        "WITH NO FOSSIL FUELS")
LEAD_SUB = ("Longest climate summit in history ends without agreement - "
            "194 nations split over coal, oil and gas")

CARDS = [
    ("assets/cop31.png", "CLIMATE",
     "COP31 COLLAPSES: EU REJECTS PACT WITH NO FOSSIL FUELS"),
    ("assets/bahrain.png", "GULF",
     "IRAN CLAIMS STRIKES ON US BASES IN BAHRAIN"),
    ("assets/ukraine.png", "UKRAINE",
     "186 DRONES OVERNIGHT; APARTMENT BLOCK HIT NEAR KYIV"),
    ("assets/mercury.png", "SPACE",
     "BEPICOLOMBO ENTERS MERCURY ORBIT AFTER 8 YEARS"),
]

REGIONS = [
    ("NORTH AMERICA", [
        "US STOCKS IN CORRECTION: S&P 500 DOWN 3.7% FRIDAY, NASDAQ OFF 5.3%",
        "FBI PROBES REPORTED HACK OF NATIONAL CRIME DATABASE",
        "BESSENT WARNS FED AGAINST OVERTIGHTENING; TRUMP BLAMES DEMOCRATS",
        "INTEL CHIEF CONFIRMS PROBE OF ALICE HUANG AND MEGASPEED",
        "VERSTAPPEN WINS LAS VEGAS GRAND PRIX, THIRD WIN IN FOUR YEARS",
        "KANSAS CITY CURRENT BEAT WASHINGTON SPIRIT 2-1 FOR FIRST NWSL TITLE",
    ]),
    ("LATIN AMERICA", [
        "MEXICO CAPTURES CARTEL BOSS EL CHAPO ISIDRO; 11 KILLED IN RAID",
        "PERU: M5.0 AFTERSHOCK NEAR CARHUAMAYO; QUAKE TOLL 1 DEAD, 16 HURT",
        "HONG KONG AND CHILE SIGN WORKING HOLIDAY PACT FOR 2027",
        "SALVADORANS KILLED IN HAITI BLAST, FIRST DEATHS AFTER DEPLOYMENT",
        "US AND VENEZUELA RESTORE MILITARY COOPERATION AFTER HEGSETH VISIT",
    ]),
    ("EUROPE", [
        "COP31 COLLAPSES IN ANTALYA: NO DEAL AS EU REJECTS FOSSIL-FREE PACT",
        "RUSSIA FIRES 186 DRONES OVERNIGHT; APARTMENT BLOCK HIT, 3 DEAD",
        "RUSSIAN SHIP SPARTA II STILL BURNING IN GULF OF FINLAND",
        "SEA DRONES HIT RUSSIAN WARSHIP MERKURY AT BENGHAZI NAVAL BASE",
        "BEPICOLOMBO ENTERS MERCURY ORBIT AFTER EIGHT-YEAR TRIP",
        "UK-EU RESET ROW: MAY AGHAST AS BURNHAM FACES REJOIN QUESTION",
        "CYPRUS EXPELS TWO RUSSIAN DIPLOMATS OVER SPYING CLAIMS",
        "DENMARK SAYS IT FOILED PLOT TO KILL US-UKRAINIAN RAPPER",
    ]),
    ("MIDDLE EAST", [
        "IRAN CLAIMS MISSILE AND DRONE STRIKES ON US BASES IN BAHRAIN",
        "BAHRAIN SAYS INDUSTRIAL SITE HIT, TWO HURT, DEFENCES INTERCEPT",
        "IRAN STRIKES THREE TANKERS NEAR STRAIT OF HORMUZ; TWO CATCH FIRE",
        "EISENKOT CALLS WEST BANK SETTLER ATTACKS TERRORISM; 12 CARS TORCHED",
        "EISENKOT INVITES LIKUD TO MARATHON COALITION TALKS",
    ]),
    ("AFRICA", [
        "NIGERIA BOAT CAPSIZES ON WAY TO FUNERAL; AT LEAST 24 DEAD",
        "SUDAN DRONES HIT HOMES AND UN OFFICES IN KHARTOUM; 5 CHILDREN KILLED",
        "MASHABA SET FOR JOHANNESBURG MAYOR JOB AS PARTIES SEAL METRO PACT",
        "EXXONMOBIL GROUP APPROVES $4BN ANGOLA OIL PROJECT",
        "PHUMZILE MLAMBO-NGCUKA, EX-SA DEPUTY PRESIDENT, DIES AT 71",
    ]),
    ("ASIA", [
        "INDONESIA CANDY FACTORY FIRE: 3 DEAD, 36 MISSING IN CIKANDE",
        "UN COURT: MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA IN 2017",
        "EU AND INDONESIA SIGN LANDMARK TRADE DEAL AFTER DECADE OF TALKS",
        "APEC LEADERS PUBLISH SHENZHEN DECLARATION ON DIGITAL TRADE",
        "CHINA BARS NEW RED-CHIP FIRMS FROM OFFSHORE LISTINGS",
        "CHINESE CARS OUTSELL JAPANESE RIVALS IN 39 MARKETS",
        "INDIA: 11 DEAD, 180 IN HOSPITAL AFTER ILLICIT ALCOHOL IN MANIPUR",
    ]),
    ("OCEANIA / PACIFIC", [
        "XI HAILS COMPLETE TURNAROUND IN CHINA-AUSTRALIA TIES",
        "TAIWAN GIVES MARSHALL ISLANDS $20M CREDIT GUARANTEE",
        "M6.8 QUAKE STRIKES BANDA SEA NEAR TIMOR-LESTE",
        "ALL BLACKS COACH RENNIE UNDER PRESSURE AFTER ENGLAND LOSS",
    ]),
]

TOTAL_STORIES = sum(len(items) for _, items in REGIONS)


# ---- Layout ---------------------------------------------------------------

def render():
    cv = Canvas(W, H, PAPER)
    base = base_dir()
    margin = 28

    # Masthead
    cv.rect(0, 0, W, 4, RED)
    cv.center(16, "THE WORLD IN ONE DAY", 4, INK)
    cv.center(52, "SUNDAY 22 NOVEMBER 2026  -  40 DATED STORIES  -  7 REGIONS",
              1, RED)
    cv.hline(margin, 74, W - 2 * margin, INK, 2)

    # Lead headline (2 lines) + subhead
    y = 86
    for line in cv.wrap(LEAD, 44):
        cv.center(y, line, 2, INK)
        y += 18
    cv.center(y + 2, LEAD_SUB, 1, GREY)
    y += 20
    cv.hline(margin, y, W - 2 * margin, INK, 1)
    y += 10

    # Illustrated cards: 4 across
    card_w = (W - 2 * margin - 3 * 12) // 4
    card_h = 196
    img_h = 158
    for i, (img, tag, cap) in enumerate(CARDS):
        x = margin + i * (card_w + 12)
        draw_image(cv, os.path.join(base, img), x, y, card_w, img_h)
        cv.rect(x, y + img_h, card_w, 2, RED)
        cv.text(x + 2, y + img_h + 5, tag, 1, RED)
        cy = y + img_h + 16
        for line in cv.wrap(cap, card_w // 6 - 1):
            cv.text(x + 2, cy, line, 1, INK)
            cy += 9
    y += card_h + 26
    cv.hline(margin, y, W - 2 * margin, INK, 2)
    y += 10

    # Region stories in two columns. Split regions so columns stay balanced:
    # left: North America, Latin America, Europe (19 stories)
    # right: Middle East, Africa, Asia, Oceania (21 stories)
    col_w = (W - 2 * margin - 20) // 2
    left = REGIONS[:3]
    right = REGIONS[3:]
    col_end = y
    for col_x, groups in ((margin, left), (margin + col_w + 20, right)):
        yy = y
        for name, items in groups:
            cv.rect(col_x, yy, col_w, 16, BLUE)
            cv.text(col_x + 4, yy + 4, name, 1, PAPER)
            yy += 20
            for item in items:
                lines = cv.wrap("* " + item, col_w // 6 - 1)
                for line in lines:
                    cv.text(col_x + 2, yy, line, 1, INK)
                    yy += 12
                yy += 5
            yy += 5
        if yy > col_end:
            col_end = yy

    # By the numbers strip
    y = col_end + 14
    cv.hline(margin, y, W - 2 * margin, INK, 2)
    y += 10
    cv.text(margin, y, "THE DAY IN NUMBERS", 1, RED)
    y += 14
    stats = [
        ("186", "DRONES FIRED AT UKRAINE OVERNIGHT"),
        ("194", "NATIONS AT COP31 IN ANTALYA"),
        ("24", "DEAD AS NIGERIA BOAT CAPSIZES"),
        ("40", "DATED STORIES, 7 REGIONS, 1 DAY"),
    ]
    box_w = (W - 2 * margin - 3 * 12) // 4
    for i, (num, label) in enumerate(stats):
        x = margin + i * (box_w + 12)
        cv.rect(x, y, box_w, 52, LIGHT)
        cv.rect(x, y, box_w, 3, GOLD)
        cv.text(x + 8, y + 8, num, 2, RED)
        ly = y + 26
        for line in cv.wrap(label, box_w // 6 - 2):
            cv.text(x + 8, ly, line, 1, INK)
            ly += 9

    # Footer
    fy = H - 26
    cv.hline(margin, fy, W - 2 * margin, INK, 1)
    cv.text(margin, fy + 6,
            "40 DATED STORIES FROM 22 NOVEMBER 2026 - REPORTED BY REUTERS, AP, "
            "AFP, ESA AND NATIONAL AGENCIES", 1, GREY)
    cv.text(margin, fy + 15, "THE WORLD IN ONE DAY - ONE DAY, EVERY REGION, "
            "NOTHING INVENTED", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(render())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()

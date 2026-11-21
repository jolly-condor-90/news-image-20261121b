"""Draw the 21 November 2026 world-news front page.

All artwork, the map and the layout are drawn in code with Pillow.
The day's stories were researched from public news reports dated 21 Nov 2026.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 229)
INK = (26, 25, 23)
RED = (166, 36, 39)
MUTED = (92, 84, 72)
HAIR = (120, 110, 94)
OCEAN = (216, 232, 241)      # #D8E8F1
LAND = (234, 220, 185)       # #EADCB9
LAND_EDGE = (184, 161, 117)  # #B8A175
GRAT = (198, 222, 234)       # #C6DEEA

# Tujuh warna region — sesuai PROMPT_PETA.md dan legenda di bagian atas gambar.
REGIONS = [
    ("EUROPE", (44, 111, 176)),       # biru
    ("MIDDLE EAST", (210, 105, 30)),  # oranye
    ("AFRICA", (47, 139, 91)),        # hijau
    ("ASIA", (180, 58, 46)),          # merah
    ("AMERICAS", (119, 72, 168)),     # ungu
    ("OCEANIA", (17, 138, 142)),      # teal
    ("WORLD", (90, 100, 114)),        # abu
]
RCOL = {name: col for name, col in REGIONS}

# Penempatan badge hasil optimasi (0 tabrakan garis, offset maks 28.8 px).
# (nomor, cx, cy, ring) — dipakai build & audit agar identik.
PLACEMENT = [
  (1, 251.11, 790.58, 15), (2, 246.99, 827.13, 15), (3, 134.42, 866.43, 15),
  (4, 243.28, 775.72, 15), (5, 136.04, 790.14, 15), (6, 143.84, 804.45, 15),
  (7, 192.12, 763.18, 15), (8, 216.25, 800.98, 15), (9, 203.74, 782.77, 15),
  (10, 376.49, 894.20, 15), (11, 321.88, 823.25, 15), (12, 208.36, 849.75, 15),
  (13, 231.06, 792.25, 15), (14, 216.84, 773.46, 15), (15, 196.69, 797.31, 15),
  (16, 349.40, 875.60, 15), (17, 346.95, 816.99, 15), (18, 301.35, 807.39, 15),
  (19, 297.28, 825.30, 15), (20, 307.38, 852.52, 15), (21, 323.62, 848.21, 15),
  (22, 384.52, 868.56, 15), (23, 358.73, 789.62, 15), (24, 274.80, 824.83, 15),
  (25, 270.40, 794.26, 15), (26, 283.50, 804.44, 23), (27, 261.51, 835.61, 23),
  (28, 232.38, 818.46, 15), (29, 195.87, 838.23, 15), (30, 243.08, 882.11, 15),
  (31, 202.71, 823.35, 15), (32, 246.22, 857.15, 15), (33, 89.06, 822.27, 15),
  (34, 99.79, 835.30, 15), (35, 165.59, 882.57, 15),
]
POS = {p[0]: p for p in PLACEMENT}

# number, region, place, headline, detail, source, lon, lat, heat
STORIES = [
    (1, "EUROPE", "ANTALYA, TÜRKIYE", "COP31 climate talks run into Saturday with no deal",
     "Talks passed Friday's deadline. A draft with no fossil-fuel text splits nearly 200 nations; a third text is due Saturday.",
     "AFP · AP · BBC", 36.9, 36.9, 12),
    (2, "MIDDLE EAST", "RIYADH, SAUDI ARABIA", "Three Houthi missiles shot down over Riyadh",
     "Coalition says air defences destroyed three ballistic missiles after two blasts. Third night of alerts; no casualties reported.",
     "Reuters · AFP", 46.7, 24.7, 11),
    (3, "AMERICAS", "JUNÍN, PERU", "Magnitude 6.7 quake shakes Peru's Andes",
     "Deep tremor near Carhuamayo was felt in Lima at 00:09 UTC. Officials report no damage, deaths or tsunami threat.",
     "USGS · IGP · AP", -75.5, -11.0, 10),
    (4, "EUROPE", "KYIV, UKRAINE", "Russian barrage kills at least eight in Kyiv",
     "Overnight strikes hit the power grid; Poland says two Russian missiles and a drone entered its airspace.",
     "AP · Reuters", 30.5, 50.5, 9),
    (5, "AMERICAS", "WASHINGTON, USA", "Trump threatens 'tremendous tax' on AI data centres abroad",
     "The president gave no details after returning from the China summit, and said his own staff had not been briefed.",
     "AP", -77.0, 38.9, 8),
    (6, "WORLD", "NEW YORK, USA", "Wall Street rout: S&P 500 −3.7%, Nasdaq −5.3%",
     "AI sell-off pushes the S&P and Dow into correction; Bitcoin slides below $56,000, a two-year low.",
     "AP · Reuters", -74.0, 40.7, 8),
    (7, "WORLD", "MERCURY ORBIT", "BepiColombo reaches Mercury after eight years",
     "ESA/JAXA craft fires its arrival burn; only the second mission ever to orbit the innermost planet.",
     "ESA · Sky & Telescope", 0.0, 76.0, 7),
    (8, "EUROPE", "BRUSSELS, BELGIUM", "UK and EU seal trade and youth-mobility deals",
     "A second annual summit agrees food trade, linked carbon markets and easier study and travel for young people.",
     "Xinhua · Guardian", 4.4, 50.9, 7),
    (9, "WORLD", "GENEVA, SWITZERLAND", "Countries open path to a 'killer robot' treaty",
     "The 128 states party to the weapons convention agree to elaborate rules for autonomous arms over two years.",
     "AFP", 6.1, 46.2, 6),
    (10, "OCEANIA", "WELLINGTON, NZ", "Rahul's 136 puts India ahead of New Zealand",
     "India reach 486-4 at stumps on day three in Wellington, a lead of 118 runs; Gill falls for 98.",
     "AP · RNZ", 174.8, -41.3, 6),
    (11, "ASIA", "MYANMAR", "Myanmar rejects UN court's genocide ruling",
     "The government calls the ICJ verdict unfair; Switzerland and the EU welcome it as a step for Rohingya justice.",
     "AP · Manila Times", 96.2, 16.8, 6),
    (12, "AFRICA", "BAYELSA, NIGERIA", "Ferry capsizes; at least four dead",
     "A boat carrying worshippers overturns; dozens are rescued and reported tolls differ between outlets.",
     "New Telegraph · Punch", 6.3, 4.9, 5),
    (13, "EUROPE", "COPENHAGEN", "Denmark expels Russian defence attaché",
     "Minister says 'enough is enough'; non-essential visas for Russians to stop.", "Anadolu", 12.6, 55.7, 5),
    (14, "EUROPE", "BERLIN", "Merz seeks '360-degree partnership' with Qatar",
     "Qatar pledges €15bn more in German investment; both sign defence pacts.", "Anadolu", 13.4, 52.5, 5),
    (15, "EUROPE", "PARIS", "France pushes fossil-fuel words into COP31 text",
     "Panama and island states back the demand; African group seeks adaptation cash.", "BBC · UN News", 2.4, 48.9, 5),
    (16, "OCEANIA", "SYDNEY", "Cricket Australia backs Pat Cummins as captain",
     "The board votes unanimously after the latest sandpaper-saga developments.", "ABC · RNZ", 151.2, -33.9, 5),
    (17, "ASIA", "TOKYO", "Nikkei plunges 5.1% on AI valuation fears",
     "The index closes at 56,436.65, its lowest since April, tracking Wall Street's sell-off.", "Xinhua", 139.7, 35.7, 5),
    (18, "ASIA", "NEW DELHI", "Delhi wakes to 'poor' air, AQI 279",
     "AIIMS and other hotspots record very poor air as smog settles over the capital.", "Indian Express", 77.2, 28.6, 4),
    (19, "ASIA", "MUMBAI", "Youth Congress workers held over Meta office vandalism",
     "Protest over suspended accounts leads to detentions in Hyderabad and Mumbai.", "Indian Express", 72.9, 19.1, 4),
    (20, "ASIA", "SINGAPORE", "Princess Aiko ends Singapore visit",
     "The Japanese princess visits Merlion Park on the last day of a 60th-anniversary trip.", "Kyodo", 103.8, 1.4, 4),
    (21, "ASIA", "KUALA LUMPUR", "Malaysia plans to resettle 10,000 Rohingya in Türkiye",
     "Announcement follows renewed international focus on the Rohingya crisis.", "AP · Manila Times", 101.7, 3.1, 4),
    (22, "OCEANIA", "AUCKLAND", "New Zealand may miss its 2030 HIV elimination target",
     "Auckland University research says access to prevention must improve; local diagnoses have fallen.", "NZ Herald", 174.8, -36.9, 4),
    (23, "ASIA", "FUKUSHIMA", "More than 1,000 isolated by heavy snow",
     "Fallen trees block roads around Kitashiobara village, stranding residents and hotel guests.", "Kyodo", 140.5, 37.8, 4),
    (24, "MIDDLE EAST", "STRAIT OF HORMUZ", "LPG tanker attacked; one Indian seafarer missing",
     "The Tara Gas is hit for a second time off Musandam; 21 of its 25 crew are Indian.", "The Hindu", 56.5, 26.5, 4),
    (25, "MIDDLE EAST", "TEHRAN", "Trump warns Iran over alleged 'dirty bomb' plot",
     "'Iran wants a deal, but not one acceptable to me,' the US president tells reporters.", "Anadolu · Xinhua", 51.4, 35.7, 4),
    (26, "MIDDLE EAST", "TEHRAN", "Iran: US naval blockade must end for oil exports to resume",
     "Foreign Minister Araghchi says Tehran is pursuing every route on exports and negotiations.", "Anadolu", 51.5, 35.6, 4),
    (27, "MIDDLE EAST", "RIYADH", "Japan agrees to buy up to 8m barrels of Saudi crude",
     "Deal for the national reserve also gives Saudi Arabia temporary Japanese storage.", "Anadolu", 46.8, 25.1, 3),
    (28, "MIDDLE EAST", "GAZA", "Displaced families brace for another winter in tents",
     "Floods worsen conditions in coastal camps as aid groups warn of the months ahead.", "Guardian", 34.5, 31.5, 3),
    (29, "AFRICA", "LAGOS", "Nigeria's petrol imports jump 47% in October",
     "Imports reach 15 million litres a day even as local refining expands.", "Punch", 3.4, 6.5, 3),
    (30, "AFRICA", "JOHANNESBURG", "South Africa mourns former deputy president Mlambo-Ngcuka",
     "The country's first female deputy president has died, news outlets report.", "IOL · Citizen", 28.0, -26.2, 3),
    (31, "AFRICA", "ACCRA", "Ghana meets euro convergence criteria",
     "The central bank says launch depends on logistics, not the economic tests.", "3News", -0.2, 5.6, 3),
    (32, "AFRICA", "NAIROBI", "Four jailed over Baringo land-dispute killings",
     "A court convicts four people in the case of a father and son killed over land.", "Citizen Digital", 36.8, -1.3, 3),
    (33, "AMERICAS", "MEXICO CITY", "Cartel leaders among 21 indicted in US court",
     "A grand jury charges La Nueva Familia Michoacana bosses with drugs, guns and people-smuggling.", "AP", -99.1, 19.4, 3),
    (34, "AMERICAS", "TAPACHULA", "Migrant caravan of about 250 enters Mexico",
     "The group crossed from Guatemala despite warnings from President Trump.", "AFP", -92.3, 14.9, 3),
    (35, "AMERICAS", "RIO GRANDE DO SUL", "Storm kills three and damages 8,000 homes",
     "Severe weather batters the Brazilian state; dozens more are injured.", "AGP · local reports", -51.2, -30.0, 3),
]

METRICS = [
    ("13", "DAY OF COP31, NO DEAL"),
    ("3", "MISSILES DOWN OVER RIYADH"),
    ("6.7", "MAGNITUDE, PERU QUAKE"),
    ("−3.7%", "S&P 500, FRIDAY CLOSE"),
    ("$55.6K", "BITCOIN, TWO-YEAR LOW"),
    ("8 YRS", "BEPICOLOMBO TO MERCURY"),
]

TOPICS = ["COP31 12", "SAUDI 9", "PERU 7", "MARKETS 6", "UKRAINE 5", "IRAN 4", "SPACE 3"]

FONT_DIR = r"C:\Windows\Fonts"
def font(size, bold=False, italic=False):
    name = "arialbd.ttf" if bold else ("ariali.ttf" if italic else "arial.ttf")
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

F_KICK = font(13, True)
F_TINY = font(10)
F_MICRO = font(9)
F_BODY = font(12)
F_SMALL = font(11)
F_SMALLB = font(12, True)
F_CARD = font(19, True)
F_CARD2 = font(17, True)
F_LIST = font(10)
F_LISTB = font(11, True)
F_HEAD = font(54, True)
F_SUB = font(14, False, True)
F_MET = font(24, True)
F_LABEL = font(10, True)
F_MAPNUM = font(9, True)
F_MAPNUM2 = font(8, True)
F_BADGE = font(12, True)
F_TAG = font(10, True)
F_ISS = font(13, True)

def fit(d, s, f, width):
    """Longest prefix of s that fits width, measured in real pixels."""
    if d.textlength(s, font=f) <= width:
        return s
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if d.textlength(s[:mid], font=f) <= width:
            lo = mid
        else:
            hi = mid - 1
    return s[:max(0, lo - 1)].rstrip() + "…"

def text(d, xy, s, f, fill=INK, anchor=None):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def wrap(d, s, f, width):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def lines(d, xy, s, f, width, leading, fill=INK, max_lines=None):
    ls = wrap(d, s, f, width)
    if max_lines:
        ls = ls[:max_lines]
    y = xy[1]
    for line in ls:
        text(d, (xy[0], y), line, f, fill)
        y += leading
    return y

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def badge(d, x, y, num, region, size=17):
    col = RCOL[region]
    d.ellipse([x, y, x + size, y + size], fill=col, outline=PAPER, width=1)
    text(d, (x + size / 2, y + size / 2 + 0.5), str(num), F_MAPNUM, PAPER, "mm")

# ---------- illustrations ----------
def ill_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 233, 226))
    cx, cy, r = x + 58, y + 47, 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(74, 146, 168), outline=(35, 85, 100), width=2)
    for poly in [[(cx - 24, cy - 18), (cx - 8, cy - 24), (cx + 4, cy - 12), (cx - 6, cy - 2), (cx - 20, cy + 2)],
                 [(cx + 6, cy - 22), (cx + 26, cy - 16), (cx + 22, cy + 4), (cx + 8, cy + 10), (cx + 2, cy - 6)],
                 [(cx - 18, cy + 8), (cx - 2, cy + 6), (cx + 8, cy + 24), (cx - 10, cy + 28)]]:
        d.polygon(poly, fill=(116, 174, 124))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(255, 255, 255), width=1)
    # thermometer
    tx = x + 140
    d.rounded_rectangle([tx - 7, y + 18, tx + 7, y + 68], 7, fill=(250, 250, 246), outline=MUTED, width=2)
    d.ellipse([tx - 12, y + 61, tx + 12, y + 85], fill=RED)
    d.rectangle([tx - 3, y + 33, tx + 3, y + 72], fill=RED)
    for k in range(4):
        d.line([tx + 8, y + 28 + k * 10, tx + 14, y + 28 + k * 10], fill=MUTED, width=1)
    text(d, (tx + 16, y + 34), "+1.5°C", F_TAG, RED)
    # clock at 13:00
    ox, oy, orr = x + 216, y + 47, 21
    d.ellipse([ox - orr, oy - orr, ox + orr, oy + orr], fill=(252, 251, 245), outline=MUTED, width=2)
    for k in range(12):
        a = k * math.pi / 6
        d.line([ox + 17 * math.sin(a), oy - 17 * math.cos(a), ox + 20 * math.sin(a), oy - 20 * math.cos(a)], fill=MUTED)
    d.line([ox, oy, ox, oy - 14], fill=INK, width=2)
    d.line([ox, oy, ox + 10, oy + 4], fill=INK, width=2)
    text(d, (ox, oy + orr - 1), "DAY 13", F_MICRO, RED, "ma")
    # draft papers
    px = x + 274
    for k in (0, 1, 2):
        d.rectangle([px + k * 6, y + 20 + k * 4, px + 30 + k * 6, y + 70 + k * 4],
                    fill=(255, 255, 250), outline=MUTED, width=1)
    text(d, (px + 20, y + 62), "DRAFT 3", F_MICRO, INK, "ma")
    rrect(d, [x + 4, y + h - 18, x + 128, y + h - 3], 3, fill=RED)
    text(d, (x + 10, y + h - 16), "NO DEAL · OVERTIME", F_TAG, (255, 255, 255))

def ill_missiles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 35, 60))
    for k in range(26):
        sx = x + 7 + k * 12
        sy = y + 9 + (k * 17) % 40
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(172, 190, 214))
    # skyline
    heights = [22, 34, 26, 46, 30, 38, 24, 42, 28]
    bx = x + 12
    for k, hh in enumerate(heights):
        d.rectangle([bx + k * 34, y + h - hh, bx + k * 34 + 27, y + h], fill=(48, 60, 88))
        for wy in range(y + h - hh + 6, y + h - 4, 9):
            for wx in range(bx + k * 34 + 5, bx + k * 34 + 23, 8):
                d.rectangle([wx, wy, wx + 2, wy + 3], fill=(222, 186, 96))
    for k, off in enumerate((0, 16, 32)):
        pts = []
        for t in range(25):
            px = x + 28 + t * 8.6
            py = y + 64 - off - 38 * math.sin(t / 24 * math.pi) + t * 0.42
            pts.append((px, py))
        d.line(pts, fill=(240, 213, 138), width=2)
        ex, ey = pts[-1]
        d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(238, 154, 63))
        d.line([ex - 11, ey, ex + 11, ey], fill=(255, 222, 140), width=1)
        d.line([ex, ey - 11, ex, ey + 11], fill=(255, 222, 140), width=1)
    rrect(d, [x + 8, y + 7, x + 106, y + 26], 3, fill=(190, 44, 44))
    text(d, (x + 14, y + 10), "3 DOWNED", F_TAG, (255, 255, 255))
    text(d, (x + w - 8, y + 8), "RIYADH · 01:45 UTC", F_MICRO, (208, 218, 235), "ra")

def ill_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    d.polygon([(x, y + h), (x + 60, y + 34), (x + 112, y + h)], fill=(182, 166, 133))
    d.polygon([(x + 82, y + h), (x + 150, y + 44), (x + 220, y + h)], fill=(160, 145, 115))
    for k in range(3):
        hx = x + 185 + k * 38
        hy = y + h - 30
        d.rectangle([hx, hy - 16, hx + 24, hy], fill=(228, 216, 190), outline=LAND_EDGE)
        d.polygon([(hx - 3, hy - 16), (hx + 12, hy - 27), (hx + 27, hy - 16)], fill=(168, 86, 66))
    pts = []
    for k in range(70):
        px = x + 8 + k * 4.4
        base = y + 62
        if 18 < k < 26:
            base -= 10
        if 26 <= k < 46:
            base += ((-1) ** k) * (16 - abs(32 - k))
        pts.append((px, base))
    d.line(pts, fill=RED, width=2)
    rrect(d, [x + 8, y + 6, x + 74, y + 24], 3, fill=RED)
    text(d, (x + 14, y + 9), "M6.7", F_TAG, (255, 255, 255))
    text(d, (x + w - 8, y + 8), "00:09 UTC · 108 km", F_MICRO, MUTED, "ra")

MINI = ["fire", "AI", "chart", "planet", "deal", "robot", "bat", "boat"]
SMALL_TAGS = ["KYIV: WARNING", "AI DATA TAX", "WALL ST: ROUT", "MERCURY ORBIT",
              "UK–EU DEAL", "ROBOT RULES", "RAHUL 136", "MYANMAR RULING"]

def star(d, cx, cy, r, fill):
    d.line([cx - r, cy, cx + r, cy], fill=fill, width=1)
    d.line([cx, cy - r, cx, cy + r], fill=fill, width=1)
    d.line([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=fill, width=1)
    d.line([cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7], fill=fill, width=1)

def ill_wide(d, x, y, w, h, kind):
    """A full-width scene for the small cards, drawn like the three lead pictures."""
    def X(u): return x + u * w / 242.0
    def Y(v): return y + v * h / 54.0
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 212))
    if kind == "fire":
        d.rectangle([x, y, x + w, y + h], fill=(25, 35, 60))
        for k in range(20):
            d.point((X(6 + k * 12), Y(5 + (k * 11) % 26)), fill=(150, 172, 204))
        heights = [18, 27, 22, 34, 25, 30, 20, 29, 24]
        for k, hh in enumerate(heights):
            bx = X(96 + k * 16)
            d.rectangle([bx, Y(54 - hh), bx + X(13) - X(0), Y(54)], fill=(45, 58, 88))
            for wy in range(int(Y(54 - hh + 4)), int(Y(50)), 7):
                for wx in range(int(bx + 3), int(bx + 11), 6):
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=(224, 188, 96))
        for off in (0, 12):
            pts = [(X(80 + t * 7), Y(30 - off) - 20 * math.sin(t / 12 * math.pi) + t * 0.5)
                   for t in range(13)]
            d.line(pts, fill=(244, 211, 134), width=2)
            ex, ey = pts[-1]
            star(d, ex, ey, 7, (236, 150, 62))
        d.polygon([(X(206), Y(34)), (X(212), Y(22)), (X(218), Y(34))], fill=(214, 88, 46))
    elif kind == "AI":
        d.rectangle([x, y, x + w, y + h], fill=(22, 38, 62))
        for k in range(14):
            d.line([X(k * 18), y, X(k * 18), y + h], fill=(34, 54, 84))
        for k in range(10):
            d.line([x, Y(k * 5), x + w, Y(k * 5)], fill=(34, 54, 84))
        for k in range(3):
            bx = X(96 + k * 34)
            d.rectangle([bx, Y(9), bx + X(28) - X(0), Y(49)], fill=(48, 64, 96), outline=(120, 156, 196))
            for j in range(4):
                d.line([bx + 4, Y(14 + j * 8), bx + 22, Y(14 + j * 8)], fill=(122, 202, 232), width=1)
                d.ellipse([bx + 24, Y(14 + j * 8), bx + 26, Y(16 + j * 8)], fill=(214, 82, 62))
        rrect(d, [X(196), Y(16), X(234), Y(42)], 3, fill=(226, 232, 240))
        text(d, (X(215), Y(20)), "TAX %", F_MICRO, RED, "ma")
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(240, 232, 216))
        d.line([X(96), Y(46), X(236), Y(46)], fill=MUTED, width=1)
        for k in range(5):
            d.line([X(100 + k * 32), Y(8), X(100 + k * 32), Y(46)], fill=(214, 204, 184))
        pts = [(X(96 + k * 11), Y(12 + 1.9 * k + ((-1) ** k) * 3)) for k in range(13)]
        d.line(pts, fill=RED, width=3)
        d.polygon([pts[-1], (X(228), Y(40)), (X(216), Y(38))], fill=RED)
        text(d, (X(228), Y(48)), "−3.7%", F_MICRO, RED, "ra")
        for k in range(3):
            d.ellipse([X(204 + k * 12), Y(35), X(214 + k * 12), Y(45)], fill=(206, 158, 64), outline=(150, 112, 40))
    elif kind == "planet":
        d.rectangle([x, y, x + w, y + h], fill=(18, 28, 52))
        for k in range(18):
            a = k * math.pi / 9
            d.line([X(96), Y(27), X(96 + 26 * math.cos(a)), Y(27 + 26 * math.sin(a))], fill=(216, 176, 86), width=1)
        d.ellipse([X(180), Y(7), X(232), Y(51)], fill=(168, 142, 106), outline=(120, 100, 72), width=1)
        d.ellipse([X(192), Y(16), X(200), Y(22)], fill=(142, 118, 88))
        d.ellipse([X(210), Y(30), X(220), Y(38)], fill=(142, 118, 88))
        d.rectangle([X(112), Y(22), X(134), Y(32)], fill=(198, 204, 214), outline=(120, 132, 150))
        d.rectangle([X(100), Y(18), X(112), Y(36)], fill=(72, 108, 162))
        d.rectangle([X(134), Y(18), X(146), Y(36)], fill=(72, 108, 162))
        d.polygon([(X(112), Y(32)), (X(122), Y(32)), (X(117), Y(44))], fill=(238, 156, 64))
    elif kind == "deal":
        d.rectangle([x, y, x + X(121), y + h], fill=(38, 66, 132))
        d.rectangle([x + X(121), y, x + w, y + h], fill=(30, 78, 152))
        for k in range(7):
            d.line([X(104 + k * 17), Y(4), X(104 + k * 17), Y(50)], fill=(224, 210, 90), width=2)
        for k in range(4):
            d.ellipse([X(112 + k * 28), Y(10), X(118 + k * 28), Y(16)], fill=(232, 214, 96))
        d.polygon([(X(150), Y(24)), (X(164), Y(16)), (X(178), Y(24)), (X(164), Y(32))], fill=(222, 188, 140))
        d.polygon([(X(164), Y(32)), (X(178), Y(24)), (X(192), Y(32)), (X(178), Y(40))], fill=(198, 152, 106))
    elif kind == "robot":
        d.rectangle([x, y, x + w, y + h], fill=(220, 229, 234))
        # UN building with flags
        d.rectangle([X(96), Y(12), X(148), Y(52)], fill=(142, 170, 190), outline=(72, 104, 126))
        for k in range(5):
            d.line([X(100 + k * 10), Y(12), X(100 + k * 10), Y(52)], fill=(88, 120, 144))
        for k in range(3):
            d.line([X(102 + k * 16), Y(12), X(102 + k * 16), Y(4)], fill=MUTED)
            d.rectangle([X(102 + k * 16), Y(4), X(114 + k * 16), Y(9)], fill=(64, 122, 190))
        # two humanoid robots
        for cx in (170, 206):
            rrect(d, [X(cx - 9), Y(14), X(cx + 9), Y(26)], 3, fill=(92, 102, 124))
            d.ellipse([X(cx - 5), Y(17), X(cx - 2), Y(20)], fill=(180, 226, 240))
            d.ellipse([X(cx + 2), Y(17), X(cx + 5), Y(20)], fill=(180, 226, 240))
            d.rectangle([X(cx - 8), Y(27), X(cx + 8), Y(43)], fill=(104, 116, 138))
            text(d, (X(cx), Y(30)), "AI", F_MICRO, (220, 238, 246), "ma")
            d.line([X(cx - 8), Y(30), X(cx - 14), Y(38)], fill=(104, 116, 138), width=3)
            d.line([X(cx + 8), Y(30), X(cx + 14), Y(38)], fill=(104, 116, 138), width=3)
            d.line([X(cx - 4), Y(43), X(cx - 4), Y(51)], fill=(104, 116, 138), width=3)
            d.line([X(cx + 4), Y(43), X(cx + 4), Y(51)], fill=(104, 116, 138), width=3)
        rrect(d, [X(96), Y(42), X(152), Y(52)], 2, fill=(246, 246, 238))
        text(d, (X(124), Y(44)), "CCW 2026", F_MICRO, INK, "ma")
    elif kind == "bat":
        d.rectangle([x, y, x + w, y + h], fill=(206, 226, 198))
        d.rectangle([X(96), Y(38), X(236), Y(54)], fill=(96, 152, 92))
        d.line([X(96), Y(38), X(236), Y(38)], fill=(72, 124, 72), width=2)
        for sx in (166, 186, 206):
            d.line([X(sx), Y(44), X(sx), Y(18)], fill=(224, 222, 208), width=3)
            d.line([X(sx - 4), Y(18), X(sx + 4), Y(18)], fill=(224, 222, 208), width=2)
        d.line([X(132), Y(44), X(160), Y(18)], fill=(156, 118, 78), width=5)
        d.ellipse([X(158), Y(14), X(168), Y(24)], fill=RED)
        rrect(d, [X(102), Y(4), X(152), Y(18)], 2, fill=(250, 250, 244))
        text(d, (X(127), Y(6)), "239/1", F_MICRO, INK, "ma")
    else:
        d.rectangle([x, y, x + w, y + h], fill=(233, 227, 210))
        # scales of justice: post, beam and two hanging pans
        d.rectangle([X(130), Y(24), X(136), Y(52)], fill=(112, 86, 58))
        d.polygon([(X(126), Y(52)), (X(140), Y(52)), (X(133), Y(46))], fill=(112, 86, 58))
        d.line([X(92), Y(16), X(174), Y(16)], fill=(112, 86, 58), width=3)
        d.ellipse([X(130), Y(12), X(136), Y(20)], fill=(200, 164, 66), outline=(112, 86, 58))
        for px in (94, 172):
            d.line([X(px), Y(17), X(px), Y(30)], fill=(120, 94, 60), width=1)
            d.line([X(px - 13), Y(30), X(px + 13), Y(30)], fill=(120, 94, 60), width=2)
            d.line([X(px - 13), Y(30), X(px - 9), Y(40)], fill=(120, 94, 60), width=1)
            d.line([X(px + 13), Y(30), X(px + 9), Y(40)], fill=(120, 94, 60), width=1)
            d.line([X(px - 9), Y(40), X(px + 9), Y(40)], fill=(120, 94, 60), width=2)
        # gavel and ICJ plaque
        d.line([X(194), Y(44), X(216), Y(24)], fill=(126, 96, 64), width=4)
        d.rectangle([X(212), Y(12), X(232), Y(22)], fill=(106, 78, 52))
        rrect(d, [X(188), Y(4), X(236), Y(16)], 2, fill=(250, 250, 244))
        text(d, (X(212), Y(6)), "ICJ", F_MICRO, RED, "ma")
def ill_bold(d, x, y, w, h, kind):
    """High-contrast, large-shape illustrations that survive a 300 px preview."""
    def X(u): return x + u * w / 242.0
    def Y(v): return y + v * h / 66.0
    if kind == "fire":
        d.rectangle([x, y, x + w, y + h], fill=(22, 34, 62))
        for k, hh in enumerate((24, 36, 28, 44, 30, 40, 26)):
            bx = X(94 + k * 21)
            d.rectangle([bx, Y(66 - hh), bx + X(18) - X(0), Y(66)], fill=(44, 60, 94))
            for j in range(2):
                d.rectangle([bx + 5 + j * 8, Y(66 - hh + 8), bx + 10 + j * 8, Y(66 - hh + 15)],
                            fill=(246, 204, 92))
        for off in (0, 14):
            pts = [(X(82 + t * 9), Y(34 - off) - 22 * math.sin(t / 12 * math.pi) + t * 0.6)
                   for t in range(13)]
            d.line(pts, fill=(255, 214, 112), width=4)
            star(d, pts[-1][0], pts[-1][1], 11, (244, 138, 50))
        d.polygon([(X(210), Y(48)), (X(218), Y(26)), (X(226), Y(48))], fill=(232, 76, 44))
        d.rectangle([X(96), Y(52), X(120), Y(64)], fill=(60, 112, 186))
        d.rectangle([X(96), Y(58), X(120), Y(64)], fill=(248, 212, 72))
    elif kind == "AI":
        d.rectangle([x, y, x + w, y + h], fill=(18, 34, 60))
        for k in range(2):
            bx = X(96 + k * 56)
            d.rectangle([bx, Y(6), bx + X(46) - X(0), Y(60)], fill=(46, 66, 104), outline=(128, 178, 220), width=2)
            for j in range(3):
                d.line([bx + 6, Y(15 + j * 14), bx + 38, Y(15 + j * 14)], fill=(124, 214, 244), width=3)
                d.ellipse([bx + 38, Y(12 + j * 14), bx + 43, Y(17 + j * 14)], fill=(238, 84, 62))
        rrect(d, [X(200), Y(16), X(238), Y(46)], 4, fill=(248, 250, 252))
        text(d, (X(219), Y(22)), "TAX%", font(12, True), RED, "ma")
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(244, 236, 218))
        d.line([X(94), Y(56), X(238), Y(56)], fill=(110, 100, 86), width=2)
        pts = [(X(96 + k * 12), Y(12 + 2.4 * k + ((-1) ** k) * 4)) for k in range(12)]
        d.line(pts, fill=RED, width=5)
        d.polygon([pts[-1], (X(238), Y(50)), (X(220), Y(48))], fill=RED)
        text(d, (X(236), Y(6)), "−3.7%", font(12, True), RED, "ra")
        for k in range(3):
            cx = X(202 + k * 15)
            d.ellipse([cx - 9, Y(48), cx + 9, Y(64)], fill=(224, 176, 68), outline=(132, 96, 36), width=2)
    elif kind == "planet":
        d.rectangle([x, y, x + w, y + h], fill=(16, 26, 50))
        for k in range(8):
            a = k * math.pi / 4
            d.line([X(100), Y(33), X(100 + 30 * math.cos(a)), Y(33 + 30 * math.sin(a))],
                   fill=(250, 196, 84), width=3)
        d.ellipse([X(172), Y(6), X(236), Y(64)], fill=(178, 150, 110), outline=(110, 90, 64), width=2)
        d.ellipse([X(188), Y(18), X(200), Y(29)], fill=(140, 116, 84))
        d.ellipse([X(212), Y(40), X(226), Y(52)], fill=(140, 116, 84))
        d.rectangle([X(108), Y(25), X(140), Y(39)], fill=(214, 220, 230), outline=(92, 106, 130), width=2)
        d.rectangle([X(94), Y(18), X(108), Y(46)], fill=(64, 122, 194))
        d.rectangle([X(140), Y(18), X(154), Y(46)], fill=(64, 122, 194))
        d.polygon([(X(108), Y(39)), (X(140), Y(39)), (X(124), Y(60))], fill=(248, 154, 52))
    elif kind == "deal":
        d.rectangle([x, y, x + X(121), y + h], fill=(36, 62, 130))
        d.rectangle([x + X(121), y, x + w, y + h], fill=(26, 76, 154))
        for k in range(5):
            d.line([X(96 + k * 27), Y(4), X(96 + k * 27), Y(62)], fill=(250, 216, 84), width=4)
        for k in range(4):
            d.ellipse([X(100 + k * 30), Y(9), X(112 + k * 30), Y(21)], fill=(250, 220, 96))
        d.polygon([(X(146), Y(28)), (X(162), Y(18)), (X(180), Y(28)), (X(162), Y(40))], fill=(234, 188, 138))
        d.polygon([(X(162), Y(40)), (X(180), Y(28)), (X(198), Y(40)), (X(180), Y(54))], fill=(192, 136, 92))
    elif kind == "robot":
        d.rectangle([x, y, x + w, y + h], fill=(216, 228, 236))
        d.rectangle([X(94), Y(12), X(150), Y(62)], fill=(140, 170, 192), outline=(60, 96, 122), width=2)
        for k in range(4):
            d.line([X(100 + k * 14), Y(12), X(100 + k * 14), Y(62)], fill=(70, 104, 130), width=2)
        for cx in (172, 212):
            rrect(d, [X(cx - 12), Y(12), X(cx + 12), Y(30)], 4, fill=(74, 86, 112))
            d.ellipse([X(cx - 8), Y(17), X(cx - 3), Y(22)], fill=(160, 232, 248))
            d.ellipse([X(cx + 3), Y(17), X(cx + 8), Y(22)], fill=(160, 232, 248))
            d.rectangle([X(cx - 11), Y(32), X(cx + 11), Y(52)], fill=(96, 110, 138))
            text(d, (X(cx), Y(36)), "AI", font(10, True), (236, 246, 250), "ma")
            d.line([X(cx - 11), Y(36), X(cx - 18), Y(46)], fill=(96, 110, 138), width=4)
            d.line([X(cx + 11), Y(36), X(cx + 18), Y(46)], fill=(96, 110, 138), width=4)
        rrect(d, [X(94), Y(50), X(150), Y(64)], 2, fill=(250, 250, 244))
        text(d, (X(122), Y(53)), "CCW 2026", font(10, True), INK, "ma")
    elif kind == "bat":
        d.rectangle([x, y, x + w, y + h], fill=(202, 228, 194))
        d.rectangle([X(94), Y(46), X(238), Y(66)], fill=(82, 146, 82))
        for sx in (168, 190, 212):
            d.line([X(sx), Y(54), X(sx), Y(20)], fill=(250, 248, 238), width=5)
            d.line([X(sx - 6), Y(20), X(sx + 6), Y(20)], fill=(250, 248, 238), width=3)
        d.line([X(132), Y(52), X(160), Y(20)], fill=(146, 104, 66), width=8)
        d.ellipse([X(156), Y(12), X(172), Y(28)], fill=RED)
        rrect(d, [X(98), Y(4), X(154), Y(22)], 3, fill=(252, 252, 246))
        text(d, (X(126), Y(7)), "239/1", font(11, True), INK, "ma")
    else:
        d.rectangle([x, y, x + w, y + h], fill=(234, 226, 206))
        d.rectangle([X(128), Y(30), X(136), Y(66)], fill=(96, 72, 48))
        d.line([X(88), Y(18), X(176), Y(18)], fill=(96, 72, 48), width=5)
        d.ellipse([X(128), Y(12), X(136), Y(24)], fill=(226, 180, 64), outline=(96, 72, 48), width=2)
        for px in (92, 172):
            d.line([X(px), Y(19), X(px), Y(38)], fill=(96, 72, 48), width=3)
            d.line([X(px - 17), Y(38), X(px + 17), Y(38)], fill=(96, 72, 48), width=4)
            d.line([X(px - 17), Y(38), X(px - 11), Y(52)], fill=(96, 72, 48), width=2)
            d.line([X(px + 17), Y(38), X(px + 11), Y(52)], fill=(96, 72, 48), width=2)
            d.line([X(px - 11), Y(52), X(px + 11), Y(52)], fill=(96, 72, 48), width=4)
        d.line([X(194), Y(56), X(220), Y(32)], fill=(110, 78, 50), width=6)
        d.rectangle([X(214), Y(16), X(238), Y(30)], fill=(96, 66, 44))
        rrect(d, [X(188), Y(4), X(238), Y(20)], 3, fill=(252, 252, 246))
        text(d, (X(213), Y(7)), "ICJ", font(11, True), RED, "ma")

def ill_mini(d, x, y, w, h, kind, col):
    """A larger, detailed drawing scaled to the card's illustration band."""
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 214))
    d.line([x, y + h - 1, x + w, y + h - 1], fill=(203, 194, 173), width=1)
    k = h / 22.0
    cx = x + w * 0.5
    def P(dx, dy):
        return (cx + dx * k, y + dy * k)
    if kind == "fire":
        d.rectangle([P(-9, 6), P(9, 22)], fill=(104, 114, 128))
        d.rectangle([P(-6, 10), P(-2, 14)], fill=(226, 194, 110))
        d.rectangle([P(3, 10), P(7, 14)], fill=(226, 194, 110))
        d.polygon([P(-6, 6), P(-1, -3), P(3, 4), P(7, -1), P(8, 7)], fill=(208, 88, 48))
        d.polygon([P(-3, 6), P(0, 1), P(3, 6)], fill=(246, 188, 82))
    elif kind == "AI":
        d.rectangle([P(-10, 1), P(10, 21)], fill=(52, 64, 90))
        d.rectangle([P(-7, 4), P(7, 14)], fill=(24, 36, 58))
        for j in range(3):
            d.line([P(-5, 6 + j * 3), P(5, 6 + j * 3)], fill=(146, 206, 232), width=1)
        d.line([P(-4, 17), P(4, 17)], fill=(146, 206, 232), width=1)
        d.ellipse([P(-2, 15), P(2, 19)], fill=(208, 88, 48))
    elif kind == "chart":
        d.line([P(-10, 19), P(10, 19)], fill=MUTED, width=1)
        d.line([P(-9, 4), P(-3, 11), P(2, 7), P(10, 18)], fill=RED, width=2)
        d.polygon([P(10, 18), P(5, 17), P(9, 12)], fill=RED)
    elif kind == "planet":
        d.ellipse([P(-8, 3), P(8, 19)], fill=(170, 143, 105))
        d.ellipse([P(-13, 8), P(13, 14)], outline=(124, 103, 74), width=2)
        d.ellipse([P(-3, 7), P(2, 12)], fill=(190, 166, 128))
    elif kind == "deal":
        d.polygon([P(-11, 12), P(-3, 5), P(2, 12), P(11, 7)], fill=(194, 148, 104))
        d.polygon([P(-11, 12), P(-3, 18), P(2, 12)], fill=(170, 126, 86))
        d.ellipse([P(-11, 11), P(-7, 15)], fill=(222, 190, 150))
        d.ellipse([P(7, 6), P(11, 10)], fill=(222, 190, 150))
    elif kind == "robot":
        d.rectangle([P(-8, 4), P(8, 17)], fill=(96, 104, 122))
        d.ellipse([P(-3, 7), P(3, 13)], fill=(198, 218, 232))
        d.line([P(0, 17), P(6, 21), P(11, 12)], fill=(96, 104, 122), width=3)
        d.ellipse([P(9, 10), P(13, 14)], fill=RED)
    elif kind == "bat":
        d.line([P(-10, 20), P(9, 3)], fill=(150, 118, 78), width=4)
        d.ellipse([P(-13, 18), P(-7, 22)], fill=(150, 118, 78))
        d.ellipse([P(6, 1), P(12, 7)], fill=RED)
    else:
        d.polygon([P(-12, 12), P(12, 12), P(6, 21), P(-7, 21)], fill=(82, 126, 154))
        d.polygon([P(-12, 12), P(-6, 6), P(9, 6), P(12, 12)], fill=(108, 156, 184))
        d.line([P(0, 12), P(3, 1)], fill=MUTED, width=2)

def draw_map(d, sx, sy, mw, mh):
    """Peta PROMPT_PETA.md: GeoJSON nyata, equirectangular, titik + panah
    + badge bernomor terpusat, legenda & caption di dalam panel."""
    d.rectangle([sx, sy, sx + mw, sy + mh], fill=OCEAN, outline=(156, 179, 194), width=1)
    geo = json.load(open(os.path.join(os.path.dirname(__file__), "world110.geojson"), encoding="utf-8"))
    LAT_T, LAT_B = 83, -58
    def proj(lon, lat):
        return (sx + (lon + 180) / 360.0 * mw,
                sy + (LAT_T - lat) / (LAT_T - LAT_B) * mh)
    # graticule tiap 30 derajat
    for lon in range(-180, 181, 30):
        d.line([proj(lon, LAT_T), proj(lon, LAT_B)], fill=GRAT, width=1)
    for lat in range(-60, 84, 30):
        d.line([proj(-180, lat), proj(180, lat)], fill=GRAT, width=1)
    # benua dari GeoJSON Natural Earth; Antarctica dilewati
    for feat in geo["features"]:
        if feat["properties"].get("NAME") == "Antarctica":
            continue
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = poly[0]
            pts = [proj(p[0], p[1]) for p in ring if LAT_B <= p[1] <= LAT_T]
            if len(pts) > 2:
                d.polygon(pts, fill=LAND)
                d.line(pts + [pts[0]], fill=LAND_EDGE, width=1)
    rad = 6.5
    # garis + panah dulu (di bawah badge), lalu titik, lalu badge
    for s in STORIES:
        n, reg = s[0], s[1]
        if n not in POS:
            continue
        dx, dy = proj(s[6], s[7])
        cx, cy, ring = POS[n][1], POS[n][2], POS[n][3]
        if ring <= 3:
            continue
        vx, vy = cx - dx, cy - dy
        L = math.hypot(vx, vy) or 1
        ux, uy = vx / L, vy / L
        ex, ey = cx - ux * (rad + 1), cy - uy * (rad + 1)
        d.line([(dx, dy), (ex, ey)], fill=(76, 90, 102), width=1)
        ax, ay = -uy, ux
        p1 = (ex, ey)
        p2 = (ex - ux * 5 + ax * 2.4, ey - uy * 5 + ay * 2.4)
        p3 = (ex - ux * 5 - ax * 2.4, ey - uy * 5 - ay * 2.4)
        d.polygon([p1, p2, p3], fill=(76, 90, 102))
    for s in STORIES:
        n = s[0]
        if n not in POS:
            continue
        dx, dy = proj(s[6], s[7])
        col = RCOL[s[1]]
        d.ellipse([dx - 2.4, dy - 2.4, dx + 2.4, dy + 2.4], fill=col,
                  outline=(255, 255, 255), width=1)
    for s in STORIES:
        n = s[0]
        if n not in POS:
            continue
        cx, cy = POS[n][1], POS[n][2]
        col = RCOL[s[1]]
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col,
                  outline=(255, 255, 255), width=2)
        text(d, (cx, cy), str(n), F_MAPNUM2, (255, 255, 255), "mm")

def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # compact masthead
    text(d, (14, 8), "THE WORLD IN ONE DAY", F_KICK, RED)
    text(d, (W - 14, 9), "35 STORIES · 7 REGIONS · EVERY STORY DATED SATURDAY 21 NOVEMBER 2026",
         F_TINY, MUTED, "ra")
    text(d, (W / 2, 44), "Saturday 21 November 2026", F_HEAD, INK, "mm")
    text(d, (W / 2, 80), "COP31 overtime  ·  three missiles down over Riyadh  ·  M6.7 Peru quake  ·  Bitcoin below $56k",
         F_SUB, RED, "mm")
    d.line([14, 94, W - 14, 94], fill=INK, width=2)

    # six big numbers, tighter
    cw = (W - 28) / 6
    for k, (val, lab) in enumerate(METRICS):
        x = 14 + k * cw
        if k:
            d.line([x, 98, x, 131], fill=HAIR, width=1)
        text(d, (x + 8, 97), val, F_MET, RED)
        text(d, (x + 8, 123), lab, F_LABEL, MUTED)
    d.line([14, 136, W - 14, 136], fill=INK, width=1)

    # most-reported topics, ordered by number of reports
    text(d, (14, 140), "MOST-REPORTED TOPICS →", F_LABEL, INK)
    tx = 168
    for k, t in enumerate(TOPICS):
        col = REGIONS[k % 7][1]
        tw = d.textlength(t, font=F_TAG) + 14
        rrect(d, [tx, 138, tx + tw, 154], 3, fill=col)
        text(d, (tx + 7, 139), t, F_TAG, (255, 255, 255))
        tx += tw + 5
    d.line([14, 158, W - 14, 158], fill=HAIR, width=1)

    # region legend
    counts = {}
    for s in STORIES:
        counts[s[1]] = counts.get(s[1], 0) + 1
    lx = 14
    for name, col in REGIONS:
        lab = "%s %d" % (name, counts.get(name, 0))
        lw = d.textlength(lab, font=F_LABEL) + 12
        d.rectangle([lx, 161, lx + lw, 177], fill=col)
        text(d, (lx + 6, 163), lab, F_LABEL, (255, 255, 255))
        lx += lw + 4
    d.line([14, 182, W - 14, 182], fill=INK, width=2)

    # three main cards
    ills = [ill_globe, ill_missiles, ill_quake]
    for i in range(3):
        s = STORIES[i]
        x = 14 + i * 338
        y = 188
        w, h = 322, 186
        d.rectangle([x, y, x + w, y + h], fill=(255, 254, 249), outline=HAIR, width=1)
        ills[i](d, x + 1, y + 1, w - 2, 78)
        d.rectangle([x + 1, y + 79, x + w - 1, y + 98], fill=RCOL[s[1]])
        text(d, (x + 7, y + 82), str(s[0]), F_BADGE, (255, 255, 255))
        place = fit(d, s[2] + "  ·  " + s[1], F_SMALL, w - 108)
        text(d, (x + 28, y + 83), place, F_SMALL, (255, 255, 255))
        text(d, (x + w - 6, y + 84), s[5], F_MICRO, (255, 255, 255), "ra")
        yy = lines(d, (x + 8, y + 103), s[3], F_CARD, w - 16, 20, INK, 2)
        lines(d, (x + 8, yy + 4), s[4], F_BODY, w - 16, 13, INK, 3)

    # eight small cards, styled like the leading entries: large illustration with a
    # bold red label, a numbered topic line, a big headline and a short body.
    for i in range(8):
        s = STORIES[3 + i]
        row, col = divmod(i, 4)
        x = 14 + col * 250
        y = 384 + row * 175
        w, h = 244, 169
        d.rectangle([x, y, x + w, y + h], fill=(255, 254, 249), outline=HAIR, width=1)
        d.rectangle([x + 1, y + 1, x + w - 1, y + 66], fill=(234, 230, 214))
        ill_bold(d, x + 1, y + 1, w - 2, 65, MINI[i])
        tag = SMALL_TAGS[i]
        tw = d.textlength(tag, font=F_ISS) + 14
        rrect(d, [x + 5, y + 4, x + 5 + tw, y + 24], 2, fill=RED)
        text(d, (x + 11, y + 6), tag, F_ISS, (255, 255, 255))
        # numbered topic line
        badge(d, x + 7, y + 69, s[0], s[1], 20)
        topic = s[2].split(",")[0].title() + "  ·  " + s[1].title()
        text(d, (x + 32, y + 71), fit(d, topic, F_TAG, w - 126), F_TAG, RCOL[s[1]])
        text(d, (x + w - 6, y + 72), s[5].split(" · ")[0], F_MICRO, MUTED, "ra")
        d.line([x + 6, y + 92, x + w - 6, y + 92], fill=(214, 204, 184), width=1)
        lines(d, (x + 8, y + 96), s[3], F_CARD2, w - 16, 20, INK, 2)
        lines(d, (x + 8, y + 138), s[4], F_TINY, w - 16, 14, MUTED, 2)

    # bottom: map left, story list right
    d.line([14, 732, W - 14, 732], fill=INK, width=2)
    rrect(d, [14, 738, 400, 956], 3, fill=(255, 254, 249), outline=(156, 179, 194))
    text(d, (20, 740), "WHERE IT HAPPENED", F_LABEL, INK)
    draw_map(d, 20, 754, 374, 150)
    # legenda 7 region (warna + jumlah berita) di dalam panel peta — 2 baris
    counts = {}
    for s in STORIES:
        counts[s[1]] = counts.get(s[1], 0) + 1
    FL = font(8)
    for row, names in enumerate((REGIONS[:4], REGIONS[4:])):
        lx, ly = 20, 908 + row * 11
        for name, col in names:
            lab = "%s %d" % (name, counts.get(name, 0))
            lw = d.textlength(lab, font=FL)
            d.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=col)
            text(d, (lx + 11, ly), lab, FL, INK)
            lx += 11 + lw + 8
    # caption dua baris agar tidak terpotong di tepi panel
    text(d, (20, 933),
         "Each number is the story with that number on this page. Dots mark the exact place;", font(8), MUTED)
    text(d, (20, 943),
         "arrows join each dot to its number.", font(8), MUTED)

    text(d, (408, 740), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES", F_LABEL, INK)
    for idx, s in enumerate(STORIES[12:]):
        col, row = divmod(idx, 12)
        x = 408 + col * 300
        y = 758 + row * 16
        d.rectangle([x, y + 1, x + 13, y + 13], fill=RCOL[s[1]])
        text(d, (x + 6.5, y + 7), str(s[0]), F_MICRO, (255, 255, 255), "mm")
        label = s[3]
        if d.textlength(s[2].title() + " — " + label, font=F_LIST) <= 279:
            label = s[2].title() + " — " + label
        text(d, (x + 17, y + 1), fit(d, label, F_LIST, 279), F_LIST, INK)

    # slim date-check and source lines, pushed down close to the bottom edge
    rrect(d, [14, 960, W - 14, 988], 3, fill=(252, 246, 230), outline=RED, width=1)
    text(d, (21, 964), "DATE CHECK:", F_LISTB, RED)
    text(d, (108, 965),
         "Every story above happened or was first reported on Saturday 21 November 2026 (any time zone). "
         "Nothing from 19–20 November counted; claims attributed to source.",
         F_SMALL, INK)
    text(d, (14, 993),
         "Sources: Reuters · AP · AFP · BBC · Al Jazeera · ESA · USGS · Kyodo · Anadolu · Guardian · Punch · ABC · RNZ. "
         "Map: Natural Earth 110m; illustrations and layout drawn in code.",
         F_MICRO, MUTED)

    out = os.path.join(os.path.dirname(__file__), "entry.png")
    im.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    build()

"""Render the 21 November 2026 world-news front page for entry 3.

Every pixel is painted with Pillow. The only non-code input is the Natural
Earth coastline file; the map panel was rebuilt for this entry to follow the
map brief, while the 35 dated stories and the card layout come from entry 2.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
BG = (247, 242, 229)          # warm newsprint
INK = (26, 25, 23)
ACCENT = (166, 36, 39)        # masthead red
SUBTLE = (92, 84, 72)
HAIRLINE = (120, 110, 94)
SEA = (216, 232, 241)         # #D8E8F1
GROUND = (234, 220, 185)      # #EADCB9
COAST = (184, 161, 117)       # #B8A175
GRID = (198, 222, 234)        # #C6DEEA

# Region palette from the map brief. The same swatches colour the top band,
# the card labels, the index dots and the map badges.
REGION_COLORS = [
    ("EUROPE", (44, 111, 176)),
    ("MIDDLE EAST", (210, 105, 30)),
    ("AFRICA", (47, 139, 91)),
    ("ASIA", (180, 58, 46)),
    ("AMERICAS", (119, 72, 168)),
    ("OCEANIA", (17, 138, 142)),
    ("WORLD", (90, 100, 114)),
]
COLOR_OF = dict(REGION_COLORS)

# Optimised once and frozen here so the renderer and the auditor agree.
# Tuple = (story number, badge x, badge y, ring distance from the dot).
BADGE_SPOTS = [
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
SPOT = {row[0]: row for row in BADGE_SPOTS}

# number, region, place, headline, detail, source, longitude, latitude, heat
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

HEADLINE_FACTS = [
    ("13", "DAY OF COP31, NO DEAL"),
    ("3", "MISSILES DOWN OVER RIYADH"),
    ("6.7", "MAGNITUDE, PERU QUAKE"),
    ("−3.7%", "S&P 500, FRIDAY CLOSE"),
    ("$55.6K", "BITCOIN, TWO-YEAR LOW"),
    ("8 YRS", "BEPICOLOMBO TO MERCURY"),
]
TRENDING = ["COP31 12", "SAUDI 9", "PERU 7", "MARKETS 6", "UKRAINE 5", "IRAN 4", "SPACE 3"]
SMALL_KINDS = ["fire", "AI", "chart", "planet", "deal", "robot", "bat", "gavel"]
SMALL_LABELS = ["KYIV: WARNING", "AI DATA TAX", "WALL ST: ROUT", "MERCURY ORBIT",
                "UK–EU DEAL", "ROBOT RULES", "RAHUL 136", "MYANMAR RULING"]

FONT_DIR = r"C:\Windows\Fonts"
_FONT_CACHE = {}
def face(px, heavy=False, italic=False):
    key = (px, heavy, italic)
    if key not in _FONT_CACHE:
        name = "arialbd.ttf" if heavy else ("ariali.ttf" if italic else "arial.ttf")
        _FONT_CACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), px)
    return _FONT_CACHE[key]

F_KICKER = face(13, True)
F_TINY = face(10)
F_MICRO = face(9)
F_BODY = face(12)
F_SMALL = face(11)
F_CARD = face(19, True)
F_CARD_SMALL = face(17, True)
F_LIST = face(10)
F_HEAD = face(54, True)
F_DECK = face(14, False, True)
F_METRIC = face(24, True)
F_LABEL = face(10, True)
F_BADGE_NUM = face(8, True)
F_CARD_NUM = face(12, True)
F_CHIP = face(10, True)
F_TAG = face(13, True)
F_MAP_NUM = face(9, True)

def write(d, xy, text, font, fill=INK, anchor=None):
    d.text(xy, text, font=font, fill=fill, anchor=anchor)

def shrink(d, text, font, width):
    if d.textlength(text, font=font) <= width:
        return text
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if d.textlength(text[:mid], font=font) <= width:
            lo = mid
        else:
            hi = mid - 1
    return text[:max(0, lo - 1)].rstrip() + "…"

def split_lines(d, text, font, width):
    out, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if d.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out

def write_block(d, xy, text, font, width, leading, fill=INK, limit=None):
    rows = split_lines(d, text, font, width)
    if limit:
        rows = rows[:limit]
    x, y = xy
    for row in rows:
        write(d, (x, y), row, font, fill)
        y += leading
    return y

def round_box(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def numbered_dot(d, x, y, number, region, diameter=20):
    col = COLOR_OF[region]
    d.ellipse([x, y, x + diameter, y + diameter], fill=col, outline=BG, width=1)
    write(d, (x + diameter / 2, y + diameter / 2 + 0.5), str(number), F_MAP_NUM, BG, "mm")

def sparkle(d, cx, cy, radius, fill):
    d.line([cx - radius, cy, cx + radius, cy], fill=fill)
    d.line([cx, cy - radius, cx, cy + radius], fill=fill)
    d.line([cx - radius * .7, cy - radius * .7, cx + radius * .7, cy + radius * .7], fill=fill)
    d.line([cx - radius * .7, cy + radius * .7, cx + radius * .7, cy - radius * .7], fill=fill)


# ---------------------------------------------------------------- lead art
def art_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 233, 226))
    cx, cy, r = x + 58, y + 47, 32
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(74, 146, 168), outline=(35, 85, 100), width=2)
    for poly in [
        [(cx-24, cy-18), (cx-8, cy-24), (cx+4, cy-12), (cx-6, cy-2), (cx-20, cy+2)],
        [(cx+6, cy-22), (cx+26, cy-16), (cx+22, cy+4), (cx+8, cy+10), (cx+2, cy-6)],
        [(cx-18, cy+8), (cx-2, cy+6), (cx+8, cy+24), (cx-10, cy+28)],
    ]:
        d.polygon(poly, fill=(116, 174, 124))
    d.arc([cx-r, cy-r, cx+r, cy+r], 200, 340, fill=(255, 255, 255), width=1)
    tx = x + 140
    d.rounded_rectangle([tx-7, y+18, tx+7, y+68], 7, fill=(250, 250, 246), outline=SUBTLE, width=2)
    d.ellipse([tx-12, y+61, tx+12, y+85], fill=ACCENT)
    d.rectangle([tx-3, y+33, tx+3, y+72], fill=ACCENT)
    for k in range(4):
        d.line([tx+8, y+28+k*10, tx+14, y+28+k*10], fill=SUBTLE)
    write(d, (tx+16, y+34), "+1.5°C", F_CHIP, ACCENT)
    ox, oy, orr = x + 216, y + 47, 21
    d.ellipse([ox-orr, oy-orr, ox+orr, oy+orr], fill=(252, 251, 245), outline=SUBTLE, width=2)
    for k in range(12):
        a = k * math.pi / 6
        d.line([ox+17*math.sin(a), oy-17*math.cos(a), ox+20*math.sin(a), oy-20*math.cos(a)], fill=SUBTLE)
    d.line([ox, oy, ox, oy-14], fill=INK, width=2)
    d.line([ox, oy, ox+10, oy+4], fill=INK, width=2)
    write(d, (ox, oy+orr-1), "DAY 13", F_MICRO, ACCENT, "ma")
    px = x + 274
    for k in (0, 1, 2):
        d.rectangle([px+k*6, y+20+k*4, px+30+k*6, y+70+k*4], fill=(255, 255, 250), outline=SUBTLE)
    write(d, (px+20, y+62), "DRAFT 3", F_MICRO, INK, "ma")
    round_box(d, [x+4, y+h-18, x+128, y+h-3], 3, fill=ACCENT)
    write(d, (x+10, y+h-16), "NO DEAL · OVERTIME", F_CHIP, (255, 255, 255))

def art_missiles(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(24, 35, 60))
    for k in range(26):
        sx, sy = x + 7 + k*12, y + 9 + (k*17) % 40
        d.ellipse([sx, sy, sx+1, sy+1], fill=(172, 190, 214))
    heights = [22, 34, 26, 46, 30, 38, 24, 42, 28]
    bx = x + 12
    for k, hh in enumerate(heights):
        d.rectangle([bx+k*34, y+h-hh, bx+k*34+27, y+h], fill=(48, 60, 88))
        for wy in range(y+h-hh+6, y+h-4, 9):
            for wx in range(bx+k*34+5, bx+k*34+23, 8):
                d.rectangle([wx, wy, wx+2, wy+3], fill=(222, 186, 96))
    for off in (0, 16, 32):
        pts = [(x+28+t*8.6, y+64-off-38*math.sin(t/24*math.pi)+t*0.42) for t in range(25)]
        d.line(pts, fill=(240, 213, 138), width=2)
        ex, ey = pts[-1]
        d.ellipse([ex-6, ey-6, ex+6, ey+6], fill=(238, 154, 63))
        d.line([ex-11, ey, ex+11, ey], fill=(255, 222, 140))
        d.line([ex, ey-11, ex, ey+11], fill=(255, 222, 140))
    round_box(d, [x+8, y+7, x+106, y+26], 3, fill=(190, 44, 44))
    write(d, (x+14, y+10), "3 DOWNED", F_CHIP, (255, 255, 255))
    write(d, (x+w-8, y+8), "RIYADH · 01:45 UTC", F_MICRO, (208, 218, 235), "ra")

def art_quake(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(238, 228, 205))
    d.polygon([(x, y+h), (x+60, y+34), (x+112, y+h)], fill=(182, 166, 133))
    d.polygon([(x+82, y+h), (x+150, y+44), (x+220, y+h)], fill=(160, 145, 115))
    for k in range(3):
        hx, hy = x + 185 + k*38, y + h - 30
        d.rectangle([hx, hy-16, hx+24, hy], fill=(228, 216, 190), outline=COAST)
        d.polygon([(hx-3, hy-16), (hx+12, hy-27), (hx+27, hy-16)], fill=(168, 86, 66))
    pts = []
    for k in range(70):
        px, base = x + 8 + k*4.4, y + 62
        if 18 < k < 26:
            base -= 10
        if 26 <= k < 46:
            base += ((-1) ** k) * (16 - abs(32 - k))
        pts.append((px, base))
    d.line(pts, fill=ACCENT, width=2)
    round_box(d, [x+8, y+6, x+74, y+24], 3, fill=ACCENT)
    write(d, (x+14, y+9), "M6.7", F_CHIP, (255, 255, 255))
    write(d, (x+w-8, y+8), "00:09 UTC · 108 km", F_MICRO, SUBTLE, "ra")


# ------------------------------------------------------------- small-card art
def scene_wide(d, x, y, w, h, kind):
    def X(u): return x + u*w/242.0
    def Y(v): return y + v*h/66.0
    if kind == "fire":
        d.rectangle([x, y, x+w, y+h], fill=(22, 34, 62))
        for k, hh in enumerate((24, 36, 28, 44, 30, 40, 26)):
            bx = X(94+k*21)
            d.rectangle([bx, Y(66-hh), bx+X(18)-X(0), Y(66)], fill=(44, 60, 94))
            for j in range(2):
                d.rectangle([bx+5+j*8, Y(66-hh+8), bx+10+j*8, Y(66-hh+15)], fill=(246, 204, 92))
        for off in (0, 14):
            arc = [(X(82+t*9), Y(34-off)-22*math.sin(t/12*math.pi)+t*0.6) for t in range(13)]
            d.line(arc, fill=(255, 214, 112), width=4)
            sparkle(d, arc[-1][0], arc[-1][1], 11, (244, 138, 50))
        d.polygon([(X(210), Y(48)), (X(218), Y(26)), (X(226), Y(48))], fill=(232, 76, 44))
        d.rectangle([X(96), Y(52), X(120), Y(64)], fill=(60, 112, 186))
        d.rectangle([X(96), Y(58), X(120), Y(64)], fill=(248, 212, 72))
    elif kind == "AI":
        d.rectangle([x, y, x+w, y+h], fill=(18, 34, 60))
        for k in range(2):
            bx = X(96+k*56)
            d.rectangle([bx, Y(6), bx+X(46)-X(0), Y(60)], fill=(46, 66, 104), outline=(128, 178, 220), width=2)
            for j in range(3):
                d.line([bx+6, Y(15+j*14), bx+38, Y(15+j*14)], fill=(124, 214, 244), width=3)
                d.ellipse([bx+38, Y(12+j*14), bx+43, Y(17+j*14)], fill=(238, 84, 62))
        round_box(d, [X(200), Y(16), X(238), Y(46)], 4, fill=(248, 250, 252))
        write(d, (X(219), Y(22)), "TAX%", face(12, True), ACCENT, "ma")
    elif kind == "chart":
        d.rectangle([x, y, x+w, y+h], fill=(244, 236, 218))
        d.line([X(94), Y(56), X(238), Y(56)], fill=(110, 100, 86), width=2)
        pts = [(X(96+k*12), Y(12+2.4*k+((-1)**k)*4)) for k in range(12)]
        d.line(pts, fill=ACCENT, width=5)
        d.polygon([pts[-1], (X(238), Y(50)), (X(220), Y(48))], fill=ACCENT)
        write(d, (X(236), Y(6)), "−3.7%", face(12, True), ACCENT, "ra")
        for k in range(3):
            cx = X(202+k*15)
            d.ellipse([cx-9, Y(48), cx+9, Y(64)], fill=(224, 176, 68), outline=(132, 96, 36), width=2)
    elif kind == "planet":
        d.rectangle([x, y, x+w, y+h], fill=(16, 26, 50))
        for k in range(8):
            a = k*math.pi/4
            d.line([X(100), Y(33), X(100+30*math.cos(a)), Y(33+30*math.sin(a))], fill=(250, 196, 84), width=3)
        d.ellipse([X(172), Y(6), X(236), Y(64)], fill=(178, 150, 110), outline=(110, 90, 64), width=2)
        d.ellipse([X(188), Y(18), X(200), Y(29)], fill=(140, 116, 84))
        d.ellipse([X(212), Y(40), X(226), Y(52)], fill=(140, 116, 84))
        d.rectangle([X(108), Y(25), X(140), Y(39)], fill=(214, 220, 230), outline=(92, 106, 130), width=2)
        d.rectangle([X(94), Y(18), X(108), Y(46)], fill=(64, 122, 194))
        d.rectangle([X(140), Y(18), X(154), Y(46)], fill=(64, 122, 194))
        d.polygon([(X(108), Y(39)), (X(140), Y(39)), (X(124), Y(60))], fill=(248, 154, 52))
    elif kind == "deal":
        d.rectangle([x, y, x+X(121), y+h], fill=(36, 62, 130))
        d.rectangle([x+X(121), y, x+w, y+h], fill=(26, 76, 154))
        for k in range(5):
            d.line([X(96+k*27), Y(4), X(96+k*27), Y(62)], fill=(250, 216, 84), width=4)
        for k in range(4):
            d.ellipse([X(100+k*30), Y(9), X(112+k*30), Y(21)], fill=(250, 220, 96))
        d.polygon([(X(146), Y(28)), (X(162), Y(18)), (X(180), Y(28)), (X(162), Y(40))], fill=(234, 188, 138))
        d.polygon([(X(162), Y(40)), (X(180), Y(28)), (X(198), Y(40)), (X(180), Y(54))], fill=(192, 136, 92))
    elif kind == "robot":
        d.rectangle([x, y, x+w, y+h], fill=(216, 228, 236))
        d.rectangle([X(94), Y(12), X(150), Y(62)], fill=(140, 170, 192), outline=(60, 96, 122), width=2)
        for k in range(4):
            d.line([X(100+k*14), Y(12), X(100+k*14), Y(62)], fill=(70, 104, 130), width=2)
        for cx in (172, 212):
            round_box(d, [X(cx-12), Y(12), X(cx+12), Y(30)], 4, fill=(74, 86, 112))
            d.ellipse([X(cx-8), Y(17), X(cx-3), Y(22)], fill=(160, 232, 248))
            d.ellipse([X(cx+3), Y(17), X(cx+8), Y(22)], fill=(160, 232, 248))
            d.rectangle([X(cx-11), Y(32), X(cx+11), Y(52)], fill=(96, 110, 138))
            write(d, (X(cx), Y(36)), "AI", face(10, True), (236, 246, 250), "ma")
            d.line([X(cx-11), Y(36), X(cx-18), Y(46)], fill=(96, 110, 138), width=4)
            d.line([X(cx+11), Y(36), X(cx+18), Y(46)], fill=(96, 110, 138), width=4)
        round_box(d, [X(94), Y(50), X(150), Y(64)], 2, fill=(250, 250, 244))
        write(d, (X(122), Y(53)), "CCW 2026", face(10, True), INK, "ma")
    elif kind == "bat":
        d.rectangle([x, y, x+w, y+h], fill=(202, 228, 194))
        d.rectangle([X(94), Y(46), X(238), Y(66)], fill=(82, 146, 82))
        for sx in (168, 190, 212):
            d.line([X(sx), Y(54), X(sx), Y(20)], fill=(250, 248, 238), width=5)
            d.line([X(sx-6), Y(20), X(sx+6), Y(20)], fill=(250, 248, 238), width=3)
        d.line([X(132), Y(52), X(160), Y(20)], fill=(146, 104, 66), width=8)
        d.ellipse([X(156), Y(12), X(172), Y(28)], fill=ACCENT)
        round_box(d, [X(98), Y(4), X(154), Y(22)], 3, fill=(252, 252, 246))
        write(d, (X(126), Y(7)), "239/1", face(11, True), INK, "ma")
    else:
        d.rectangle([x, y, x+w, y+h], fill=(234, 226, 206))
        d.rectangle([X(128), Y(30), X(136), Y(66)], fill=(96, 72, 48))
        d.line([X(88), Y(18), X(176), Y(18)], fill=(96, 72, 48), width=5)
        d.ellipse([X(128), Y(12), X(136), Y(24)], fill=(226, 180, 64), outline=(96, 72, 48), width=2)
        for px in (92, 172):
            d.line([X(px), Y(19), X(px), Y(38)], fill=(96, 72, 48), width=3)
            d.line([X(px-17), Y(38), X(px+17), Y(38)], fill=(96, 72, 48), width=4)
            d.line([X(px-17), Y(38), X(px-11), Y(52)], fill=(96, 72, 48), width=2)
            d.line([X(px+17), Y(38), X(px+11), Y(52)], fill=(96, 72, 48), width=2)
            d.line([X(px-11), Y(52), X(px+11), Y(52)], fill=(96, 72, 48), width=4)
        d.line([X(194), Y(56), X(220), Y(32)], fill=(110, 78, 50), width=6)
        d.rectangle([X(214), Y(16), X(238), Y(30)], fill=(96, 66, 44))
        round_box(d, [X(188), Y(4), X(238), Y(20)], 3, fill=(252, 252, 246))
        write(d, (X(213), Y(7)), "ICJ", face(11, True), ACCENT, "ma")


# --------------------------------------------------------------------- map
def map_point(lon, lat, box):
    sx, sy, mw, mh = box
    top, bottom = 83, -58
    return (sx + (lon + 180)/360.0*mw,
            sy + (top - lat)/(top - bottom)*mh)

def render_map(d, box):
    sx, sy, mw, mh = box
    d.rectangle([sx, sy, sx+mw, sy+mh], fill=SEA, outline=(156, 179, 194), width=1)
    geo = json.load(open(os.path.join(os.path.dirname(__file__), "world110.geojson"), encoding="utf-8"))
    for lon in range(-180, 181, 30):
        d.line([map_point(lon, 83, box), map_point(lon, -58, box)], fill=GRID, width=1)
    for lat in range(-60, 84, 30):
        d.line([map_point(-180, lat, box), map_point(180, lat, box)], fill=GRID, width=1)
    for feature in geo["features"]:
        if feature["properties"].get("NAME") == "Antarctica":
            continue
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]
            pts = [map_point(p[0], p[1], box) for p in ring if -58 <= p[1] <= 83]
            if len(pts) > 2:
                d.polygon(pts, fill=GROUND)
                d.line(pts + [pts[0]], fill=COAST, width=1)

    radius = 6.5
    # leader lines first, so a number is never painted over
    for story in STORIES:
        number = story[0]
        if number not in SPOT:
            continue
        _, bx, by, ring = SPOT[number]
        if ring <= 3:
            continue
        dx, dy = map_point(story[6], story[7], box)
        vx, vy = bx-dx, by-dy
        length = math.hypot(vx, vy) or 1
        ux, uy = vx/length, vy/length
        ex, ey = bx-ux*(radius+1), by-uy*(radius+1)
        d.line([(dx, dy), (ex, ey)], fill=(76, 90, 102), width=1)
        px, py = -uy, ux
        tip = (ex, ey)
        left = (ex-ux*5+px*2.4, ey-uy*5+py*2.4)
        right = (ex-ux*5-px*2.4, ey-uy*5-py*2.4)
        d.polygon([tip, left, right], fill=(76, 90, 102))
    # exact dots
    for story in STORIES:
        if story[0] not in SPOT:
            continue
        dx, dy = map_point(story[6], story[7], box)
        col = COLOR_OF[story[1]]
        d.ellipse([dx-2.4, dy-2.4, dx+2.4, dy+2.4], fill=col, outline=(255, 255, 255), width=1)
    # numbered badges, digit centred with mm
    for story in STORIES:
        number = story[0]
        if number not in SPOT:
            continue
        _, bx, by, _ = SPOT[number]
        col = COLOR_OF[story[1]]
        d.ellipse([bx-radius, by-radius, bx+radius, by+radius], fill=col, outline=(255, 255, 255), width=2)
        write(d, (bx, by), str(number), F_BADGE_NUM, (255, 255, 255), "mm")


def render_map_legend(d, counts):
    tiny = face(8)
    for row, group in enumerate((REGION_COLORS[:4], REGION_COLORS[4:])):
        lx, ly = 20, 908 + row*11
        for name, col in group:
            label = "%s %d" % (name, counts.get(name, 0))
            width = d.textlength(label, font=tiny)
            d.rectangle([lx, ly+1, lx+8, ly+9], fill=col)
            write(d, (lx+11, ly), label, tiny, INK)
            lx += 11 + width + 8
    write(d, (20, 933),
          "Each number is the story with that number on this page. Dots mark the exact place;", tiny, SUBTLE)
    write(d, (20, 943), "arrows join each dot to its number.", tiny, SUBTLE)


# -------------------------------------------------------------------- page
def draw_page():
    image = Image.new("RGB", (CANVAS, CANVAS), BG)
    d = ImageDraw.Draw(image)

    write(d, (14, 8), "THE WORLD IN ONE DAY", F_KICKER, ACCENT)
    write(d, (CANVAS-14, 9), "35 STORIES · 7 REGIONS · EVERY STORY DATED SATURDAY 21 NOVEMBER 2026",
          F_TINY, SUBTLE, "ra")
    write(d, (CANVAS/2, 44), "Saturday 21 November 2026", F_HEAD, INK, "mm")
    write(d, (CANVAS/2, 80),
          "COP31 overtime  ·  three missiles down over Riyadh  ·  M6.7 Peru quake  ·  Bitcoin below $56k",
          F_DECK, ACCENT, "mm")
    d.line([14, 94, CANVAS-14, 94], fill=INK, width=2)

    col_w = (CANVAS-28)/6
    for k, (value, caption) in enumerate(HEADLINE_FACTS):
        x = 14 + k*col_w
        if k:
            d.line([x, 98, x, 131], fill=HAIRLINE)
        write(d, (x+8, 97), value, F_METRIC, ACCENT)
        write(d, (x+8, 123), caption, F_LABEL, SUBTLE)
    d.line([14, 136, CANVAS-14, 136], fill=INK)

    write(d, (14, 140), "MOST-REPORTED TOPICS →", F_LABEL, INK)
    tx = 168
    for k, topic in enumerate(TRENDING):
        col = REGION_COLORS[k % 7][1]
        tw = d.textlength(topic, font=F_CHIP) + 14
        round_box(d, [tx, 138, tx+tw, 154], 3, fill=col)
        write(d, (tx+7, 139), topic, F_CHIP, (255, 255, 255))
        tx += tw + 5
    d.line([14, 158, CANVAS-14, 158], fill=HAIRLINE)

    counts = {}
    for story in STORIES:
        counts[story[1]] = counts.get(story[1], 0) + 1
    lx = 14
    for name, col in REGION_COLORS:
        label = "%s %d" % (name, counts.get(name, 0))
        width = d.textlength(label, font=F_LABEL) + 12
        d.rectangle([lx, 161, lx+width, 177], fill=col)
        write(d, (lx+6, 163), label, F_LABEL, (255, 255, 255))
        lx += width + 4
    d.line([14, 182, CANVAS-14, 182], fill=INK, width=2)

    lead_art = [art_climate, art_missiles, art_quake]
    for i in range(3):
        story = STORIES[i]
        x, y, w, h = 14 + i*338, 188, 322, 186
        d.rectangle([x, y, x+w, y+h], fill=(255, 254, 249), outline=HAIRLINE)
        lead_art[i](d, x+1, y+1, w-2, 78)
        d.rectangle([x+1, y+79, x+w-1, y+98], fill=COLOR_OF[story[1]])
        write(d, (x+7, y+82), str(story[0]), F_CARD_NUM, (255, 255, 255))
        place = shrink(d, story[2] + "  ·  " + story[1], F_SMALL, w-108)
        write(d, (x+28, y+83), place, F_SMALL, (255, 255, 255))
        write(d, (x+w-6, y+84), story[5], F_MICRO, (255, 255, 255), "ra")
        yy = write_block(d, (x+8, y+103), story[3], F_CARD, w-16, 20, INK, 2)
        write_block(d, (x+8, yy+4), story[4], F_BODY, w-16, 13, INK, 3)

    for i in range(8):
        story = STORIES[3+i]
        row, col = divmod(i, 4)
        x, y, w, h = 14 + col*250, 384 + row*175, 244, 169
        d.rectangle([x, y, x+w, y+h], fill=(255, 254, 249), outline=HAIRLINE)
        d.rectangle([x+1, y+1, x+w-1, y+66], fill=(234, 230, 214))
        scene_wide(d, x+1, y+1, w-2, 65, SMALL_KINDS[i])
        tag = SMALL_LABELS[i]
        tw = d.textlength(tag, font=F_TAG) + 14
        round_box(d, [x+5, y+4, x+5+tw, y+24], 2, fill=ACCENT)
        write(d, (x+11, y+6), tag, F_TAG, (255, 255, 255))
        numbered_dot(d, x+7, y+69, story[0], story[1], 20)
        topic = story[2].split(",")[0].title() + "  ·  " + story[1].title()
        write(d, (x+32, y+71), shrink(d, topic, F_CHIP, w-126), F_CHIP, COLOR_OF[story[1]])
        write(d, (x+w-6, y+72), story[5].split(" · ")[0], F_MICRO, SUBTLE, "ra")
        d.line([x+6, y+92, x+w-6, y+92], fill=(214, 204, 184))
        yy = write_block(d, (x+8, y+96), story[3], F_CARD_SMALL, w-16, 20, INK, 2)
        write_block(d, (x+8, yy+2), story[4], F_TINY, w-16, 14, SUBTLE, 2)

    d.line([14, 732, CANVAS-14, 732], fill=INK, width=2)
    round_box(d, [14, 738, 400, 956], 3, fill=(255, 254, 249), outline=(156, 179, 194))
    write(d, (20, 740), "WHERE IT HAPPENED", F_LABEL, INK)
    render_map(d, (20, 754, 374, 150))
    render_map_legend(d, counts)

    write(d, (408, 740), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES", F_LABEL, INK)
    for idx, story in enumerate(STORIES[12:]):
        col, row = divmod(idx, 12)
        x, y = 408 + col*300, 758 + row*16
        d.rectangle([x, y+1, x+13, y+13], fill=COLOR_OF[story[1]])
        write(d, (x+6.5, y+7), str(story[0]), F_MICRO, (255, 255, 255), "mm")
        label = story[3]
        if d.textlength(story[2].title() + " — " + label, font=F_LIST) <= 279:
            label = story[2].title() + " — " + label
        write(d, (x+17, y+1), shrink(d, label, F_LIST, 279), F_LIST, INK)

    round_box(d, [14, 960, CANVAS-14, 988], 3, fill=(252, 246, 230), outline=ACCENT)
    write(d, (21, 964), "DATE CHECK:", face(11, True), ACCENT)
    write(d, (108, 965),
          "Every story above happened or was first reported on Saturday 21 November 2026 (any time zone). "
          "Nothing from 19–20 November counted; claims attributed to source.", F_SMALL, INK)
    write(d, (14, 993),
          "Sources: Reuters · AP · AFP · BBC · Al Jazeera · ESA · USGS · Kyodo · Anadolu · Guardian · Punch · ABC · RNZ. "
          "Map: Natural Earth 110m; illustrations and layout drawn in code.", F_MICRO, SUBTLE)

    return image


def main():
    image = draw_page()
    target = os.path.join(os.path.dirname(__file__), "entry.png")
    image.save(target, "PNG", optimize=True)
    print("wrote", target, os.path.getsize(target), "bytes")


if __name__ == "__main__":
    main()

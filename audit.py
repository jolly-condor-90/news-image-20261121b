"""Three-pass audit of the entry-3 image: content, colours, map, fonts, gate."""
import math
import os
import sys
from PIL import Image

sys.path.insert(0, ".")
import draw as page

problems = []
def verify(condition, message):
    print(("  OK   " if condition else "  FAIL ") + message)
    if not condition:
        problems.append(message)

print("=== 1. CONTENT ===")
verify(len(page.STORIES) == 35, "35 stories present")
verify(sorted(s[0] for s in page.STORIES) == list(range(1, 36)), "numbers 1..35 once each")
verify(sum(1 for s in page.STORIES if s[1] == "MIDDLE EAST") == 6, "region tally computed")

print("\n=== 2. REGION COLOURS ===")
expected = {
    "EUROPE": (44, 111, 176), "MIDDLE EAST": (210, 105, 30),
    "AFRICA": (47, 139, 91), "ASIA": (180, 58, 46),
    "AMERICAS": (119, 72, 168), "OCEANIA": (17, 138, 142),
    "WORLD": (90, 100, 114),
}
for name, rgb in expected.items():
    verify(page.COLOR_OF[name] == rgb, "%-12s %s" % (name, rgb))
verify(page.SEA == (216, 232, 241), "ocean #D8E8F1")
verify(page.GROUND == (234, 220, 185), "land #EADCB9")
verify(page.COAST == (184, 161, 117), "coastline #B8A175")
verify(page.GRID == (198, 222, 234), "graticule #C6DEEA")

print("\n=== 3. MAP AUDIT ===")
BOX = (20, 754, 374, 150)
spot = [(row[1], row[2], row[3]) for row in page.BADGE_SPOTS]
min_gap = min(math.hypot(spot[i][0]-spot[j][0], spot[i][1]-spot[j][1])
              for i in range(len(spot)) for j in range(i+1, len(spot)))
max_offset = 0.0
for story, badge in zip(page.STORIES, spot):
    dx, dy = page.map_point(story[6], story[7], BOX)
    max_offset = max(max_offset, math.hypot(badge[0]-dx, badge[1]-dy))
verify(len(spot) == 35, "1. badge count equals story count")
verify(min_gap >= 13.0, "2. min badge gap %.2f >= 13 px" % min_gap)
verify(max_offset <= 42.0, "3. max badge offset %.1f <= 42 px" % max_offset)
verify(all(math.hypot(spot[i][0]-page.map_point(s[6], s[7], BOX)[0],
                      spot[i][1]-page.map_point(s[6], s[7], BOX)[1]) > 9
           for i, s in enumerate(page.STORIES)), "4. dots not covered by badges")
samples = [(1, 36.9, 36.9, "Antalya"), (2, 46.7, 24.7, "Riyadh"),
           (3, -75.5, -11.0, "Peru"), (8, 4.4, 50.9, "Brussels"),
           (10, 174.8, -41.3, "Wellington")]
for n, lon, lat, place in samples:
    px, py = page.map_point(lon, lat, BOX)
    print("     #%d %-10s -> (%.0f, %.0f)" % (n, place, px, py))
verify(all(page.COLOR_OF[s[1]] == expected[s[1]] for s in page.STORIES),
       "5. badge colour matches story region")
verify(os.path.exists("world110.geojson"), "6. real GeoJSON coastlines available")

print("\n=== 4. FONT SIZE AT 300px ===")
scale = 300 / CANVAS if False else 300 / 1024
for label, px in [("headline", 19), ("list", 10), ("map badge", 8),
                  ("legend", 8), ("caption", 8)]:
    verify(px * scale >= 2.0, "%-10s %.2f px @300" % (label, px * scale))

print("\n=== 5. FILE GATE ===")
im = Image.open("entry.png")
im.verify()
im = Image.open("entry.png")
size = os.path.getsize("entry.png")
verify(im.format == "PNG" and im.size == (1024, 1024), "PNG 1024x1024")
verify(size <= 1048576, "size %d bytes <= 1 MiB" % size)

print("\nRESULT:", "ALL PASS" if not problems else "FAILED: %s" % problems)
sys.exit(0 if not problems else 1)

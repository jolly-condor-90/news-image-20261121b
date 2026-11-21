"""Local pre-submit checks for the 21 November 2026 news image (entry 3)."""
import os, math
from PIL import Image
import draw

here = os.path.dirname(__file__)
path = os.path.join(here, "entry.png")
im = Image.open(path)
assert im.format == "PNG", im.format
assert im.size == (1024, 1024), im.size
assert os.path.getsize(path) <= 1048576, os.path.getsize(path)
print("CHECK 1 file: PNG %s, %d bytes (limit 1048576) OK" % (im.size, os.path.getsize(path)))

nums = [s[0] for s in draw.STORIES]
assert len(nums) == 35 and sorted(nums) == list(range(1, 36))
regions = sorted({s[1] for s in draw.STORIES})
assert len(regions) == 7, regions
print("CHECK 1 content: 35 numbered stories, 7 regions %s OK" % regions)
counts = {r: sum(1 for s in draw.STORIES if s[1] == r) for r in regions}
for s in draw.STORIES:
    assert s[3] and s[4] and s[5], s[0]
print("  region counts:", counts)

# 300 px preview outside the repository
prev = os.path.join(os.path.dirname(here), "check21")
os.makedirs(prev, exist_ok=True)
im.resize((300, 300), Image.LANCZOS).save(os.path.join(prev, "preview300.png"))
im.crop((10, 730, 404, 958)).resize((1182, 684)).save(os.path.join(prev, "crop_map.png"))
print("CHECK 2 previews written OK")

# map placement from the embedded, shared PLACEMENT table
LT, LB = 83, -58
X0, Y0, X1, Y1 = 20, 754, 394, 904
def proj(lon, lat):
    return (X0 + (lon + 180) / 360.0 * (X1 - X0),
            Y0 + (LT - lat) / (LT - LB) * (Y1 - Y0))
pl = [(p[1], p[2], p[3]) for p in draw.PLACEMENT]
assert len(pl) == 35
worstgap = min(math.hypot(pl[i][0] - pl[j][0], pl[i][1] - pl[j][1])
               for i in range(35) for j in range(i + 1, 35))
assert worstgap >= 13.0, worstgap
maxoff = max(math.hypot(pl[i][0] - proj(s[6], s[7])[0], pl[i][1] - proj(s[6], s[7])[1])
             for i, s in enumerate(draw.STORIES))
assert maxoff <= 42, maxoff
print("CHECK 2 map: 35 badges, min gap %.1f px, max offset %.1f px OK" % (worstgap, maxoff))
print("CHECK 3: inspect check21/preview300.png and crop_map.png.")

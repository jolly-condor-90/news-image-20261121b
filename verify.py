"""Local pre-submit checks for the 21 November 2026 news image (entry 3)."""
import math
import os
from PIL import Image
import draw

here = os.path.dirname(__file__)
path = os.path.join(here, "entry.png")
im = Image.open(path)
assert im.format == "PNG", im.format
assert im.size == (1024, 1024), im.size
assert os.path.getsize(path) <= 1048576, os.path.getsize(path)
print("CHECK 1 file: PNG %s, %d bytes (limit 1048576) OK" % (im.size, os.path.getsize(path)))

numbers = [s[0] for s in draw.STORIES]
assert len(numbers) == 35 and sorted(numbers) == list(range(1, 36))
regions = sorted({s[1] for s in draw.STORIES})
assert len(regions) == 7, regions
print("CHECK 1 content: 35 numbered stories, 7 regions OK")

box = (20, 754, 374, 150)
spots = [(p[1], p[2], p[3]) for p in draw.BADGE_SPOTS]
smallest = min(math.hypot(spots[i][0]-spots[j][0], spots[i][1]-spots[j][1])
               for i in range(len(spots)) for j in range(i+1, len(spots)))
farthest = max(math.hypot(spots[i][0]-draw.map_point(s[6], s[7], box)[0],
                          spots[i][1]-draw.map_point(s[6], s[7], box)[1])
               for i, s in enumerate(draw.STORIES))
assert smallest >= 13 and farthest <= 42, (smallest, farthest)
print("CHECK 2 map: 35 badges, gap %.1f px, offset %.1f px OK" % (smallest, farthest))

preview = os.path.join(os.path.dirname(here), "check21")
os.makedirs(preview, exist_ok=True)
im.resize((300, 300), Image.LANCZOS).save(os.path.join(preview, "preview300.png"))
im.crop((10, 730, 404, 958)).resize((1182, 684)).save(os.path.join(preview, "crop_map.png"))
print("CHECK 3 previews written OK")

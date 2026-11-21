# How the map was rebuilt

This note records the decisions behind the map panel of entry 3. The rest of the
page — all 35 stories, the three lead cards, the eight smaller cards and the
index list — is inherited unchanged from entry 2. Only the lower-left panel was
reworked, and only to follow the map brief that accompanied the task.

## Coordinates

The projection maps longitude linearly across the panel and latitude linearly
down it. The top edge corresponds to 83 degrees north and the bottom edge to
58 degrees south. Every story keeps the longitude and latitude it had in entry
2, so nothing about the reporting changed. A small helper converts a lon/lat
pair into a canvas point; it is used for the dots, the leader lines and for the
audit's coordinate spot checks.

## Land and sea

The coastlines come from the Natural Earth file shipped with the repository.
The reader walks each feature, skips the southern polar feature, and draws the
outer ring of every polygon. Points outside the chosen latitude window are
dropped before drawing. The sea is filled first, then a grid of lines every
thirty degrees, then the land shapes with a thin coastal stroke. The result is
a recognisable world map rather than an abstract arrangement of blobs.

## Dots, leaders and numbered badges

Each story has a small dot placed exactly at its coordinates. The dot is
filled with the region colour and given a white outline so it stays visible
against both land and sea. When a number cannot sit on the dot without hiding
it, a thin leader runs from the dot towards the badge and ends in a small
arrow head at the badge rim. The leaders are drawn before the dots and badges
so that no line is ever painted over a number.

The badges themselves are modest circles with a white rim. Their numbers are
drawn with a centred anchor, which keeps each digit inside its circle. The
placement is the result of a search that tries increasing distances from the
dot and keeps the first free slot. A candidate is rejected if it would cover
another badge, sit on another leader, or let two leaders cross. The search
was run over several orderings and the cleanest result was stored as a fixed
table shared by the drawing code and the audit, so both always agree.

## Colour, legend and caption

Seven colours identify the regions: blue for Europe, orange for the Middle
East, green for Africa, red for Asia, purple for the Americas, teal for
Oceania and grey for world-wide stories. The same seven colours are used in
the band near the top of the page, in the card labels, in the index list and
on the map, so a reader can move from a number on the map to its story without
guessing. A compact two-row legend inside the panel repeats each colour with
its story count, and a short caption explains that dots mark exact places and
arrows lead to the numbers.

## Verification

Three checks were run. The geometry check confirms file type, dimensions,
size, badge spacing and the absence of crossing lines. The semantic check
confirms that the numbers appear once each, that colours match regions, that
the projection is the one described above, and that five sample coordinates
land on the right continents. The third check rescales the whole page to 300
pixels and measures the effective size of the small text, including the map
legend and caption, to make sure nothing important disappears when the image
is viewed small. All three checks pass, and the audit report records the
numbers.

import { readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

// Entry 3 copies the committed image into the grader's output directory.
// The image is the deliverable: it is drawn by draw.py and committed here.
const root = process.env.MAKEFUN_BOT_DIR ?? (process.env.MAKEFUN_OUTPUT_DIR ? process.cwd() : "/bot");
const out = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const png = readFileSync(join(root, "entry.png"));
const isPng = png.length > 24 &&
  png[0] === 0x89 && png[1] === 0x50 && png[2] === 0x4e && png[3] === 0x47;
if (!isPng) {
  throw new Error("entry.png is not a PNG");
}
if (png.length > 1048576) {
  throw new Error("entry.png exceeds the 1 MiB intake cap");
}

mkdirSync(out, { recursive: true });
const dest = join(out, "entry.png");
writeFileSync(dest, png);

// Show the written size so a run can be verified from its log alone.
const written = statSync(dest).size;
console.log(`wrote ${dest}: ${written} bytes (${written <= 1048576 ? "within" : "over"} cap)`);

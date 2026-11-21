// make.fun entry: copy the committed image into the output folder.
// draw.py is the source that produced entry.png; it is not needed at grading time.
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? (process.env.MAKEFUN_OUTPUT_DIR ? process.cwd() : "/bot");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const bytes = readFileSync(join(botDir, "entry.png"));
const looksLikePng = bytes.length > 24 && bytes[0] === 0x89 &&
  bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47;
if (!looksLikePng) throw new Error("entry.png is not a PNG");
if (bytes.length > 1048576) throw new Error("entry.png exceeds 1 MiB");

mkdirSync(outputDir, { recursive: true });
const target = join(outputDir, "entry.png");
writeFileSync(target, bytes);
console.log("entry.png written:", statSync(target).size, "bytes");

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

// The image is committed with the repository; the grader copies it to /output.
const root = process.env.MAKEFUN_BOT_DIR ?? (process.env.MAKEFUN_OUTPUT_DIR ? process.cwd() : "/bot");
const out = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(out, { recursive: true });
const png = readFileSync(join(root, "entry.png"));
if (png.subarray(1, 4).toString() !== "PNG") {
  throw new Error("entry.png is not a PNG");
}
writeFileSync(join(out, "entry.png"), png);
console.log("wrote entry.png", png.length, "bytes");

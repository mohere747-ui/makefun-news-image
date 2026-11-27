// The committed poster is copied byte-for-byte to the output directory.
// Copy the rendered poster into the directory the grader reads.
const { mkdirSync, copyFileSync } = require("node:fs");
const { join } = require("node:path");

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const source = join(__dirname, "entry.png");
const destination = join(outputDir, "entry.png");

mkdirSync(outputDir, { recursive: true });
copyFileSync(source, destination);
console.log(`copied ${source} to ${destination}`);

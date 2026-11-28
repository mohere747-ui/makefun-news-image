// The broadsheet poster is copied byte-for-byte to the grader's output.
'use strict';

const fs = require('node:fs');
const path = require('node:path');

// entry.png lives in the repository root, next to this script.
const repoRoot = __dirname;
const source = path.join(repoRoot, 'entry.png');

// Override with MAKEFUN_OUTPUT_DIR; fall back to /output.
const outputDir = path.resolve(process.env.MAKEFUN_OUTPUT_DIR || '/output');
const destination = path.join(outputDir, 'entry.png');

fs.mkdirSync(outputDir, { recursive: true });
fs.copyFileSync(source, destination);

console.log(`source: ${source}`);
console.log(`destination: ${destination}`);

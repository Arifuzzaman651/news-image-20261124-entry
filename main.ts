// "The World in One Day" — news-image-20261124 entry (Node 22, standard library only).
// The poster is drawn by render_poster.py and shipped as entry.png beside this file;
// this program copies it to the grader's output directory, verifying it on the way.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = new URL('./entry.png', import.meta.url);
const target = join(outDir, 'entry.png');

if (!existsSync(source)) {
  throw new Error('entry.png is missing from the repository');
}

// A real PNG starts with its 8-byte magic; the first IHDR chunk then
// names the width and height (bytes 16-19 and 20-23, big-endian).
const bytes = readFileSync(source);
const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(magic)) {
  throw new Error('entry.png is not a PNG file');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}; the gate allows at most 1024x1024`);
}
if (bytes.length === 0 || bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes; the gate allows at most 1 MiB`);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(target, bytes);

const copied = readFileSync(target);
const digest = (b) => createHash('sha256').update(b).digest('hex');
if (digest(copied) !== digest(bytes)) {
  throw new Error('the copied entry.png does not match the repository copy');
}
console.log(`Wrote ${target} (${width}x${height}, ${bytes.length} bytes, sha256 ${digest(bytes).slice(0, 12)}…)`);

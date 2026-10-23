import { cp, copyFile, mkdir, readdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const frontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(frontend, 'app', 'dist');
await copyFile(path.join(output, 'index.html'), path.join(frontend, 'index.html'));
const sourceAssets = path.join(output, 'assets');
const targetAssets = path.join(frontend, 'assets');
await mkdir(targetAssets, { recursive: true });
const current = new Set(await readdir(sourceAssets));
for (const name of await readdir(targetAssets)) {
  if (/^index-.*\.(css|js)$/.test(name) && !current.has(name)) await rm(path.join(targetAssets, name));
}
await cp(sourceAssets, targetAssets, { recursive: true, force: true });

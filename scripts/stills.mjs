// Renderiza stills de control: node scripts/stills.mjs [frames...]  (sin args: inicio y mitad de cada sección)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
const plan = JSON.parse(fs.readFileSync('public/plan.json', 'utf8'));
let frames = process.argv.slice(2).map(Number);
if (!frames.length) {
  frames = [20, plan.introEnd - 30];
  for (const s of plan.sections) frames.push(s.start + 50, Math.round((s.start + s.end) / 2));
  frames.push(plan.annexStart + 120);
}
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'Poster', chromiumOptions: {gl: 'swiftshader'}});
fs.mkdirSync('work/stills', {recursive: true});
for (const f of frames) {
  const out = `work/stills/f${String(f).padStart(5, '0')}.jpg`;
  await renderStill({serveUrl, composition, frame: f, output: out, imageFormat: 'jpeg', jpegQuality: 85, chromiumOptions: {gl: 'swiftshader'}});
  console.log(out);
}

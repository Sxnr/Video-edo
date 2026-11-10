import {spring} from 'remotion';
import {plan, Rect} from './plan';
import {Box, stageFor, FULL} from './layout';

/** Cámara: mapea px del póster a px de pantalla: screen = p * s + t */
export type Cam = {cx: number; cy: number; ax: number; ay: number; s: number};
const MAX_SCALE = 0.78; // no ampliar más que esto (los recortes son 300 dpi: el texto sigue nítido)

export const fit = (r: Rect, st: Box, fill = 0.94, maxS = MAX_SCALE): Cam => {
  const s = Math.min((st.w * fill) / r[2], (st.h * fill) / r[3], maxS);
  return {cx: r[0] + r[2] / 2, cy: r[1] + r[3] / 2, ax: st.x + st.w / 2, ay: st.y + st.h / 2, s};
};
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const mix = (a: Cam, b: Cam, t: number): Cam => ({
  cx: lerp(a.cx, b.cx, t), cy: lerp(a.cy, b.cy, t), ax: lerp(a.ax, b.ax, t), ay: lerp(a.ay, b.ay, t),
  s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), t)),
});
const union = (a: Rect, b: Rect, m = 0.1): Rect => {
  const x0 = Math.min(a[0], b[0]), y0 = Math.min(a[1], b[1]);
  const x1 = Math.max(a[0] + a[2], b[0] + b[2]), y1 = Math.max(a[1] + a[3], b[1] + b[3]);
  const w = x1 - x0, h = y1 - y0;
  return [x0 - w * m, y0 - h * m, w * (1 + 2 * m), h * (1 + 2 * m)];
};
const grow = (r: Rect, k: number): Rect => [r[0] - (r[2] * (k - 1)) / 2, r[1] - (r[3] * (k - 1)) / 2, r[2] * k, r[3] * k];

type Key = {f: number; dur: number; cam: Cam; sec?: number};
const [PW, PH] = plan.posterSize;
const POSTER: Rect = [0, 0, PW, PH];

const buildKeys = (): Key[] => {
  const keys: Key[] = [{f: 0, dur: 1, cam: fit(POSTER, FULL, 0.96)}];
  const S = plan.sections;
  S.forEach((s, i) => {
    const st = stageFor(s);
    const boxCam = fit(s.box, st);
    if (i > 0) {
      const prev = S[i - 1];
      keys.push({f: prev.end - 4, dur: 20, cam: fit(union(prev.box, s.box), FULL, 0.96, 0.3)});
    }
    const arrive = i === 0 ? plan.introEnd - 6 : S[i - 1].end + 12;
    keys.push({f: arrive, dur: 28, cam: boxCam, sec: s.n});
    // énfasis con zoom: entrar al elemento y volver al recuadro completo
    const foc = plan.cues.filter((c) => c.s === s.n && (c.kind === 'focus' || c.kind === 'zoom')).sort((a, b) => a.f0 - b.f0);
    foc.forEach((c, j) => {
      const r = grow(c.rect!, 1.35);
      keys.push({f: Math.max(c.f0 - 6, arrive + 20), dur: 24, cam: fit(r, st, 0.94), sec: s.n});
      const next = foc[j + 1];
      if (!next || next.f0 - 6 > c.f1 + 10) keys.push({f: Math.min(c.f1, s.end - 2), dur: 24, cam: boxCam, sec: s.n});
    });
  });
  keys.push({f: plan.annexStart - 14, dur: 30, cam: fit(POSTER, FULL, 0.96)});
  return keys.sort((a, b) => a.f - b.f);
};
const KEYS = buildKeys();

const prog = (frame: number, dur: number) =>
  frame <= 0 ? 0 : spring({frame, fps: plan.fps, config: {damping: 200, mass: 1}, durationInFrames: dur});

export const cameraAt = (frame: number): Cam => {
  let from = KEYS[0].cam, to = KEYS[0].cam, f0 = 0, dur = 1;
  for (const k of KEYS) {
    if (k.f > frame) break;
    from = mix(from, to, prog(k.f - f0, dur));
    to = k.cam; f0 = k.f; dur = k.dur;
  }
  let cam = mix(from, to, prog(frame - f0, dur));
  // drift lento tipo Ken Burns mientras se habla
  const s = plan.sections.find((x) => frame >= x.start && frame < x.end);
  if (s) {
    const p = (frame - s.start) / Math.max(1, s.end - s.start);
    cam = {...cam, s: cam.s * (1 + 0.025 * p), cx: cam.cx + Math.sin(p * Math.PI) * 6 / cam.s};
  }
  return cam;
};
export const toScreen = (cam: Cam) => ({s: cam.s, tx: cam.ax - cam.cx * cam.s, ty: cam.ay - cam.cy * cam.s});

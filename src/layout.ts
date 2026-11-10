import {PIP, PIP_MARGIN, W, H} from './theme';
import {plan, Rect, Section} from './plan';

export type Box = {x: number; y: number; w: number; h: number};
export const pipBox = (kind: 'portrait' | 'landscape'): Box => {
  const p = PIP[kind];
  return {x: W - PIP_MARGIN - p.w, y: H - PIP_MARGIN - p.h, w: p.w, h: p.h};
};
export const isWide = (r: Rect) => r[2] / r[3] > 2.6;

/** Zona de pantalla donde se centra el recuadro activo (no choca con PiP ni subtítulos). */
export const stageFor = (s: Section): Box => {
  if (!s.pip) return {x: 60, y: 56, w: 930, h: 780}; // sección 5: la hoja ocupa la derecha
  const p = pipBox(s.pip);
  if (isWide(s.box)) return {x: 60, y: 44, w: W - 120, h: p.y - 40 - 44};
  return {x: 60, y: 44, w: p.x - 60 - 60, h: 810};
};
/** Zona de subtítulos (abajo, dentro del área segura, a la izquierda del PiP). */
export const captionZone = (s: Section | undefined): Box => {
  if (s && s.pip) {
    const p = pipBox(s.pip);
    return {x: 60, y: 880, w: p.x - 60 - 40, h: 150};
  }
  return {x: 200, y: 880, w: W - 400 - 120, h: 150};
};
export const FULL: Box = {x: 60, y: 40, w: W - 120, h: H - 80};

export const sectionAt = (f: number): Section | undefined => {
  const S = plan.sections;
  for (let i = 0; i < S.length; i++) {
    const nextStart = i + 1 < S.length ? S[i + 1].start : Infinity;
    if (f >= S[i].start - 6 && f < Math.min(nextStart - 6, S[i].end + 30)) return S[i];
  }
  return undefined;
};

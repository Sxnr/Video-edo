import React from 'react';
import {Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {plan, Section, Cue} from './plan';
import {C, FONT_SANS, FONT_SERIF, W} from './theme';
import {pipBox, stageFor, captionZone, sectionAt, Box} from './layout';
import {sp, window01, clamp} from './anim';

const SHEET_W = 1259, SHEET_H = 799; // coords originales de procedimiento_edo.png
const S = plan.sections;
const nextSame = (i: number) => i + 1 < S.length && S[i + 1].speaker === S[i].speaker && !!S[i + 1].pip;
const prevSame = (i: number) => i > 0 && S[i - 1].speaker === S[i].speaker && !!S[i - 1].pip;

export const Overlays: React.FC<{frame: number}> = ({frame}) => {
  const cur = sectionAt(frame);
  return (
    <>
      <SheetPanel frame={frame} />
      <Callouts frame={frame} />
      {S.map((s, i) => s.pip ? <Pip key={s.n} s={s} i={i} frame={frame} /> : null)}
      <VoiceBadge frame={frame} />
      <Captions frame={frame} cur={cur} />
    </>
  );
};

/* ---------- PiP del hablante ---------- */
const Pip: React.FC<{s: Section; i: number; frame: number}> = ({s, i, frame}) => {
  const b = pipBox(s.pip!);
  const end = nextSame(i) ? S[i + 1].start : s.end + 8;
  const inn = prevSame(i) ? 1 : sp(frame - s.start + 4, 20);
  const out = nextSame(i) ? 0 : sp(frame - end, 14);
  const o = clamp(inn - out);
  if (frame < s.start - 4 || frame > end + 16) return null;
  const lt = s.lowerThird ? window01(frame, s.start + 10, s.start + 160, 18, 14) : 0;
  return (
    <>
      <div style={{position: 'absolute', left: b.x, top: b.y, width: b.w, height: b.h, borderRadius: 22, overflow: 'hidden',
        opacity: o, transform: `translateY(${(1 - o) * 30}px) scale(${0.96 + 0.04 * o})`,
        boxShadow: '0 14px 40px rgba(10,30,40,0.35)', border: '4px solid white', background: '#000'}}>
        <Sequence from={s.start} durationInFrames={end - s.start + 1} layout="none">
          <OffthreadVideo src={staticFile(`pip/s${s.n}.mp4`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </Sequence>
      </div>
      {lt > 0.001 && <LowerThird s={s} b={b} o={lt} />}
    </>
  );
};

const LowerThird: React.FC<{s: Section; b: Box; o: number}> = ({s, b, o}) => (
  <div style={{position: 'absolute', right: W - (b.x + b.w), top: b.y - 92, opacity: o,
    transform: `translateX(${(1 - o) * 40}px)`, display: 'flex', alignItems: 'stretch', boxShadow: '0 8px 24px rgba(10,30,40,0.3)', borderRadius: 14, overflow: 'hidden'}}>
    <div style={{width: 10, background: C.orange}} />
    <div style={{background: C.petrol, padding: '10px 22px 12px 18px', color: 'white'}}>
      <div style={{fontFamily: FONT_SERIF, fontWeight: 700, fontSize: 32, lineHeight: 1.1, whiteSpace: 'nowrap'}}>{s.speaker}</div>
      <div style={{fontFamily: FONT_SANS, fontSize: 24, color: C.peach, whiteSpace: 'nowrap'}}>{s.role}</div>
    </div>
  </div>
);

/* ---------- indicador de voz (sección sin cámara) ---------- */
const VoiceBadge: React.FC<{frame: number}> = ({frame}) => {
  return (
    <>
      {S.filter((s) => !s.pip).map((s) => {
        const o = window01(frame, s.start, s.end + 4, 16, 12);
        if (o <= 0.001) return null;
        const bars = [0, 1, 2, 3, 4, 5, 6];
        return (
          <div key={s.n} style={{position: 'absolute', right: 60, bottom: 60, height: 74, padding: '0 22px', borderRadius: 37, opacity: o,
            background: C.petrol, display: 'flex', alignItems: 'center', gap: 16, boxShadow: '0 10px 30px rgba(10,30,40,0.3)'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: 5, height: 40}}>
              {bars.map((k) => {
                const e = plan.env[Math.max(0, frame - (k % 3))] ?? 0;
                const hgt = 6 + 34 * e * (0.55 + 0.45 * Math.abs(Math.sin(frame * 0.35 + k * 1.7)));
                return <div key={k} style={{width: 6, height: hgt, borderRadius: 3, background: k % 2 ? C.peach : C.orange}} />;
              })}
            </div>
            <div style={{color: 'white', fontFamily: FONT_SERIF, fontWeight: 700, fontSize: 28, whiteSpace: 'nowrap'}}>{s.speaker}</div>
          </div>
        );
      })}
    </>
  );
};

/* ---------- hoja de procedimiento (sección 5 y comienzo de la 6) ---------- */
const sheetCues = plan.cues.filter((c) => c.kind === 'sheet');
const SHEET_POS: Record<number, {box: Box; rotY: number}> = {
  5: {box: {x: 1030, y: 110, w: 830, h: 527}, rotY: -12},
  6: {box: {x: 64, y: 478, w: 560, h: 356}, rotY: 10},
};
const SheetPanel: React.FC<{frame: number}> = ({frame}) => {
  const out: React.ReactNode[] = [];
  for (const sec of S) {
    const pos = SHEET_POS[sec.n];
    if (!pos) continue;
    const cs = sheetCues.filter((c) => c.s === sec.n);
    if (!cs.length) continue;
    const f0 = sec.n === 5 ? sec.start + 6 : cs[0].f0 - 4;
    const f1 = sec.n === 5 ? sec.end : cs[cs.length - 1].f1;
    const o = window01(frame, f0, f1, 22, 16);
    if (o <= 0.001) continue;
    // cámara de la hoja: viaja al paso activo (zoom ≤ 1,3×)
    const target = (c?: Cue) => {
      if (!c) return {cx: 0.5, cy: 0.5, z: 1};
      const [x, y, w, h] = c.rect!;
      const z = Math.min(1.3, 0.8 / Math.max(w / SHEET_W, h / SHEET_H));
      return {cx: (x + w / 2) / SHEET_W, cy: (y + h / 2) / SHEET_H, z: Math.max(1, z)};
    };
    type T = {cx: number; cy: number; z: number};
    const lerpT = (a: T, b: T, k: number): T => ({cx: a.cx + (b.cx - a.cx) * k, cy: a.cy + (b.cy - a.cy) * k, z: a.z + (b.z - a.z) * k});
    let from = target(undefined), to = from, fs = 0;
    for (const c of cs) {
      if (c.f0 - 4 > frame) break;
      from = lerpT(from, to, sp(c.f0 - 4 - fs, 26)); to = target(c); fs = c.f0 - 4;
    }
    const st = lerpT(from, to, sp(frame - fs, 26));
    const {box, rotY} = pos;
    const z = st.z;
    // mantener el paso centrado pero sin mostrar fuera de la hoja
    const tx = clamp(0.5 - st.cx * z, 1 - z, 0) * box.w;
    const ty = clamp(0.5 - st.cy * z, 1 - z, 0) * box.h;
    out.push(
      <div key={sec.n} style={{position: 'absolute', left: box.x, top: box.y, width: box.w, height: box.h, opacity: o,
        transform: `perspective(1600px) rotateY(${rotY * (0.6 + 0.4 * o)}deg) rotateX(3deg) translateX(${(1 - o) * 60 * Math.sign(-rotY)}px)`,
        borderRadius: 18, overflow: 'hidden', boxShadow: '0 18px 50px rgba(10,30,40,0.45)', border: `5px solid ${C.white}`, background: '#262626'}}>
        <div style={{position: 'absolute', left: tx, top: ty, width: box.w * z, height: box.h * z}}>
          <Img src={staticFile('sheet.png')} style={{width: '100%', height: '100%'}} />
          {cs.map((c, i) => {
            const v = window01(frame, c.f0, c.f1, 12, 10);
            if (v <= 0.001) return null;
            const [x, y, w, h] = c.rect!;
            return <div key={i} style={{position: 'absolute', left: `${(x / SHEET_W) * 100}%`, top: `${(y / SHEET_H) * 100}%`,
              width: `${(w / SHEET_W) * 100}%`, height: `${(h / SHEET_H) * 100}%`, opacity: v, borderRadius: 10,
              border: `3px solid ${C.orange}`, boxShadow: '0 0 18px rgba(232,99,43,0.8)', background: 'rgba(232,99,43,0.10)'}} />;
          })}
        </div>
        <div style={{position: 'absolute', left: 14, top: 10, padding: '4px 12px', borderRadius: 8, background: 'rgba(19,78,94,0.9)',
          color: 'white', fontSize: 20, fontFamily: FONT_SANS}}>Resolución a mano · {sec.n === 5 ? 'Vicente' : 'cálculo de k (Modelo 1)'}</div>
      </div>,
    );
  }
  return <>{out}</>;
};

/* ---------- textos del póster ampliados ---------- */
const md = (t: string) => t.split(/(\*\*[^*]+\*\*)/).map((p, i) =>
  p.startsWith('**') ? <b key={i} style={{color: C.petrol}}>{p.slice(2, -2)}</b> : <span key={i}>{p}</span>);
const Callouts: React.FC<{frame: number}> = ({frame}) => (
  <>
    {plan.cues.filter((c) => c.kind === 'callout').map((c, i) => {
      const o = window01(frame, c.f0, c.f1, 16, 12);
      if (o <= 0.001) return null;
      const sec = S.find((x) => x.n === c.s)!;
      const st = stageFor(sec);
      const p = sec.pip ? pipBox(sec.pip) : {x: W - 60};
      return (
        <div key={i} style={{position: 'absolute', left: 80, top: st.y + st.h + 14, width: (p as Box).x - 80 - 50, opacity: o,
          transform: `translateY(${(1 - o) * 24}px)`, background: C.white, borderRadius: 18, padding: '20px 28px',
          borderLeft: `10px solid ${C.orange}`, boxShadow: '0 12px 36px rgba(10,30,40,0.25)', fontSize: 34, lineHeight: 1.32, color: C.text}}>
          {md(c.text!)}
        </div>
      );
    })}
  </>
);

/* ---------- subtítulos ---------- */
const Captions: React.FC<{frame: number; cur?: Section}> = ({frame}) => {
  const cap = plan.captions.find((c) => frame >= c.f0 - 2 && frame < c.f1);
  if (!cap) return null;
  const sec = S.find((x) => x.n === cap.section);
  const z = captionZone(sec);
  const o = clamp((frame - cap.f0 + 3) / 4) * clamp((cap.f1 - frame) / 4);
  let active = -1;
  cap.words.forEach((w, i) => { if (frame >= w.f0 - 1) active = i; });
  return (
    <div style={{position: 'absolute', left: z.x, top: z.y, width: z.w, height: z.h, display: 'flex', alignItems: 'flex-end', justifyContent: 'center'}}>
      <div style={{maxWidth: z.w, background: 'rgba(15,40,50,0.80)', borderRadius: 16, padding: '10px 26px 12px', opacity: o,
        fontFamily: FONT_SANS, fontSize: 40, lineHeight: 1.25, color: 'white', textAlign: 'center',
        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', boxShadow: '0 6px 18px rgba(0,0,0,0.2)'}}>
        {cap.words.map((w, i) => (
          <span key={i} style={{color: i === active ? '#FF8A4C' : i < active ? 'white' : 'rgba(255,255,255,0.82)',
            }}>{w.w}{i < cap.words.length - 1 ? ' ' : ''}</span>
        ))}
      </div>
    </div>
  );
};

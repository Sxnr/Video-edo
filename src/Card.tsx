import React from 'react';
import {Img, staticFile} from 'remotion';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import {plan, Rect, Section, Cue} from './plan';
import {C} from './theme';
import {window01, pulse, sp, clamp} from './anim';

const RADIUS = 30; // px del póster

/** Recuadro de la sección que se desprende del póster (3D), con sus énfasis. */
export const Card: React.FC<{sec: Section; lift: number; s: number; frame: number}> = ({sec, lift, s, frame}) => {
  const [x, y, w, h] = sec.box;
  const rotY = x < 2000 ? 5 : -5; // columna izquierda / derecha
  const cues = plan.cues.filter((c) => c.s === sec.n);
  const rel = (r: Rect): React.CSSProperties => ({position: 'absolute', left: r[0] - x, top: r[1] - y, width: r[2], height: r[3]});
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transformOrigin: '50% 50%',
      transform: `perspective(${1800 / s}px) translateZ(${(lift * 70) / s}px) rotateX(${lift * 5}deg) rotateY(${lift * rotY}deg)`,
      boxShadow: `0 ${(lift * 26) / s}px ${(lift * 70) / s}px rgba(10,30,40,${0.38 * lift})`,
      borderRadius: RADIUS, overflow: 'hidden', background: C.white}}>
      <Img src={staticFile(`boxes/${sec.n}.png`)} style={{position: 'absolute', width: w, height: h}} />
      {cues.map((c, i) => <CueLayer key={i} c={c} frame={frame} s={s} rel={rel} sec={sec} />)}
    </div>
  );
};

const CueLayer: React.FC<{c: Cue; frame: number; s: number; rel: (r: Rect) => React.CSSProperties; sec: Section}> = ({c, frame, s, rel, sec}) => {
  if (!c.rect) return null;
  const [x, y, w, h] = sec.box;
  const vis = window01(frame, c.f0, c.f1);
  if (c.kind === 'card') {
    // tarjetas de cifra de la sección 8: atenuadas hasta que se nombran, luego "pop"
    const on = sp(frame - c.f0, 16);
    const p = pulse(frame, c.f0, 18);
    return (
      <>
        <div style={{...rel(c.rect), background: C.white, opacity: 0.78 * (1 - on), borderRadius: 24}} />
        {p > 0 && <Lens r={c.rect} box={sec.box} n={sec.n} scale={1 + 0.1 * p} s={s} />}
        <Frame r={c.rect} rel={rel} s={s} o={on * (1 - clamp((frame - c.f0 - 50) / 20)) } />
      </>
    );
  }
  if (vis <= 0.001) return null;
  if (c.kind === 'mark' || c.kind === 'focus') return <Frame r={c.rect} rel={rel} s={s} o={vis} />;
  if (c.kind === 'pop') {
    const p = pulse(frame, c.f0, 20);
    return (
      <>
        {p > 0 && <Lens r={c.rect} box={sec.box} n={sec.n} scale={1 + 0.07 * p} s={s} />}
        <Frame r={c.rect} rel={rel} s={s} o={vis} fill />
      </>
    );
  }
  if (c.kind === 'katex') {
    const html = katex.renderToString(c.tex!, {throwOnError: false});
    const r = c.rect;
    const k = 0.92 + 0.12 * sp(frame - c.f0, 18);
    return (
      <div style={{...rel([r[0] - r[2] * 0.08, r[1] - r[3] * 0.12, r[2] * 1.16, r[3] * 1.24]), display: 'flex', alignItems: 'center',
        justifyContent: 'center', background: C.white, borderRadius: 22, opacity: vis, transform: `scale(${k})`,
        border: `${4 / s}px solid ${C.orange}`, boxShadow: `0 0 ${24 / s}px rgba(232,99,43,0.55), 0 ${8 / s}px ${24 / s}px rgba(0,0,0,0.2)`,
        color: C.text, fontSize: r[3] * 0.5, whiteSpace: 'nowrap'}}>
        <span dangerouslySetInnerHTML={{__html: html}} />
      </div>
    );
  }
  return null;
};

/** Marco naranjo suave alrededor del elemento mencionado */
const Frame: React.FC<{r: Rect; rel: (r: Rect) => React.CSSProperties; s: number; o: number; fill?: boolean}> = ({r, rel, s, o, fill}) => {
  const pad = 10;
  return (
    <div style={{...rel([r[0] - pad, r[1] - pad, r[2] + 2 * pad, r[3] + 2 * pad]), opacity: o,
      border: `${4.5 / s}px solid ${C.orange}`, borderRadius: 20,
      background: fill ? 'rgba(252,227,214,0.28)' : 'rgba(252,227,214,0.10)',
      boxShadow: `0 0 ${22 / s}px rgba(232,99,43,0.55)`, transform: `scale(${0.985 + 0.015 * o})`}} />
  );
};

/** Copia ampliada de un trozo del recuadro (para el "pop" de una cifra) */
const Lens: React.FC<{r: Rect; box: Rect; n: number; scale: number; s: number}> = ({r, box, n, scale, s}) => (
  <div style={{position: 'absolute', left: r[0] - box[0], top: r[1] - box[1], width: r[2], height: r[3], overflow: 'hidden',
    transform: `scale(${scale})`, borderRadius: 14, boxShadow: `0 ${10 / s}px ${30 / s}px rgba(0,0,0,0.25)`, background: C.white}}>
    <Img src={staticFile(`boxes/${n}.png`)} style={{position: 'absolute', left: -(r[0] - box[0]), top: -(r[1] - box[1]), width: box[2], height: box[3]}} />
  </div>
);

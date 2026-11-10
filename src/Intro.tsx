import React from 'react';
import {Img, staticFile} from 'remotion';
import {plan} from './plan';
import {C, FONT_SANS, FONT_SERIF} from './theme';
import {sp, clamp} from './anim';

const NAMES: [string, string][] = [['Adonis', 'Adonis Hernández'], ['Yeny', 'Yeny Zapata'], ['Vicente', 'Vicente Acevedo'],
  ['Francisco', 'Francisco Carrera'], ['Martina', 'Martina Cares']];

export const Intro: React.FC<{frame: number}> = ({frame}) => {
  const end = plan.introEnd;
  if (frame > end + 24) return null;
  const inn = sp(frame - 2, 34);
  const out = sp(frame - (end - 8), 22);
  const o = clamp(inn - out);
  const bgO = clamp(1 - out);
  const line = (d: number) => {
    const k = sp(frame - d, 22);
    return {opacity: k * (1 - out), transform: `translateY(${(1 - k) * 18}px)`};
  };
  return (
    <div style={{position: 'absolute', inset: 0, opacity: bgO, background: `rgba(238,242,244,${0.86})`,
      display: 'flex', alignItems: 'center', justifyContent: 'flex-start', paddingLeft: 70}}>
      <div style={{width: 1400, borderRadius: 34, background: C.petrol, padding: '50px 56px 46px', color: 'white', opacity: o,
        transform: `perspective(1800px) translateZ(${(1 - inn) * -160 + out * -60}px) rotateX(${(1 - inn) * 10}deg)`,
        boxShadow: '0 30px 80px rgba(10,30,40,0.40)'}}>
        <div style={{display: 'flex', gap: 48, alignItems: 'center'}}>
          <div style={{flex: 1}}>
            <div style={{fontFamily: FONT_SERIF, fontWeight: 700, fontSize: 44, lineHeight: 1.18, whiteSpace: 'nowrap', ...line(8)}}>
              MODELACIÓN DEL ENFRIAMIENTO DE LA LECHE<br />MEDIANTE LA LEY DE ENFRIAMIENTO DE NEWTON
            </div>
            <div style={{height: 6, width: 220, background: C.orange, borderRadius: 3, margin: '26px 0 22px', ...line(14)}} />
          </div>
          <div style={{background: 'white', borderRadius: 22, padding: 14, ...line(4)}}>
            <Img src={staticFile('logo.png')} style={{height: 190, display: 'block'}} />
          </div>
        </div>
        <div style={{fontFamily: FONT_SANS, fontSize: 29, lineHeight: 1.5}}>
          <div style={{display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 12, ...line(16)}}>
            <span style={{color: C.peach, fontWeight: 700, marginRight: 6}}>Integrantes:</span>
            {NAMES.map(([k, full]) => {
              const f = plan.names[k] ?? 20;
              const v = sp(frame - (f - 3), 14);
              return <span key={k} style={{opacity: 0.25 + 0.75 * v, transform: `scale(${0.92 + 0.08 * v})`,
                background: `rgba(232,99,43,${0.9 * v})`, borderRadius: 30, padding: '1px 13px', display: 'inline-block'}}>{full}</span>;
            })}
          </div>
          <div style={{marginTop: 10, ...line(24)}}><span style={{color: C.peach, fontWeight: 700}}>Profesores:</span> Jaime Eduardo Pinto y Christian Marcelo Yañez</div>
          <div style={{...line(30)}}><span style={{color: C.peach, fontWeight: 700}}>Asignatura:</span> Ecuaciones Diferenciales</div>
        </div>
      </div>
    </div>
  );
};

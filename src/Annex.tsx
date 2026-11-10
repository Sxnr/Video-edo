import React from 'react';
import {plan} from './plan';
import {C, FONT_SANS, FONT_SERIF} from './theme';
import {sp, clamp} from './anim';

const ITEMS = [
  'Se usó Claude (Anthropic) para la corrección y revisión del póster y del informe.',
  'Se usó Claude (Anthropic) como apoyo para generar gráficos y diseñar el póster.',
  'Se usó Claude (Anthropic) para ajustes del video: edición y corte de silencios, animaciones y generación de subtítulos.',
  'El análisis, los datos medidos y las conclusiones son del grupo.',
];

export const Annex: React.FC<{frame: number}> = ({frame}) => {
  const f0 = plan.annexStart;
  const total = plan.durationInFrames;
  const black = clamp((frame - (total - plan.fps)) / plan.fps);
  if (frame < f0 - 10) return null;
  const inn = sp(frame - f0, 30);
  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: `rgba(238,242,244,${0.7 * inn})`}} />
      <div style={{position: 'absolute', left: 210, top: 250, width: 1500, borderRadius: 30, overflow: 'hidden', background: 'white',
        opacity: inn, transform: `perspective(1800px) translateZ(${(1 - inn) * -150}px) rotateX(${(1 - inn) * 8}deg)`,
        boxShadow: '0 30px 80px rgba(10,30,40,0.35)'}}>
        <div style={{background: C.petrol, padding: '26px 40px', display: 'flex', alignItems: 'center', gap: 24}}>
          <div style={{width: 64, height: 64, borderRadius: 32, background: C.orange, border: '4px solid white', color: 'white',
            fontFamily: FONT_SERIF, fontWeight: 700, fontSize: 36, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>A</div>
          <div style={{color: 'white', fontFamily: FONT_SERIF, fontWeight: 700, fontSize: 50}}>ANEXO: USO DE INTELIGENCIA ARTIFICIAL</div>
        </div>
        <div style={{padding: '34px 56px 44px', fontFamily: FONT_SANS, fontSize: 38, lineHeight: 1.35, color: C.text}}>
          {ITEMS.map((t, i) => {
            const k = sp(frame - (f0 + 16 + i * 24), 20);
            const last = i === ITEMS.length - 1;
            return (
              <div key={i} style={{display: 'flex', gap: 20, marginTop: i ? 20 : 0, opacity: k, transform: `translateX(${(1 - k) * 30}px)`,
                background: last ? C.peach : 'transparent', borderRadius: 14, padding: last ? '10px 16px' : '0 16px'}}>
                <span style={{color: C.orange, fontWeight: 700}}>•</span>
                <span style={{fontWeight: last ? 700 : 400}}>{t}</span>
              </div>
            );
          })}
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, background: 'black', opacity: black}} />
    </>
  );
};

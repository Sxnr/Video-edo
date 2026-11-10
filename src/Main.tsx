import React from 'react';
import {AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, delayRender, continueRender} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {plan} from './plan';
import {C, FONT_SANS} from './theme';
import {cameraAt, toScreen} from './camera';
import {liftOf} from './anim';
import {Card} from './Card';
import {Overlays} from './Overlays';
import {Intro} from './Intro';
import {Annex} from './Annex';

const fontHandle = delayRender('fonts');
Promise.all([
  loadFont({family: 'Carlito', url: staticFile('fonts/Carlito-Regular.ttf'), weight: '400'}),
  loadFont({family: 'Carlito', url: staticFile('fonts/Carlito-Bold.ttf'), weight: '700'}),
  loadFont({family: 'Carlito', url: staticFile('fonts/Carlito-Italic.ttf'), weight: '400', style: 'italic'}),
  loadFont({family: 'Caladea', url: staticFile('fonts/Caladea-Bold.ttf'), weight: '700'}),
  loadFont({family: 'Caladea', url: staticFile('fonts/Caladea-Regular.ttf'), weight: '400'}),
]).then(() => continueRender(fontHandle));

const [PW, PH] = plan.posterSize;

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);
  const {s, tx, ty} = toScreen(cam);
  const lifts = plan.sections.map((_, i) => liftOf(i, frame));
  const maxLift = Math.max(0, ...lifts);
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: FONT_SANS, overflow: 'hidden'}}>
      {/* escenario: póster completo, transformado por la cámara */}
      <div style={{position: 'absolute', left: 0, top: 0, width: PW, height: PH, transformOrigin: '0 0',
        transform: `translate(${tx}px, ${ty}px) scale(${s})`}}>
        <Img src={staticFile('poster_base.jpg')} style={{position: 'absolute', width: PW, height: PH}} />
        <Img src={staticFile('poster_blur.jpg')} style={{position: 'absolute', width: PW, height: PH, opacity: maxLift}} />
        <div style={{position: 'absolute', width: PW, height: PH, background: C.bg, opacity: maxLift * 0.62}} />
        {plan.sections.map((sec, i) => lifts[i] > 0.001 ? <Card key={sec.n} sec={sec} lift={lifts[i]} s={s} frame={frame} /> : null)}
      </div>
      <Intro frame={frame} />
      <Overlays frame={frame} />
      <Annex frame={frame} />
      <Audio src={staticFile('mix.wav')} />
    </AbsoluteFill>
  );
};

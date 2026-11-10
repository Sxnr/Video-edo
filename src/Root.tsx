import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import plan from '../public/plan.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="Poster" component={Main} durationInFrames={plan.durationInFrames}
    fps={plan.fps} width={1920} height={1080} />
);

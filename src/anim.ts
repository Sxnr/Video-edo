import {spring} from 'remotion';
import {plan} from './plan';
export const sp = (f: number, dur = 24, damping = 200) =>
  f <= 0 ? 0 : spring({frame: f, fps: plan.fps, config: {damping}, durationInFrames: dur});
/** 0→1 al entrar en f0, 1→0 al salir en f1 */
export const window01 = (frame: number, f0: number, f1: number, inDur = 14, outDur = 12) =>
  Math.max(0, Math.min(1, sp(frame - f0, inDur) - sp(frame - f1, outDur)));
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
/** pulso breve (0→1→0) que empieza en f0 */
export const pulse = (frame: number, f0: number, dur = 16) => {
  const t = (frame - f0) / dur;
  return t <= 0 || t >= 1 ? 0 : Math.sin(Math.PI * t);
};
export const liftOf = (i: number, frame: number) => {
  const S = plan.sections;
  const s = S[i];
  const start = i === 0 ? plan.introEnd + 8 : S[i - 1].end + 22;
  return clamp(sp(frame - start, 26) - sp(frame - (s.end - 2), 16));
};

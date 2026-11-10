"""Plan de render: tiempos en frames, subtítulos, énfasis, pista de voz, PiP y música.
Entradas: parts.json, work/timeline.json (build_edl.py), edl/emphasis.json, work/poster_boxes.json
Salidas (public/): plan.json, mix.wav, pip/s<n>.mp4"""
import json, os, re, subprocess, sys, unicodedata
import numpy as np
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, 'scripts')
from music import make_music
P = json.load(open('parts.json')); T = P['timing']; FPS = T['fps']; SR = 48000; SPF = SR // FPS
parts = {v['id']: v for v in P['videos']}
tl = json.load(open('work/timeline.json'))['clips']
emph = json.load(open('edl/emphasis.json'))
boxes = json.load(open('work/poster_boxes.json'))
os.makedirs('public/pip', exist_ok=True)

def n(x):
    x = unicodedata.normalize('NFKD', x.lower()); return ''.join(c for c in x if c.isalnum())

# --- secciones en frames
sections, clips = [], []
f = round(T['intro_lead'] * FPS)
for s in sorted({c['section'] for c in tl}):
    cs = [c for c in tl if c['section'] == s]
    start = f
    for c in cs:
        d = round((c['src_end'] - c['src_start']) * FPS)
        base = c['out_start']
        words = [dict(w=w['w'], f0=start + (f - start) + round((w['s'] - base) * FPS), f1=start + (f - start) + round((w['e'] - base) * FPS)) for w in c['words']]
        clips.append(dict(section=s, id=c['id'], src0=c['src_start'], frames=d, at=f, words=words))
        f += d
    sections.append(dict(n=s, id=cs[0]['id'], start=start, end=f))
    f += round(T['gap'] * FPS)
f -= round(T['gap'] * FPS)
annex_start = f + round(0.5 * FPS)
total = annex_start + round((T['annex'] + T['fade']) * FPS)

# --- hablantes / PiP / lower-thirds
seen = set()
for sec in sections:
    v = parts[sec['id']]; spk = v['speaker']
    sec['speaker'] = spk; sec['role'] = v['role']
    sec['lowerThird'] = spk not in seen; seen.add(spk)
    sec['pip'] = None if sec['n'] in v.get('noPipSections', []) else v['pip']['kind']
    sec['box'] = boxes['boxes'][str(sec['n'])]

# --- PiP: concatena los mismos tramos (frame-exactos) del video normalizado
def build_pip(sec):
    if not sec['pip']: return
    out = f"public/pip/s{sec['n']}.mp4"
    cs = [c for c in clips if c['section'] == sec['n']]
    key = json.dumps([(c['src0'], c['frames']) for c in cs] + [parts[sec['id']]['pip']])
    if os.path.exists(out + '.key') and open(out + '.key').read() == key and os.path.exists(out): return
    x, y, w, h = parts[sec['id']]['pip']['crop']
    W, H = (640, 800) if sec['pip'] == 'portrait' else (880, 660)
    fc = ''.join(f"[0:v]trim=start_frame={round(c['src0'] * FPS)}:end_frame={round(c['src0'] * FPS) + c['frames']},setpts=PTS-STARTPTS[v{i}];" for i, c in enumerate(cs))
    fc += ''.join(f'[v{i}]' for i in range(len(cs))) + f"concat=n={len(cs)}:v=1:a=0,crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop_duration=1,format=yuv420p[o]"
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', f"work/norm/{sec['id']}.mp4", '-filter_complex', fc, '-map', '[o]',
                    '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-g', '15', '-r', str(FPS), out], check=True)
    open(out + '.key', 'w').write(key)
for sec in sections: build_pip(sec)

# --- voz: muestras exactas por frame + fundido de 25 ms en cada unión (evita clics)
voice = np.zeros(total * SPF, np.float32)
cache = {}
fade = int(0.025 * SR); ramp = np.linspace(0, 1, fade, dtype=np.float32)
for c in clips:
    if c['id'] not in cache:
        raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', f"work/norm/{c['id']}.mp4", '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        cache[c['id']] = np.frombuffer(raw, np.float32)
    a = cache[c['id']][round(c['src0'] * FPS) * SPF: (round(c['src0'] * FPS) + c['frames']) * SPF].copy()
    a[:fade] *= ramp; a[-fade:] *= ramp[::-1]
    voice[c['at'] * SPF: c['at'] * SPF + len(a)] += a

import wave as _w
with _w.open('work/voice.wav', 'wb') as w_:
    w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((np.clip(voice, -1, 1) * 32767).astype('<i2').tobytes())
# envolvente de voz por frame (0..1) para indicador de onda y ducking
rms = np.sqrt((voice.reshape(total, SPF) ** 2).mean(1))
env = np.clip(20 * np.log10(rms + 1e-6) + 50, 0, 40) / 40

# --- música (original, generada) con ducking bajo la voz
if os.path.exists('input/music.mp3'):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', 'input/music.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    music = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    reps = int(np.ceil(len(voice) / len(music))); music = np.tile(music, (reps, 1))[:len(voice)]
    music_src = 'input/music.mp3'
else:
    music = make_music(len(voice) / SR, SR); music_src = 'generada (scripts/music.py)'
music = music / (np.sqrt((music ** 2).mean()) + 1e-9) * 10 ** (-24 / 20)  # RMS -24 dBFS sin voz
speaking = np.convolve((env > 0.35).astype(float), np.ones(9) / 9, 'same') > 0.05
# ganancia por frame: -6 dB al hablar (=> ~-30 dBFS, ~-28 dB bajo la voz), suavizado ataque 0,2 s / liberación 0,8 s
g = np.where(speaking, 10 ** (-6 / 20), 1.0); gs = np.empty_like(g); cur = 1.0
for i, x in enumerate(g):
    k = 1 / (0.2 * FPS) if x < cur else 1 / (0.8 * FPS); cur += (x - cur) * min(1, k * 3); gs[i] = cur
gain = np.repeat(gs, SPF)
t = np.arange(len(voice)) / SR; dur = len(voice) / SR
gain *= np.clip(t / 2.0, 0, 1) * np.clip((dur - t) / 3.0, 0, 1)
mix = music * gain[:, None] + voice[:, None]
mix[-SPF * FPS:] *= np.linspace(1, 0, SPF * FPS)[:, None] ** 0.5  # termina junto al fundido a negro
peak = np.abs(mix).max()
if peak > 0.95: mix *= 0.95 / peak
import wave
with wave.open('public/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())

# --- subtítulos
caps = []
for sec in sections:
    ws = [w for c in clips if c['section'] == sec['n'] for w in c['words']]
    cur = []
    for i, w in enumerate(ws):
        cur.append(w)
        txt = ' '.join(x['w'] for x in cur)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        brk = nxt is None or len(txt) + len(nxt['w']) > 66 or nxt['f0'] - w['f1'] > 0.6 * FPS \
              or (re.search(r'[.?!]$', w['w']) and len(txt) > 22) or (w['f1'] - cur[0]['f0'] > 5.5 * FPS)
        if brk:
            caps.append(dict(section=sec['n'], f0=cur[0]['f0'], f1=w['f1'], words=cur)); cur = []
for a, b in zip(caps, caps[1:]):  # mantener visible hasta el siguiente (máx 0,5 s extra)
    a['f1'] = min(b['f0'], a['f1'] + round(0.5 * FPS)) if b['section'] == a['section'] else min(a['f1'] + 8, b['f0'])
caps[-1]['f1'] += 10

# --- énfasis
cues = []
for c in emph['cues']:
    ws = [w for cl in clips if cl['section'] == c['s'] for w in cl['words']]
    toks = [n(x) for x in c['at'].split() if n(x)]
    hit = next((i for i in range(len(ws) - len(toks) + 1) if all(n(ws[i + k]['w']) == toks[k] for k in range(len(toks)))), None)
    if hit is None: raise SystemExit(f"énfasis: no encuentro {c['at']!r} en sección {c['s']}")
    sec = next(s for s in sections if s['n'] == c['s'])
    f0 = ws[hit]['f0']; f1 = min(f0 + round(c['hold'] * FPS), sec['end'] + 6)
    cue = dict(c, f0=f0, f1=f1); cue.pop('at'); cue.pop('hold')
    if 'item' in c: cue['rect'] = emph['items'][c['item']]
    if c['kind'] == 'sheet': cue['rect'] = emph['sheet'][c['step']]
    cues.append(cue)

# nombres dichos en el saludo (para la intro)
ws = [w for cl in clips if cl['section'] == 1 for w in cl['words']]
names = {}
for nm in ['Adonis', 'Yeny', 'Vicente', 'Francisco', 'Martina']:
    names[nm] = next(w['f0'] for w in ws if n(w['w']) == n(nm))
intro_end = next(w['f1'] for w in ws if n(w['w']) == 'martina') + 24

plan = dict(fps=FPS, durationInFrames=total, posterSize=boxes['size'], header=boxes['boxes']['header'], refs=boxes['boxes']['refs'],
            logo=boxes['items']['Imagen 76'], introEnd=intro_end, names=names, annexStart=annex_start,
            sections=sections, captions=caps, cues=cues, env=[round(float(x), 3) for x in env], music=music_src)
json.dump(plan, open('public/plan.json', 'w'), ensure_ascii=False)
print(f"duración: {total / FPS:.2f} s = {int(total / FPS // 60)}:{total / FPS % 60:05.2f}  ({total} frames)")
for s in sections: print(f"  sección {s['n']}: {(s['end'] - s['start']) / FPS:5.1f} s  [{s['start']/FPS:6.1f} – {s['end']/FPS:6.1f}]  pip={s['pip']}")
print(f"  anexo desde {annex_start / FPS:.1f} s; intro hasta {intro_end / FPS:.1f} s; música: {music_src}")

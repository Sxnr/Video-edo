"""Genera reporte_edicion.md desde parts.json, edl/selection.json y work/timeline.json"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from words import words, find_phrase
from build_edl import fix
parts = {v['id']: v for v in json.load(open('parts.json'))['videos']}
sel = json.load(open('edl/selection.json'))
tl = json.load(open('work/timeline.json'))
cfg = json.load(open('edl/report_notes.json'))
NAMES = {1: 'Introducción y objetivo', 2: 'Marco teórico', 3: 'Metodología', 4: 'Datos y análisis exploratorio',
         5: 'Formulación y resolución', 6: 'Estimación de k y validación', 7: 'Propuesta de mejora', 8: 'Interpretación', 9: 'Conclusión'}
GAP, INTRO_EXTRA, ANNEX, FADE = cfg['gap'], cfg['intro_extra'], cfg['annex'], cfg['fade']
secs = {}
for c in tl['clips']: secs.setdefault(c['section'], []).append(c)
def mmss(x): return f"{int(x // 60)}:{x % 60:04.1f}"
L = ['# Reporte de edición — Video del póster "Enfriamiento de la leche (Ley de Newton)"', '',
     '> Punto de control antes del render. Generado por `scripts/report.py`.', '']
L += cfg['preamble'] + ['']
L += ['## Duración', '', '| # | Sección | Hablante | Fuente | Habla tras cortes |', '|---|---|---|---|---|']
L.append(f"| 0 | Intro (título, integrantes, profesores) | — | generada, sobre el saludo de Adonis | +{INTRO_EXTRA:.1f} s |")
for s in sorted(secs):
    cs = secs[s]; id = cs[0]['id']; d = sum(c['out_end'] - c['out_start'] for c in cs)
    L.append(f"| {s} | {NAMES[s]} | {parts[id]['speaker']} | `{parts[id]['file']}` | {d:.1f} s |")
L.append(f"| 10 | Anexo: uso de IA + fade a negro | — | generada | {ANNEX + FADE:.1f} s |")
speech = tl['speech_duration']; total = speech + GAP * (len(secs) - 1) + INTRO_EXTRA + ANNEX + FADE
L += ['', f"- Habla total: **{speech:.1f} s**; pausas de transición entre secciones: {len(secs)-1} × {GAP} s.",
      f"- **Duración total estimada: {mmss(total)}** (límite 5:00). Velocidad de voz: 1,00× (sin acelerar).", '']
L += ['## Transcripción limpia por sección', '',
      '_Texto tal como queda en el video (Whisper large-v3-turbo + alineación forzada + glosario). `/` = corte de pausa._', '']
for s in sorted(secs):
    cs = secs[s]
    L += [f"### {s}. {NAMES[s]} — {parts[cs[0]['id']]['speaker']} ({mmss(cs[0]['out_start'])}–{mmss(cs[-1]['out_end'])} del tramo de voz)", '',
          ' / '.join(' '.join(w['w'] for w in c['words']) for c in cs), '']
L += ['## Cortes de contenido (lo que no entra)', '', '| Hablante | Desde → hasta (original) | Duración | Texto | Motivo |', '|---|---|---|---|---|']
for id, items in sel['discarded'].items():
    W = words(id)
    for fa, fb, why in items:
        i, _ = find_phrase(W, fa); _, j = find_phrase(W, fb, i)
        txt = fix(id, ' '.join(w['w'] for w in W[i:j + 1]))
        if len(txt) > 140: txt = txt[:70] + ' … ' + txt[-60:]
        L.append(f"| {parts[id]['speaker'].split()[0]} | {mmss(W[i]['s'])} → {mmss(W[j]['e'])} | {W[j]['e'] - W[i]['s']:.1f} s | {txt} | {why} |")
nclips = len(tl['clips'])
L += ['', f"Además se recortaron automáticamente las pausas ≥ 0,35 s dentro de las frases ({nclips} clips en total; margen de 0,12 s a cada lado, crossfade de audio de 30 ms en cada unión). El detalle está en `edl/<hablante>.json`.", '']
L += cfg['sections_after']
open('reporte_edicion.md', 'w').write('\n'.join(L) + '\n')
print('total', mmss(total))

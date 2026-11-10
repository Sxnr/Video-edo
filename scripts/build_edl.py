"""Construye las EDL a partir de edl/selection.json.

selection.json: lista ordenada de bloques {section, id, ranges:[[a,b,"texto/motivo"],...]}.
Para cada rango: se ajustan los bordes al habla real y se recortan las pausas internas
(silencedetect >= 0.35 s) dejando PAD s antes/después de cada frase. Nunca se corta si
el centro de una palabra cae dentro del tramo a eliminar.
Salida: edl/<id>.json (decisiones por hablante) y work/timeline.json (clips en orden,
con palabras remapeadas al tiempo de salida para subtítulos/énfasis).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from words import words, silences, find_phrase

PAD, MIN_SIL = 0.12, 0.35
FPS = 30
GAP_BETWEEN_SECTIONS = 0.0  # la transición visual se monta sobre el audio, no agrega silencio
CORR = json.load(open('edl/corrections.json')) if os.path.exists('edl/corrections.json') else {}

import re
def fix(id, txt):
    # correcciones por palabra completa (conserva la puntuación)
    for a, b in CORR.get('_all', []) + CORR.get(id, []):
        txt = re.sub(r'(?<![\w])' + re.escape(a) + r'(?![\w])', b, txt)
    return txt

def speech_pieces(id, a, b, W, S):
    """Sub-rangos de [a,b] sin pausas internas. Se recorta cada tramo silencioso (detector de energía,
    >= MIN_SIL) que quede entre dos palabras alineadas, dejando PAD a cada lado. La voz (incluida la
    que Whisper no transcribió) nunca se corta, y nunca se corta dentro de una palabra."""
    ws = [w for w in W if w['e'] > a and w['s'] < b]
    cuts = []
    for w0, w1 in zip(ws, ws[1:]):
        g0, g1 = w0['e'], w1['s']
        if g1 - g0 < MIN_SIL: continue
        for s_, e in S:
            cs, ce = max(s_, g0), min(e, g1)
            if ce - cs >= MIN_SIL:
                cuts.append((cs + PAD, ce - PAD))
    pieces, cur = [], a
    for cs, ce in sorted(cuts):
        if cs > cur: pieces.append([cur, cs])
        cur = max(cur, ce)
    if cur < b: pieces.append([cur, b])
    return [p for p in pieces if p[1] - p[0] > 0.05]

def main():
    sel = json.load(open('edl/selection.json'))
    parts = {v['id']: v for v in json.load(open('parts.json'))['videos']}
    cache, cursor = {}, {}
    timeline, per = [], {}
    t = 0.0
    for blk in sel['blocks']:
        id = blk['id']
        if id not in cache: cache[id] = (words(id), silences(id))
        W, S = cache[id]
        cur = cursor.get(id, 0)
        for fa, fb, note in blk['ranges']:
            i, _ = find_phrase(W, fa, cur)
            _, j = find_phrase(W, fb, i)
            cur = j + 1
            a = W[i]['s'] - PAD
            if i > 0: a = max(a, (W[i-1]['e'] + W[i]['s']) / 2)
            b = W[j]['e'] + PAD
            if j + 1 < len(W): b = min(b, (W[j]['e'] + W[j+1]['s']) / 2)
            for pa, pb in speech_pieces(id, a, b, W, S):
                # cuantiza a frames (30 fps) para que audio y video del PiP queden en sincronía exacta
                pa, pb = round(pa * FPS) / FPS, round(pb * FPS) / FPS
                if pb - pa < 2 / FPS: continue
                ws = [dict(w=fix(id, w['w']), s=round(max(w['s'], pa) - pa + t, 3), e=round(min(w['e'], pb) - pa + t, 3))
                      for w in W if pa <= (w['s'] + w['e']) / 2 <= pb]
                clip = dict(section=blk['section'], id=id, src_start=round(pa, 3), src_end=round(pb, 3),
                            out_start=round(t, 3), out_end=round(t + pb - pa, 3), words=ws)
                timeline.append(clip)
                per.setdefault(id, []).append(dict(inicio=round(pa, 3), fin=round(pb, 3), seccion=blk['section'],
                                                    motivo=note, texto=' '.join(w['w'] for w in ws)))
                t += pb - pa
        cursor[id] = cur
        t += GAP_BETWEEN_SECTIONS
    for id, clips in per.items():
        json.dump(dict(hablante=parts[id]['speaker'], archivo=parts[id]['file'], clips=clips,
                       descartado=sel.get('discarded', {}).get(id, [])),
                  open(f'edl/{id}.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(dict(speech_duration=round(t, 3), clips=timeline), open('work/timeline.json', 'w'), ensure_ascii=False)
    secs = {}
    for c in timeline: secs[c['section']] = secs.get(c['section'], 0) + c['out_end'] - c['out_start']
    for s in sorted(secs): print(f'sección {s}: {secs[s]:6.1f} s')
    print(f'habla total: {t:.1f} s  ({len(timeline)} clips)')

if __name__ == '__main__':
    main()

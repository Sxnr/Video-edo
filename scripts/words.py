"""Utilidades: palabras con timestamps desde el JSON de whisper.cpp y silencios de silencedetect."""
import json, re

def words(id):
    import os
    if os.path.exists(f'work/transcripts/{id}.aligned.json'):
        return refine_onsets(id, json.load(open(f'work/transcripts/{id}.aligned.json')))
    return whisper_words(id)

_rms = {}
def _energy(id):
    if id not in _rms:
        import wave, numpy as np
        w = wave.open(f'work/wav/{id}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
        f = 160; n = len(x) // f
        _rms[id] = 20 * np.log10(np.sqrt((x[:n * f].reshape(n, f) ** 2).mean(1)) + 1e-9)
    return _rms[id]

def refine_onsets(id, W):
    """Si el alineador ubicó el inicio de una palabra tarde, justo después de una pausa, y entre el fin de
    la pausa y ese inicio hay energía de voz (no respiración), adelanta el inicio al fin de la pausa."""
    import os, numpy as np
    sp = f'work/silence/{id}.json'
    if not os.path.exists(sp): return W
    S = json.load(open(sp)); thr = S['thr']; r = _energy(id)
    for a, b in S['pauses']:
        for i, w in enumerate(W):
            if not (0.08 < w['s'] - b < 0.7): continue
            if i > 0 and W[i - 1]['e'] > a + 0.1: continue
            seg = r[int(b * 100):int(w['s'] * 100)]
            if len(seg) and np.median(seg) > thr + 8:
                w['s'] = round(b + 0.02, 3)
            break
    return W

def whisper_words(id):
    d = json.load(open(f'work/transcripts/{id}.json'))
    out = []
    for seg in d['transcription']:
        for t in seg['tokens']:
            txt = t['text']
            if txt.startswith('[_') or txt.startswith('[') and txt.endswith(']'):
                continue
            a, b = t['offsets']['from'] / 1000, t['offsets']['to'] / 1000
            if txt.startswith(' ') or not out:
                out.append({'w': txt.strip(), 's': a, 'e': b})
            else:
                out[-1]['w'] += txt
                out[-1]['e'] = max(out[-1]['e'], b)
    return [w for w in out if w['w']]

def silences(id):
    import os
    if os.path.exists(f'work/silence/{id}.json'):
        return [tuple(x) for x in json.load(open(f'work/silence/{id}.json'))['pauses']]
    s, res = None, []
    for line in open(f'work/silence/{id}.txt'):
        m = re.search(r'silence_start: ([\d.]+)', line)
        if m: s = float(m.group(1))
        m = re.search(r'silence_end: ([\d.]+)', line)
        if m and s is not None: res.append((s, float(m.group(1)))); s = None
    return res

import unicodedata
def _n(x):
    x = unicodedata.normalize('NFKD', x.lower())
    return ''.join(c for c in x if c.isalnum())

def find_phrase(W, phrase, start=0):
    """índice de la primera palabra de `phrase` en W a partir de `start` (comparación sin tildes/puntuación)"""
    toks = [_n(t) for t in phrase.split() if _n(t)]
    for i in range(start, len(W) - len(toks) + 1):
        if all(_n(W[i + k]['w']) == toks[k] for k in range(len(toks))):
            return i, i + len(toks) - 1
    raise ValueError(f'no se encontró la frase: {phrase!r} desde {start}')

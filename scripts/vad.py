"""Detección de pausas por energía (complementa silencedetect): marca como pausa todo tramo
>= 0.35 s cuyo RMS (ventanas de 10 ms) esté bajo el umbral adaptativo; respiraciones y
ruido de fondo quedan como pausa, la voz no. Salida: work/silence/<id>.json"""
import json, sys, wave, numpy as np
MIN = 0.35
for id in [v['id'] for v in json.load(open('parts.json'))['videos']]:
    w = wave.open(f'work/wav/{id}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    f = 160; n = len(x) // f
    r = 20 * np.log10(np.sqrt((x[:n*f].reshape(n, f) ** 2).mean(1)) + 1e-9)
    r = np.convolve(r, np.ones(3) / 3, 'same')
    p10, p50 = np.percentile(r, 10), np.percentile(r, 50)
    thr = max(-35, (p10 + p50) / 2) + 3
    sp = r > thr
    # rellena huecos de voz < 120 ms (oclusivas) y elimina ráfagas < 80 ms (clics)
    def runs(a):
        out, i = [], 0
        while i < len(a):
            j = i
            while j < len(a) and a[j] == a[i]: j += 1
            out.append((a[i], i, j)); i = j
        return out
    for v, i, j in runs(sp):
        if not v and j - i < 12 and i > 0: sp[i:j] = True
    for v, i, j in runs(sp):
        if v and j - i < 8: sp[i:j] = False
    pauses = [(round(i * 0.01, 2), round(j * 0.01, 2)) for v, i, j in runs(sp) if not v and (j - i) * 0.01 >= MIN]
    json.dump(dict(thr=round(float(thr), 1), pauses=pauses), open(f'work/silence/{id}.json', 'w'))
    print(id, 'umbral', round(float(thr), 1), 'dB, pausas', len(pauses), 'total', round(sum(b - a for a, b in pauses), 1), 's')

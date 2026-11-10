"""Música de fondo original generada por síntesis (sin derechos de terceros):
pad ambiental en Fa mayor, ~72 bpm, progresión I–vi–IV–V con arpegio tenue y bajo suave."""
import numpy as np

def _note(m): return 440.0 * 2 ** ((m - 69) / 12)

def make_music(dur, sr=48000, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * sr) + sr
    out = np.zeros((n, 2), np.float32)
    bpm = 72; beat = 60 / bpm; bar = 4 * beat; chord_len = 2 * bar
    # Fmaj9, Dm9, Bbmaj9, Csus2 (MIDI)
    prog = [[53, 57, 60, 64, 67], [50, 57, 60, 64, 65], [46, 53, 57, 62, 65], [48, 55, 60, 62, 67]]
    t_all = np.arange(n) / sr
    # pad: armónicos suaves con leve desafinación, ataque/relajo largos (crossfade entre acordes)
    for ci in range(int(dur / chord_len) + 2):
        t0 = ci * chord_len; ch = prog[ci % 4]
        a, b = int(max(0, t0 - 1.5) * sr), int(min(n / sr, t0 + chord_len + 2.0) * sr)
        if a >= n: break
        t = t_all[a:b] - t0
        env = np.clip((t + 1.5) / 2.5, 0, 1) * np.clip((chord_len + 2.0 - t) / 2.5, 0, 1)
        env = env ** 1.5
        for k, m in enumerate(ch[1:]):
            for det, pan in [(-0.08, 0.3), (0.08, 0.7)]:
                fr = _note(m + 12 * (k == 3)) * 2 ** (det / 12)
                ph = rng.uniform(0, 2 * np.pi)
                s = np.sin(2 * np.pi * fr * t + ph) + 0.25 * np.sin(4 * np.pi * fr * t + ph) + 0.08 * np.sin(6 * np.pi * fr * t)
                trem = 1 + 0.08 * np.sin(2 * np.pi * 0.15 * t + ph)
                out[a:b, 0] += (s * env * trem * (1 - pan) * 0.10).astype(np.float32)
                out[a:b, 1] += (s * env * trem * pan * 0.10).astype(np.float32)
        # bajo: raíz, una vez por compás
        for bi in range(2):
            tb = t0 + bi * bar; ia = int(tb * sr); ib = min(n, ia + int(bar * sr))
            if ia >= n: break
            tt = t_all[ia:ib] - tb
            s = np.sin(2 * np.pi * _note(ch[0] - 12) * tt) * np.exp(-tt / 1.8) * np.clip(tt / 0.05, 0, 1)
            out[ia:ib] += (s * 0.22)[:, None].astype(np.float32)
    # arpegio tipo campana, corcheas espaciadas, desde los 6 s
    pattern = [0, 2, 1, 3, 2, 4, 3, 1]
    step = beat
    for si in range(int(dur / step)):
        ts = si * step
        if ts < 6: continue
        ch = prog[int(ts // chord_len) % 4]
        if si % 8 in (5, 7): continue
        m = ch[1:][pattern[si % 8] % 4] + 12
        ia = int(ts * sr); ib = min(n, ia + int(1.6 * sr))
        tt = t_all[ia:ib] - ts
        fr = _note(m)
        s = (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(2 * np.pi * 2.01 * fr * tt) * np.exp(-tt / 0.25)) * np.exp(-tt / 0.55) * np.clip(tt / 0.01, 0, 1)
        pan = 0.35 + 0.3 * ((si * 3) % 5) / 4
        out[ia:ib, 0] += (s * 0.05 * (1 - pan)).astype(np.float32)
        out[ia:ib, 1] += (s * 0.05 * pan).astype(np.float32)
    # reverb: convolución con cola de ruido decreciente (FFT)
    L = int(2.8 * sr); tt = np.arange(L) / sr
    wet = np.zeros_like(out)
    for c in range(2):
        ir = rng.standard_normal(L) * np.exp(-tt / 0.9); ir[0] = 0; ir /= np.sqrt((ir ** 2).sum())
        N = 1 << int(np.ceil(np.log2(n + L)))
        wet[:, c] = np.fft.irfft(np.fft.rfft(out[:, c], N) * np.fft.rfft(ir, N), N)[:n]
    y = 0.6 * out + 0.55 * wet
    # pasa-bajos suave (1 polo, ~3,5 kHz)
    a = np.exp(-2 * np.pi * 3500 / sr)
    from scipy.signal import lfilter
    y = lfilter([1 - a], [1, -a], y, axis=0)
    return y[:int(dur * sr)].astype(np.float32)

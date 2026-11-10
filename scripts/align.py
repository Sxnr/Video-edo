"""Alineación forzada (torchaudio MMS_FA) del texto de Whisper para obtener tiempos por palabra
precisos (~20 ms). Entrada: work/transcripts/<id>.json + work/wav/<id>.wav
Salida: work/transcripts/<id>.aligned.json  [{w, s, e, score}]"""
import json, sys, re, unicodedata, os
import wave, numpy as np
import torch, torchaudio, torchaudio.functional as F
from num2words import num2words
torch.set_num_threads(4)
B = torchaudio.pipelines.MMS_FA
model = B.get_model(with_star=True).eval()
DICT = B.get_dict(star='*')
SR = B.sample_rate
MARGIN = 1.5

def norm_word(w):
    """palabra original -> lista de 'palabras' romanizadas para el alineador"""
    w = w.replace('°C', ' grados').replace('ºC', ' grados').replace('%', ' por ciento').replace('²', ' cuadrado')
    out = []
    for p in re.findall(r"\d+(?:[.,]\d+)?|[^\W\d_]+", w):
        if p[0].isdigit():
            if re.search(r'[.,]', p):
                a, b = re.split(r'[.,]', p)
                out += num2words(int(a), lang='es').split() + ['coma'] + num2words(int(b), lang='es').split() if not b.startswith('0') else num2words(int(a), lang='es').split() + ['coma'] + ['cero'] * (len(b) - len(b.lstrip('0'))) + (num2words(int(b), lang='es').split() if b.strip('0') else [])
            else:
                out += num2words(int(p), lang='es').split()
        else:
            out.append(p)
    res = []
    for p in out:
        s = unicodedata.normalize('NFKD', p.lower())
        s = ''.join(c for c in s if c in DICT and c not in '-*')
        if s: res.append(s)
    return res

def main(ids):
    sys.path.insert(0, os.path.dirname(__file__))
    for id in ids:
        wf = wave.open(f'work/wav/{id}.wav'); assert wf.getframerate() == SR
        wav = torch.from_numpy(np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768).unsqueeze(0)
        d = json.load(open(f'work/transcripts/{id}.json'))
        res = []
        segs = d['transcription']
        for si, seg in enumerate(segs):
            # palabras del segmento
            ws = []
            for t in seg['tokens']:
                tx = t['text']
                if tx.startswith('['): continue
                if tx.startswith(' ') or not ws: ws.append(tx.strip())
                else: ws[-1] += tx
            ws = [w for w in ws if w]
            if not ws: continue
            a = max(0, seg['offsets']['from'] / 1000 - MARGIN)
            b = min(wav.shape[1] / SR, seg['offsets']['to'] / 1000 + MARGIN)
            # no invadir palabras ya alineadas del segmento anterior
            if res: a = max(a, res[-1]['e'])
            chunk = wav[:, int(a * SR):int(b * SR)]
            nw = [norm_word(w) for w in ws]
            flat = [x for n in nw for x in n]
            if not flat or chunk.shape[1] < SR * 0.2: continue
            with torch.inference_mode():
                em, _ = model(chunk)
            tokens = [DICT['*']] + [DICT[c] for x in flat for c in x] + [DICT['*']]
            # star entre palabras no; star al inicio y final absorbe habla de segmentos vecinos
            try:
                ali, scores = F.forced_align(em, torch.tensor([tokens], dtype=torch.int32), blank=0)
            except Exception as ex:
                print('fallo', id, si, ex); continue
            spans = F.merge_tokens(ali[0], scores[0].exp())
            ratio = chunk.shape[1] / em.shape[1] / SR
            spans = spans[1:-1] if len(spans) >= 2 else spans  # quita los '*'
            # agrupar spans por palabra normalizada
            k = 0; wspans = []
            for x in flat:
                wspans.append(spans[k:k + len(x)]); k += len(x)
            j = 0
            for w, n in zip(ws, nw):
                sp = [s for q in wspans[j:j + len(n)] for s in q]; j += len(n)
                if not sp:
                    continue
                s0 = a + sp[0].start * ratio; e0 = a + sp[-1].end * ratio
                sc = sum(s.score for s in sp) / len(sp)
                res.append(dict(w=w, s=round(s0, 3), e=round(e0, 3), score=round(float(sc), 3)))
        json.dump(res, open(f'work/transcripts/{id}.aligned.json', 'w'), ensure_ascii=False)
        print('alineado', id, len(res), 'palabras')

if __name__ == '__main__':
    main(sys.argv[1:] or [v['id'] for v in json.load(open('parts.json'))['videos']])

#!/usr/bin/env bash
# silencedetect con umbral adaptativo: max(-35 dB, punto medio entre p10 y p50 del RMS) — para pistas con piso de ruido alto.
set -e
cd "$(dirname "$0")/.."
mkdir -p work/silence
for id in $(python3 -c "import json;[print(v['id']) for v in json.load(open('parts.json'))['videos']]"); do
  thr=$(python3 -c "
import numpy as np, wave
w=wave.open('work/wav/$id.wav'); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768
f=320; n=len(x)//f; r=20*np.log10(np.sqrt((x[:n*f].reshape(n,f)**2).mean(1))+1e-9)
print(round(max(-35,(np.percentile(r,10)+np.percentile(r,50))/2),1))")
  ffmpeg -nostdin -nostats -i work/wav/$id.wav -af silencedetect=noise=${thr}dB:d=0.35 -f null - 2>&1 | { grep -E "silence_(start|end)" || true; } > work/silence/$id.txt
  echo "$id thr=${thr}dB silences=$(grep -c start work/silence/$id.txt || true)"
done

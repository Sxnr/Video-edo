#!/usr/bin/env bash
# Paso 1: normaliza cada video de parts.json -> work/norm/<id>.mp4 (1920x1080, 30fps CFR, H.264, AAC 48k mono, -16 LUFS)
# y work/wav/<id>.wav (16 kHz mono, para Whisper/silencedetect).
set -e
cd "$(dirname "$0")/.."
mkdir -p work/norm work/wav
python3 -c "import json;[print(v['id'],v['file']) for v in json.load(open('parts.json'))['videos']]" | while read id file; do
  out=work/norm/$id.mp4
  [ -f "$out" ] && [ "$out" -nt "input/$file" ] && [ -z "$FORCE" ] && { echo "skip $id"; continue; }
  # video: fit 1920x1080 sin deformar; fondo desenfocado para material vertical
  VF="[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.15[bg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
  AF="highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"
  ffmpeg -nostdin -v error -y -i "input/$file" -filter_complex "$VF" -map "[v]" -map 0:a:0 -af "$AF" -ac 1 \
    -c:v libx264 -preset veryfast -crf 18 -g 30 -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$out"
  ffmpeg -nostdin -v error -y -i "$out" -vn -ac 1 -ar 16000 -c:a pcm_s16le work/wav/$id.wav
  echo "norm $id"
done

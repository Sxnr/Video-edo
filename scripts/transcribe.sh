#!/usr/bin/env bash
# Transcribe work/wav/<id>.wav -> work/transcripts/<id>.json (whisper.cpp, token timestamps + DTW)
set -e
cd "$(dirname "$0")/.."
MODEL=${WHISPER_MODEL:-large-v3-turbo}
BIN=whisper.cpp/build/bin/whisper-cli
PROMPT="Ley de Enfriamiento de Newton, EDO, ecuación diferencial de primer orden, factor integrante, temperatura ambiente, constante de enfriamiento k, RMSE, R², regresión, residuos, 78,1 °C, 51,4 °C, 22,1 °C, 0,0239, 0,0213, 0,998, Alexa, Zill, Boyce, DiPrima, Çengel."
mkdir -p work/transcripts
for id in "$@"; do
  out=work/transcripts/$id
  [ -f "$out.json" ] && [ -z "$FORCE" ] && { echo "skip $id"; continue; }
  $BIN -m whisper.cpp/ggml-$MODEL.bin -f work/wav/$id.wav -l es -t 4 \
    --prompt "$PROMPT" -ojf -of "$out" --dtw ${MODEL//-/.} -np
  echo "done $id"
done

#!/usr/bin/env bash
# Versión de entrega < 95 MB: H.264 dos pasadas + AAC 128 kbps
set -e
cd "$(dirname "$0")/.."
IN=out/video_poster_final.mp4; OUT=out/video_poster_entrega.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
VB=$(python3 -c "print(int((88e6*8/$DUR - 128000)/1000))")   # kbps: ~88 MB, margen bajo 95 MB
echo "duración ${DUR}s -> video ${VB}k"
cd out
ffmpeg -nostdin -v error -y -i ../$IN -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile ffpass -an -f mp4 /dev/null
ffmpeg -nostdin -v error -y -i ../$IN -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile ffpass -c:a aac -b:a 128k -movflags +faststart ../$OUT
rm -f ffpass*
cd ..
ls -la $OUT

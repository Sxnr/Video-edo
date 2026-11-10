# Video del póster — Enfriamiento de la leche (Ley de Newton)

Pipeline reproducible (Remotion + ffmpeg + whisper.cpp) que arma el video de presentación del póster
a partir de las grabaciones de cada integrante.

```bash
npm install
node scripts/install-whisper.mjs      # whisper.cpp + modelo large-v3-turbo (una vez)
pip install gdown torch torchaudio num2words scipy pillow numpy   # (torch: índice CPU)
npm run build-all                     # descargar → normalizar → transcribir → EDL → preparar → render → entrega
```

| Paso | Script | Qué hace |
|---|---|---|
| download | `scripts/download.py` | Baja de Drive lo que falte según `parts.json`; si cambió el ID de un video, borra solo sus derivados |
| normalize | `scripts/normalize.sh` | 1920×1080, 30 fps CFR, AAC 48 kHz mono, −16 LUFS |
| transcribe | `scripts/transcribe.sh`, `align.py`, `vad.py` | Whisper `large-v3-turbo` + alineación forzada (MMS_FA) + detección de pausas |
| edl | `scripts/build_edl.py`, `report.py` | Aplica `edl/selection.json` (frases de inicio/fin), recorta pausas → `edl/<id>.json`, `reporte_edicion.md` |
| prepare | `scripts/poster.py`, `assets.py`, `plan.py` | Póster PPTX→PNG 300 dpi y recuadros; recursos; plan de frames, voz + música, PiP |
| render | Remotion (`src/`) | `out/video_poster_final.mp4` (H.264 CRF 18) |
| deliver | `scripts/deliver.sh` | `out/video_poster_entrega.mp4` < 95 MB (dos pasadas) |

**Si alguien vuelve a grabar su parte:** cambia su `driveId` (y `file`) en `parts.json`, revisa en
`edl/selection.json` las frases de inicio/fin de sus tramos, y corre `npm run build-all`.
Énfasis visuales sincronizados con la voz: `edl/emphasis.json`. Correcciones del glosario: `edl/corrections.json`.
Música: si existe `input/music.mp3` se usa esa; si no, `scripts/music.py` genera una pista original.

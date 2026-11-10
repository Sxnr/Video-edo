"""Descarga desde Drive lo que falte según parts.json y verifica cada archivo.
Si cambió el ID de Drive de un video (alguien volvió a grabar), borra solo sus derivados
para que el pipeline rehaga esa parte."""
import json, os, subprocess, sys, shutil
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
P = json.load(open('parts.json'))
os.makedirs('input', exist_ok=True); os.makedirs('work', exist_ok=True)
state_f = 'work/drive_ids.json'
state = json.load(open(state_f)) if os.path.exists(state_f) else {}

def get(drive_id, dest):
    tmp = dest + '.part'
    r = subprocess.run([sys.executable, '-m', 'gdown', drive_id, '-O', tmp, '-q'])
    if r.returncode or not os.path.exists(tmp):
        raise SystemExit(f'ERROR: no se pudo descargar {dest} (ID {drive_id}). ¿Está compartido como "cualquiera con el enlace"?')
    os.replace(tmp, dest)

def is_video(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return 'video' in r.stdout

failed = []
for v in P['videos']:
    dest = f"input/{v['file']}"
    if state.get(v['id']) not in (None, v['driveId']):
        print(f"{v['id']}: cambió el ID de Drive -> se rehace su parte")
        for p in [f"work/norm/{v['id']}.mp4", f"work/wav/{v['id']}.wav", f"work/silence/{v['id']}.json", f"work/silence/{v['id']}.txt"] + \
                 [f"work/transcripts/{v['id']}{x}" for x in ('.json', '.aligned.json', '.words.txt')]:
            if os.path.exists(p): os.remove(p)
        if os.path.exists(dest): os.remove(dest)
    if not os.path.exists(dest):
        print('descargando', v['file']); get(v['driveId'], dest)
    if not is_video(dest):
        failed.append(v['file']); continue
    state[v['id']] = v['driveId']
for extra in P.get('support', []) + [P['poster']]:
    dest = f"input/{extra['file']}"
    if not os.path.exists(dest):
        print('descargando', extra['file']); get(extra['driveId'], dest)
    if os.path.getsize(dest) < 20000: failed.append(extra['file'])
json.dump(state, open(state_f, 'w'), indent=1)
if failed:
    raise SystemExit('ERROR: estos archivos no son válidos (probablemente página de permiso de Drive): ' + ', '.join(failed))
print('descargas OK')

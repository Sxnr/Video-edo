"""Póster: input/poster.pptx -> poster.pdf -> poster.png (300 dpi) y work/poster_boxes.json
con los rectángulos de cada sección leídos directo del PPTX (en px del PNG, con margen)."""
import json, re, subprocess, zipfile, os
from PIL import Image
DPI, MARGIN_PT = 300, 1.5
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
if not os.path.exists('input/poster.pdf') or os.path.getmtime('input/poster.pdf') < os.path.getmtime('input/poster.pptx'):
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', 'input', 'input/poster.pptx'], check=True, capture_output=True)
if not os.path.exists('input/poster.png') or os.path.getmtime('input/poster.png') < os.path.getmtime('input/poster.pdf'):
    subprocess.run(['pdftoppm', '-png', '-r', str(DPI), '-singlefile', 'input/poster.pdf', 'input/poster'], check=True)
z = zipfile.ZipFile('input/poster.pptx'); x = z.read('ppt/slides/slide1.xml').decode()
shapes = []
for m in re.finditer(r'<p:(sp|pic|graphicFrame)>.*?</p:\1>', x, re.S):
    b = m.group(0)
    o = re.search(r'<a:off x="(\d+)" y="(\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', b)
    if not o: continue
    shapes.append(dict(kind=m.group(1), name=re.search(r'name="([^"]*)"', b).group(1),
                       r=[int(v) / 12700 for v in o.groups()], text=''.join(re.findall(r'<a:t>([^<]*)</a:t>', b))))
f = DPI / 72
W, H = Image.open('input/poster.png').size
def px(r, m=MARGIN_PT):
    x, y, w, h = r
    return [round((x - m) * f), round((y - m) * f), round((w + 2 * m) * f), round((h + 2 * m) * f)]
boxes = {'header': px(shapes[0]['r'])}
# cada sección = el rectángulo de fondo inmediatamente anterior a su barra de título con el número
for i, s in enumerate(shapes):
    if s['kind'] == 'sp' and re.fullmatch(r'[1-9]', s['text'].strip()):
        bg = shapes[i - 3]['r']  # fondo, barra, círculo, número
        boxes[s['text'].strip()] = px(bg)
refs = [s for s in shapes if s['text'].startswith('Referencias')][0]
boxes['refs'] = px(refs['r'])
# elementos internos útiles para énfasis (px del PNG, sin margen)
items = {}
for s in shapes:
    t = s['text']
    if s['kind'] == 'pic': items[s['name']] = px(s['r'], 0)
    if s['kind'] == 'graphicFrame': items[s['name']] = px(s['r'], 0)
    for key in ['47 min', '17 min', '22,1 °C']:
        if t.strip() == key: items['card ' + key] = px(shapes[shapes.index(s) - 1]['r'], 0)
json.dump(dict(size=[W, H], boxes=boxes, items=items), open('work/poster_boxes.json', 'w'), indent=1, ensure_ascii=False)
print(W, H); print(json.dumps(boxes)); print(json.dumps(items))

"""Recursos gráficos para Remotion (public/): recortes de recuadros, póster base/desenfocado, logo, hoja, fuentes."""
import json, os, shutil
from PIL import Image, ImageFilter, ImageEnhance
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
os.makedirs('public/boxes', exist_ok=True); os.makedirs('public/fonts', exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
d = json.load(open('work/poster_boxes.json'))
im = Image.open('input/poster.png').convert('RGB')
W, H = im.size
for k, (x, y, w, h) in d['boxes'].items():
    im.crop((x, y, x + w, y + h)).save(f'public/boxes/{k}.png', optimize=True)
base = im.resize((W // 2, H // 2), Image.LANCZOS)
base.save('public/poster_base.jpg', quality=92)
base.resize((W // 4, H // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6)).save('public/poster_blur.jpg', quality=88)
x, y, w, h = d['items']['Imagen 76']
im.crop((x, y, x + w, y + h)).save('public/logo.png')
# hoja de procedimiento: tinta clara sobre fondo oscuro -> realce suave, x2 Lanczos, unsharp leve
s = Image.open('input/procedimiento_edo.png').convert('RGB')
s = s.resize((s.width * 2, s.height * 2), Image.LANCZOS)
s = ImageEnhance.Contrast(s).enhance(1.15)
s = ImageEnhance.Color(s).enhance(1.1)
s = s.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
s.save('public/sheet.png', optimize=True)
for f in ['Carlito-Regular', 'Carlito-Bold', 'Carlito-Italic', 'Caladea-Bold', 'Caladea-Regular']:
    shutil.copy(f'/usr/share/fonts/truetype/crosextra/{f}.ttf', f'public/fonts/{f}.ttf')
print('ok', W, H)

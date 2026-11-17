"""Clothing photos (exported from Figma, images 60–69) → web images.
Crops remove third-party labels and the screen-photo UI; a light common grade (black point, contrast) makes them
sit together; output webp into ../assets/img. Detail crops feed the 'how it's made' section."""
import os
from PIL import Image, ImageEnhance, ImageOps
OUT = '../assets/img'; os.makedirs(OUT, exist_ok=True)
# id: (source, crop box or None)
P = {
 '01': ('p62', (92, 12, 622, 718)),     # sprayed grey blazer — inside the screen photo's arrows/border
 '02': ('p60', None),                    # red-laced back
 '03': ('p64', None),                    # spine stitch
 '04': ('p61', (40, 0, 420, 500)),       # raw-edge cream — label cut away
 '05': ('p63', None),                    # post-it coat
 '06': ('p65', (0, 300, 372, 795)),      # red beads — maker's label cut away
 '07': ('p66', None),                    # red cross-stitch herringbone
 '08': ('p67', None),                    # hooked trousers
 '09': ('p68', None),                    # tied back
 '10': ('p69', None),                    # leather net shirt
}
def grade(im):
    im = ImageOps.autocontrast(im, cutoff=.4, preserve_tone=True)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageEnhance.Color(im).enhance(.92)
for k, (src, box) in P.items():
    im = Image.open(f'pieces/{src}.png').convert('RGB')
    if box: im = im.crop(box)
    im = grade(im)
    # gentle 1.5x upscale so cards stay crisp-ish on retina (sources are 360–740 px)
    im = im.resize((round(im.width * 1.5), round(im.height * 1.5)), Image.LANCZOS)
    im.save(f'{OUT}/piece-{k}.webp', 'WEBP', quality=82, method=6)
    print(k, im.size, os.path.getsize(f'{OUT}/piece-{k}.webp') // 1024, 'KB')
# macro details for the process steps (found / ripped / reworn)
D = {'found': ('p66', (110, 50, 300, 240)), 'ripped': ('p64', (160, 90, 330, 380)), 'reworn': ('p62', (430, 220, 700, 490))}
for k, (src, box) in D.items():
    im = grade(Image.open(f'pieces/{src}.png').convert('RGB').crop(box))
    im = im.resize((720, round(720 * im.height / im.width)), Image.LANCZOS)
    im.save(f'{OUT}/detail-{k}.webp', 'WEBP', quality=80, method=6); print(k, im.size)

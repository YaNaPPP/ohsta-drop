import sys, numpy as np, cv2
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
rgb = np.array(Image.open(src).convert('RGB'))
H, W = rgb.shape[:2]
bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
mn = rgb.min(axis=2).astype(int)

def box(x0, y0, x1, y1):
    m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True; return m

# ---- 1. baked UI text (white) ----
text_boxes = [
    (40, 30, 215, 105),     # OH logo
    (345, 40, 700, 155),    # tagline
    (40, 435, 1885, 645),   # INCOMING
    (40, 665, 860, 735),    # date
    (40, 1000, 160, 1045), (345, 985, 580, 1045), (960, 985, 1120, 1045), (1820, 1000, 1880, 1045),
]
region = np.zeros((H, W), bool)
for b in text_boxes: region |= box(*b)
white = (mn > 232) & region

# blob (saturated pure blue) + spray ring around it
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
blob = (rgb[..., 2] > 200) & (rgb[..., 0] < 90) & (rgb[..., 1] < 110) & box(655, 430, 940, 650)
yy, xx = np.mgrid[0:H, 0:W]
ring_zone = (((xx - 800) / 250.0) ** 2 + ((yy - 545) / 95.0) ** 2) < 1.0
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(int)
med = cv2.medianBlur(gray.astype(np.uint8), 21).astype(int)
ring_zone = (((xx - 800) / 275.0) ** 2 + ((yy - 545) / 110.0) ** 2) < 1.0
ring = ring_zone & ((gray - med) > 7)

ui = white | blob | ring
ui = cv2.dilate(ui.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
# blob fully: fill its convex area
blob_fill = cv2.morphologyEx(blob.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
ui |= cv2.dilate(blob_fill, np.ones((25, 25), np.uint8)) > 0

no_text = cv2.inpaint(bgr, ui.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)

# ---- 2. graffiti mask on the text-free image ----
hsv2 = cv2.cvtColor(no_text, cv2.COLOR_BGR2HSV).astype(float)
h, s, v = hsv2[..., 0], hsv2[..., 1], hsv2[..., 2]
blue = (h > 92) & (h < 128) & (v > 30)
alpha = np.clip((s - 115) / 75.0, 0, 1) * blue
zone = ((xx < 1185) | ((xx < 1240) & (yy > 520))) & (yy > 18) & (yy < 925)
alpha *= zone
alpha = cv2.GaussianBlur(alpha.astype(np.float32), (3, 3), 0)
alpha[alpha < 0.04] = 0

gmask = cv2.dilate((alpha > 0.02).astype(np.uint8), np.ones((9, 9), np.uint8))
clean = cv2.inpaint(no_text, gmask * 255, 11, cv2.INPAINT_TELEA)
# soften the inpainted patches a bit + reintroduce wall grain so they don't look plastic
blur = cv2.GaussianBlur(clean, (0, 0), 6)
g = cv2.GaussianBlur(gmask.astype(np.float32), (0, 0), 4)[..., None]
clean = (clean * (1 - g * 0.6) + blur * g * 0.6)
noise = np.random.default_rng(1).normal(0, 4.5, clean.shape[:2])[..., None]
clean = np.clip(clean + noise * g, 0, 255).astype(np.uint8)
# kill the faint blue overspray ghost so the letters aren't readable before they're sprayed
ghost = cv2.GaussianBlur(cv2.dilate(gmask, np.ones((41, 41), np.uint8)).astype(np.float32), (0, 0), 10) * zone
hc = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV).astype(np.float32)
hc[..., 1] *= (1 - 0.85 * ghost)
hc[..., 2] = np.minimum(255, hc[..., 2] * (1 + 0.12 * ghost))
clean = cv2.cvtColor(hc.astype(np.uint8), cv2.COLOR_HSV2BGR)

# ---- 3. reveal-time map ----
body = cv2.morphologyEx((alpha > 0.15).astype(np.uint8), cv2.MORPH_OPEN,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))
body = cv2.dilate(body, np.ones((5, 5), np.uint8))
sweep = np.clip((xx - 150) / 1020.0, 0, 1)
rng = np.random.default_rng(7)
nz = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 9)
nz = (nz - nz.mean()) / (nz.std() + 1e-6)
t = 0.02 + sweep * 0.60 + (yy / H) * 0.10 + nz * 0.025

# drips: everything graffiti-ish that is not body grows downward from where it leaves the body
drip = (alpha > 0.02) & (body == 0)
tm = t.copy()
for x in range(0, 1240):
    col = drip[:, x]
    if not col.any(): continue
    run_start, last_t = None, None
    for y in range(H):
        if body[y, x]:
            last_t = t[y, x]; run_start = None
        elif col[y]:
            if run_start is None:
                run_start = y
                base = last_t if last_t is not None else t[y, x]
            tm[y, x] = base + 0.06 + (y - run_start) / 340.0 * 0.32
        else:
            run_start = None
t = tm
# logo halo sprays in last, together with the type
# logo halo reveals with the first sweep
t = np.clip(t, 0, 1)

Image.fromarray(cv2.cvtColor(no_text, cv2.COLOR_BGR2RGB)).save(f'{out}/painted.jpg', quality=84, optimize=True, progressive=True)
Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)).save(f'{out}/clean.jpg', quality=84, optimize=True, progressive=True)
m = np.zeros((H, W, 3), np.uint8)
m[..., 0] = (alpha * 255).astype(np.uint8)
m[..., 1] = (t * 255).astype(np.uint8)
Image.fromarray(m).save(f'{out}/map.png', optimize=True)
# debug previews
Image.fromarray((ui * 255).astype(np.uint8)).save(f'{out}/dbg_ui.png')
Image.fromarray((t * 255 * (alpha > 0.02)).astype(np.uint8)).save(f'{out}/dbg_t.png')
print('ok', drip.sum(), body.sum())

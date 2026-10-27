"""Turn the graffiti mask into a pen path for a smooth, bold spray reveal.
in : map.png (R = paint alpha, G = old timing), size W×H, open-kernel size
out: strokes.json  [[x, y, r, lift], ...]  in photo pixels, ordered like a writer would spray it
     map.png rewritten with B = 1 on letter bodies (revealed by the brush) and 0 on drips (revealed by time)
"""
import sys, json, numpy as np, cv2
from skimage.morphology import skeletonize

mp_path, out_json, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
mp = cv2.imread(mp_path)                       # BGR
alpha = mp[..., 2].astype(np.float32) / 255
H, W = alpha.shape
body = cv2.morphologyEx((alpha > .15).astype(np.uint8), cv2.MORPH_OPEN,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
n, lab, stats, _ = cv2.connectedComponentsWithStats(body)
keep = np.zeros_like(body)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > k * k * 3: keep[lab == i] = 1
body = keep
dist = cv2.distanceTransform(body, cv2.DIST_L2, 5)
sk = skeletonize(body > 0)
pts = set(zip(*np.nonzero(sk)))                # (y, x)

def nbrs(p):
    y, x = p
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dy or dx) and (y + dy, x + dx) in pts: yield (y + dy, x + dx)

# writer-like traversal: start at the left-most point, follow the skeleton, prefer going right/down,
# when a stroke ends lift the can and jump to the nearest unvisited point
visited, order = set(), []
cur = min(pts, key=lambda p: (p[1], p[0]))
lift = 1
while True:
    visited.add(cur); order.append((cur, lift)); lift = 0
    cand = [q for q in nbrs(cur) if q not in visited]
    if cand:
        cur = max(cand, key=lambda q: (q[1] - cur[1]) * .3 + (q[0] - cur[0]) * .1); continue
    rest = pts - visited
    if not rest: break
    cy, cx = cur
    # jump: nearest unvisited, biased to keep moving left-to-right through the word
    cur = min(rest, key=lambda q: np.hypot(q[0] - cy, q[1] - cx) + max(0, cx - q[1]) * 1.5)
    lift = 1

# split into strokes and spray them left to right through the word (each stroke starts at its left/top end)
strokes, curs = [], []
for p, lf in order:
    if lf and curs: strokes.append(curs); curs = []
    curs.append(p)
if curs: strokes.append(curs)
strokes = [st if (st[0][1], st[0][0]) <= (st[-1][1], st[-1][0]) else st[::-1] for st in strokes]
strokes.sort(key=lambda st: (min(p[1] for p in st) // 40, min(p[0] for p in st)))
order = [(p, int(i == 0)) for st in strokes for i, p in enumerate(st)]

# thin the path: keep a point every ~0.35 r along each stroke
path, last = [], None
for (y, x), lf in order:
    r = float(dist[y, x])
    if lf or last is None or np.hypot(x - last[0], y - last[1]) > max(3, r * .35):
        path.append([int(x), int(y), round(r * 1.25 + 2, 1), lf]); last = (x, y)

# coverage check: stamp the brush and fill any body pixel it misses with extra dabs
cov = np.zeros_like(body)
for x, y, r, _ in path: cv2.circle(cov, (x, y), int(r), 1, -1)
miss = (body > 0) & (cov == 0)
extra = 0
if miss.any():
    ys, xs = np.nonzero(miss)
    for y, x in zip(ys[::3], xs[::3]):
        if cov[y, x]: continue
        r = max(4.0, float(dist[y, x]) * 1.6 + 3)
        path.append([int(x), int(y), round(r, 1), 1]); cv2.circle(cov, (int(x), int(y)), int(r), 1, -1); extra += 1
print(f'{W}x{H}  skeleton {len(pts)}  path {len(path)}  extra dabs {extra}  body {int(body.sum())}  uncovered {int(((body>0)&(cov==0)).sum())}')

mp[..., 0] = (body * 255).astype(np.uint8)      # B channel = body flag
cv2.imwrite(mp_path, mp)
json.dump(path, open(out_json, 'w'), separators=(',', ':'))

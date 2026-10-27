"""Suit outlines from the cutout's alpha mask, cut geometrically.
args: cutout.png x0 y0 cuts.json out.json preview.png scene.png [affine.npy]
cuts (scene px): wrist_x, ankle_y, head (polygon to remove), hem (polyline jacket/trousers), rip_box [x0,y0,x1,y1]"""
import sys, json, numpy as np, cv2
cut = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED); x0, y0 = int(sys.argv[2]), int(sys.argv[3])
C = json.load(open(sys.argv[4])); out, prev, scene = sys.argv[5], sys.argv[6], cv2.imread(sys.argv[7])
A = np.load(sys.argv[8]) if len(sys.argv) > 8 else np.array([[1., 0, 0], [0, 1., 0]])
Ai = cv2.invertAffineTransform(A)
toCut = lambda P: (np.asarray(P, float) @ Ai[:, :2].T + Ai[:, 2]) - [x0, y0]       # scene → cutout px
toScene = lambda P: (np.asarray(P, float) + [x0, y0]) @ A[:, :2].T + A[:, 2]
a = (cut[..., 3] > 128).astype(np.uint8); H, W = a.shape
yy, xx = np.mgrid[0:H, 0:W]
wx = toCut([[C['wrist_x'], 0]])[0, 0]; ay = toCut([[0, C['ankle_y']]])[0, 1]
body = a.copy(); body[xx < wx] = 0; body[yy > ay] = 0
head = np.zeros_like(a); cv2.fillPoly(head, [np.round(toCut(C['head'])).astype(np.int32)], 1); body[head > 0] = 0
# hem: everything above the hem polyline (extended to the edges) is jacket
hem = toCut(C['hem']); poly = np.vstack([[[-5, hem[0, 1]]], hem, [[W + 5, hem[-1, 1]]], [[W + 5, -5]], [[-5, -5]]])
up = np.zeros_like(a); cv2.fillPoly(up, [np.round(poly).astype(np.int32)], 1)
k = max(3, W // 200)
clean = lambda m: cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
jacket = clean(body * up); trousers = clean(body * (1 - up))
def biggest(m):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    return (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8) if n > 1 else m
jacket = biggest(jacket)
# rip: skin-coloured pixels inside the rip box
bgr = cut[..., :3]; hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(int)
rb = toCut([C['rip_box'][:2], C['rip_box'][2:]]); rx0, ry0 = np.floor(rb[0]).astype(int); rx1, ry1 = np.ceil(rb[1]).astype(int)
skin = ((hsv[..., 1] > 45) & (hsv[..., 0] < 28) & (hsv[..., 2] < 215) & (a > 0)).astype(np.uint8)
box = np.zeros_like(a); box[max(0, ry0):ry1, max(0, rx0):rx1] = 1
rip = biggest(cv2.morphologyEx(skin * box, cv2.MORPH_CLOSE, np.ones((k * 2, k * 2), np.uint8)))
def contour(m, eps):
    c, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(c, key=cv2.contourArea)
    return toScene(cv2.approxPolyDP(c, eps, True)[:, 0, :])
def from_top(c): i = int(np.argmin(c[:, 1])); return np.vstack([c[i:], c[:i]])
J = from_top(contour(jacket, W / 450))
T = contour(trousers, W / 450)
# open the trousers stroke where it runs under the jacket hem: start just past the hem on the left leg
hemS = np.asarray(C['hem'], float)
hy = np.interp(T[:, 0], hemS[:, 0], hemS[:, 1])
under = T[:, 1] < hy + 10
if under.any() and (~under).any():
    i = int(np.argmax(under[:-1] & ~under[1:])) + 1
    T = np.vstack([T[i:], T[:i]]); T = T[~(T[:, 1] < np.interp(T[:, 0], hemS[:, 0], hemS[:, 1]) + 10)]
R = from_top(contour(rip, W / 600)) if rip.sum() > 30 else np.zeros((0, 2))
json.dump({'jacket': np.round(J).astype(int).tolist(), 'trousers': np.round(T).astype(int).tolist(), 'rip': np.round(R).astype(int).tolist()},
          open(out, 'w'), separators=(',', ':'))
pv = scene.copy()
for c, col, closed in [(J, (0, 0, 255), True), (T, (0, 200, 255), False), (R, (255, 0, 255), True)]:
    if len(c): cv2.polylines(pv, [np.round(c).astype(np.int32)], closed, col, 3)
cv2.imwrite(prev, pv); print('points', len(J), len(T), len(R))

# Composite Blender parts with vector-derived white outline + purple shadow.
# usage: python3 comp.py partsdir out.png [scale]
import sys, json, numpy as np, shapely
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt as edt
sys.path.insert(0, '.')
from glyphs import pieces, polys
from shapely.geometry import Polygon

D = sys.argv[1]; OUT = sys.argv[2]; SC = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
meta = json.load(open(D + '/meta.json'))
W, H = int(1774 * SC), int(887 * SC)


def raster(g, ss=3):
    im = Image.new('L', (W * ss, H * ss), 0); d = ImageDraw.Draw(im)
    for p in polys(g):
        d.polygon([(x * SC * ss, y * SC * ss) for x, y in p.exterior.coords], fill=255)
        for h in p.interiors: d.polygon([(x * SC * ss, y * SC * ss) for x, y in h.coords], fill=0)
    return np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255


def layer(mask_dist, width, c_in, c_out, edge_soft=1.0, grad0=0.35):
    a = np.clip((width - mask_dist) / edge_soft + 0.5, 0, 1)
    t = np.clip((mask_dist - width * grad0) / (width * (1 - grad0)), 0, 1); t = t * t * (3 - 2 * t)
    rgb = np.array(c_in)[None, None] * (1 - t[..., None]) + np.array(c_out)[None, None] * t[..., None]
    return np.dstack([rgb, a * 255]).astype(np.uint8)


def over(dst, src):
    a = src[..., 3:4] / 255.0
    dst[..., :3] = dst[..., :3] * (1 - a) + src[..., :3] * a
    dst[..., 3:4] = np.maximum(dst[..., 3:4], src[..., 3:4])


shadows = []; fronts = []
for pid, geoms, col, hole in pieces():
    small = pid.startswith('m') and pid != 'M'; splash = pid.startswith('splash')
    g = shapely.union_all(geoms)
    k = 4 if (small or splash) else 16
    g = g.buffer(k, quad_segs=24).buffer(-k, quad_segs=24)
    g = shapely.union_all([Polygon(p.exterior) for p in polys(g)])
    m = raster(g)
    dist = edt(m < 0.5) + np.clip(0.5 - m, -0.5, 0.5) * (m > 0)  # px outside silhouette
    ol = 8 if splash else 9 if small else 17
    sh = 12 if splash else 16 if small else 30
    outline = layer(dist, ol * SC, (255, 255, 255), (236, 220, 255))
    sd = np.roll(np.roll(dist, int(20 * SC) if not splash else int(8 * SC), axis=0), int(4 * SC), axis=1)
    shadow = layer(sd, sh * SC, (196, 140, 250), (146, 84, 234), grad0=0.45)
    body = np.zeros((H, W, 4), np.float32)
    im = np.asarray(Image.open(f'{D}/{pid}.png').convert('RGBA'), dtype=np.float32)
    if SC != 1.0:
        pass
    x, y = int(round(meta[pid]['x'] * SC)), int(round(meta[pid]['y'] * SC))
    hh, ww = im.shape[:2]; hh = min(hh, H - y); ww = min(ww, W - x)
    body[y:y + hh, x:x + ww] = im[:hh, :ww]
    front = outline.astype(np.float32); over(front, body)
    shadows.append(shadow); fronts.append(front)

can = np.zeros((H, W, 4), np.float32)
for s in shadows: over(can, s.astype(np.float32))
for f in fronts: over(can, f)
Image.fromarray(can.astype(np.uint8)).save(OUT)
print('ok', OUT)

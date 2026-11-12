# Clean bubble-letter glyphs for SIZE MATTERZ, built from round strokes (logo px, y down).
import math
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import unary_union

Q = 48  # quad segs per quarter circle


def stroke(pts, r):
    return LineString(pts).buffer(r, quad_segs=Q)


def arc(cx, cy, rad, a0, a1, n=40):  # degrees, y down
    return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + rad * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def cr(pts, steps=24):
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(len(pts) - 1, i + 2)]
        for k in range(steps):
            t = k / steps; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(tuple(pts[-1]))
    return out


def taper(pts, r0, r1, ease=lambda t: t, steps=30):
    s = cr(pts, steps)
    L = [0.0]
    for i in range(1, len(s)):
        L.append(L[-1] + math.dist(s[i], s[i - 1]))
    T = L[-1]
    return unary_union([Point(p).buffer(r0 + (r1 - r0) * ease(L[i] / T), quad_segs=Q) for i, p in enumerate(s)])


def drop(pts, r0, r1):
    return unary_union([taper(pts, r0 * 1.3, r1 * 0.92, lambda t: t ** 1.1), Point(pts[-1]).buffer(r1, quad_segs=Q)])


def soft(g, kc=14, ko=0):
    g = g.buffer(kc, quad_segs=Q).buffer(-kc, quad_segs=Q)  # round concave corners
    if ko:
        g = g.buffer(-ko, quad_segs=Q).buffer(ko, quad_segs=Q)
    return g


def S():
    r = 42; y1, y2, y3 = 236, 336, 436; xl, xr = 398, 488
    top = [(540, y1 + 4), (515, y1)] + [(x, y1) for x in (470, 430)] + [(xl, y1)]
    left = arc(xl, (y1 + y2) / 2, (y2 - y1) / 2, 270, 90)  # around left side, downwards
    mid = [(xl, y2), (xr, y2)]
    right = arc(xr, (y2 + y3) / 2, (y3 - y2) / 2, -90, 90)
    bot = [(xr, y3), (390, y3), (348, y3 - 4)]
    pts = top + left[1:] + mid[1:] + right[1:] + bot[1:]
    return soft(stroke(pts, r), 5)


def I():
    return stroke([(668, 262), (668, 410)], 67)


def Z(x0, x1, yt, yb, r):
    return soft(unary_union([stroke([(x0, yt), (x1, yt), (x0 + 2, yb), (x1 + 2, yb)], r)]), 12)


def E(x0, yt, ym, yb, xt, xm, xb, r):
    return soft(unary_union([stroke([(xt, yt), (x0, yt), (x0, yb), (xb, yb)], r), stroke([(x0, ym), (xm, ym)], r)]), 6)


def M():
    r = 47
    return soft(unary_union([stroke([(102, 728), (102, 542), (225, 688), (348, 542), (348, 728)], r)]), 12)


def A():
    r = 48
    legs = stroke([(440, 728), (507, 545), (585, 728)], r)
    bar = stroke([(462, 660), (560, 660)], 34)
    return soft(unary_union([legs, bar]), 12)


def T(xb0, xb1, xs, rb, rs):
    return soft(unary_union([stroke([(xb0, 554), (xb1, 554)], rb), stroke([(xs, 560), (xs, 728)], rs)]), 16)


def R():
    r = 44; yt, ym = 541, 645; xc = 1266
    bowl = [(1218, 730), (1218, yt), (xc, yt)] + arc(xc, (yt + ym) / 2, (ym - yt) / 2, -90, 90)[1:] + [(1218, ym)]
    leg = [(1248, ym), (1316, 730)]
    return soft(unary_union([stroke(bowl, r), stroke(leg, r)]), 6)


def snake():
    return taper([(1288, 446), (1360, 440), (1430, 416), (1494, 370), (1536, 318)], 42, 54, lambda t: t ** 0.7)


def mark(a, b, r0, r1):
    return taper([a, b], r0, r1)


def splashP():
    return unary_union([
        drop([(668, 214), (664, 160), (658, 105), (658, 52)], 9, 40),
        drop([(658, 208), (640, 170), (612, 128), (588, 102)], 7, 33),
        drop([(650, 210), (618, 190), (585, 168), (556, 150)], 6, 27),
        drop([(678, 210), (702, 160), (742, 108), (786, 70)], 8, 39),
        drop([(686, 216), (738, 186), (798, 154), (856, 134)], 7, 35),
    ]), [Point(774, 168).buffer(17, quad_segs=Q), Point(612, 198).buffer(9, quad_segs=Q), Point(718, 196).buffer(10, quad_segs=Q)]


def splashB():
    return unary_union([
        drop([(1562, 300), (1572, 250), (1584, 190), (1598, 142)], 7, 30),
        drop([(1556, 296), (1538, 255), (1516, 222), (1500, 205)], 6, 27),
        drop([(1570, 300), (1622, 245), (1672, 200), (1722, 178)], 8, 38),
        drop([(1574, 308), (1638, 292), (1688, 302), (1722, 332)], 8, 38),
    ]), [Point(1610, 330).buffer(14, quad_segs=Q)]


# id, geometry list (first is main body; extras are loose droplets), colour, hole
def pieces():
    sp, spd = splashP(); sb, sbd = splashB()
    return [
        ('M', [M()], (205, 120, 252), None),
        ('A', [A()], (104, 230, 238), None),
        ('T1', [T(632, 740, 686, 57, 50)], (253, 159, 67), dict(x=686, y=528, rx=36, ry=17, col=(249, 92, 104))),
        ('T2', [T(852, 929, 890, 56, 50)], (203, 104, 252), dict(x=890, y=528, rx=34, ry=17, col=(164, 50, 249))),
        ('E2', [E(1036, 539, 636, 733, 1105, 1092, 1122, 42)], (196, 245, 109), None),
        ('R', [R()], (106, 202, 252), None),
        ('Z2', [Z(1398, 1600, 537, 715, 47)], (252, 112, 193), None),
        ('S', [S()], (253, 208, 80), None),
        ('I', [I()], (253, 115, 191), dict(x=668, y=236, rx=37, ry=17, col=(247, 43, 152))),
        ('Z1', [Z(832, 973, 243, 431, 46)], (92, 225, 252), None),
        ('snake', [snake()], (253, 157, 83), None),
        ('E1', [E(1080, 238, 338, 438, 1214, 1196, 1240, 43)], (195, 244, 108), None),
        ('mL1', [mark((203, 444), (138, 392), 15, 24)], (253, 110, 190), None),
        ('mL2', [mark((250, 414), (224, 336), 13, 22)], (253, 214, 80), None),
        ('mR1', [mark((1598, 466), (1646, 398), 13, 22)], (253, 214, 80), None),
        ('mR2', [mark((1626, 500), (1708, 466), 13, 22)], (109, 210, 253), None),
        ('splashP', [sp] + spd, (253, 126, 206), None),
        ('splashB', [sb] + sbd, (109, 220, 253), None),
    ]


def polys(g):
    return list(g.geoms) if isinstance(g, MultiPolygon) else [g]

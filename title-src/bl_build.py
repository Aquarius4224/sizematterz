# Build the SIZE MATTERZ inflated letters in Blender and render.
# usage: bpyenv/bin/python bl_build.py out.png [scale] [only_id] [samples]
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from glyphs import pieces, polys

out = sys.argv[1]
SC = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
ONLY = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
SAMPLES = int(sys.argv[4]) if len(sys.argv) > 4 else 64

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
U = 0.01  # logo px -> blender units


def srgb2lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(col):
    return tuple(srgb2lin(v) for v in col) + (1.0,)


def hsv_shift(col, dh, ds, dv):
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in col])
    h = (h + dh / 360) % 1; s = min(1, max(0, s * ds)); v = min(1, max(0, v * dv))
    return tuple(int(255 * c) for c in colorsys.hsv_to_rgb(h, s, v))


def darker(col):
    import colorsys
    h = colorsys.rgb_to_hsv(*[c / 255 for c in col])[0] * 360
    dh = -14 if h < 75 else 12 if h < 210 else 6 if h < 300 else -8
    return hsv_shift(col, dh, 1.25, 0.8)


def make_mat(name, col, ytop, ybot):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = N['Principled BSDF']
    light = hsv_shift(col, 4 if col[0] > col[2] else -4, 0.92, 1.06)
    dark = darker(col)
    # vertical gradient: light top -> base -> deeper bottom
    geo = N.new('ShaderNodeNewGeometry')
    sep = N.new('ShaderNodeSeparateXYZ'); Lk.new(geo.outputs['Position'], sep.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -ybot * U; mr.inputs['From Max'].default_value = -ytop * U
    Lk.new(sep.outputs['Y'], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = lin(hsv_shift(col, -8 if col[0] > col[2] else 8, 1.3, 0.82))
    cr.elements[1].position = 1.0; cr.elements[1].color = lin(light)
    e = cr.elements.new(0.5); e.color = lin(hsv_shift(col, 0, 1.18, 1.0))
    Lk.new(mr.outputs['Result'], ramp.inputs['Fac'])
    # saturated rim where the surface turns away
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
    rr = N.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value = 0.25; rr.inputs['From Max'].default_value = 0.85
    Lk.new(lw.outputs['Facing'], rr.inputs['Value'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    Lk.new(rr.outputs['Result'], mix.inputs['Factor'])
    Lk.new(ramp.outputs['Color'], mix.inputs[6]); mix.inputs[7].default_value = lin(dark)
    Lk.new(mix.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.32
    bsdf.inputs['Coat Weight'].default_value = 1.0
    bsdf.inputs['Coat Roughness'].default_value = 0.06
    bsdf.inputs['Subsurface Weight'].default_value = 0.12
    bsdf.inputs['Subsurface Radius'].default_value = (0.3, 0.3, 0.3)
    bsdf.inputs['Subsurface Scale'].default_value = 0.05
    return m


def curve_obj(name, geoms, bevel, extrude, mat, z=0.0):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = bevel; cu.bevel_resolution = 10
    cu.extrude = extrude; cu.offset = -bevel; cu.resolution_u = 1
    for g in geoms:
        for p in polys(g):
            for ring in [p.exterior] + list(p.interiors):
                co = list(ring.coords)[:-1]
                sp = cu.splines.new('POLY'); sp.points.add(len(co) - 1)
                for i, (x, y) in enumerate(co):
                    sp.points[i].co = (x * U, -y * U, 0, 1)
                sp.use_cyclic_u = True; sp.use_smooth = True
    ob = bpy.data.objects.new(name, cu); ob.location.z = z
    cu.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    return ob


import numpy as np, shapely
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, Point
from shapely import affinity


def heights(d, R, dome):
    q = np.minimum(d, R) / R
    return R * np.sqrt(np.maximum(0, 1 - (1 - q) ** 2)) + dome * np.maximum(0, np.minimum(d, 2.6 * R) - R)


def inflate_mesh(name, poly, R, mat, dome=0.35, zs=0.85, st=2.2):
    P = []; D = []
    # boundary samples, plus two thin inner rings so the steep rim is resolved
    for d, sp in ((0, st * 0.8), (0.6, st * 0.8), (st * 0.9, st)):
        g = poly.buffer(-d, quad_segs=32) if d > 0 else poly
        for p in polys(g):
            for ring in [p.exterior] + list(p.interiors):
                L = ring.length; n = max(8, int(L / sp))
                for i in range(n):
                    q = ring.interpolate(L * i / n); P.append((q.x, q.y)); D.append(d)
    x0, y0, x1, y1 = poly.bounds
    gx, gy = np.meshgrid(np.arange(x0, x1, st), np.arange(y0, y1, st * 0.866))
    gx = gx + (np.arange(gx.shape[0])[:, None] % 2) * st * 0.5   # triangular lattice
    gx = gx.ravel(); gy = gy.ravel()
    inside = shapely.contains_xy(poly, gx, gy); gx = gx[inside]; gy = gy[inside]
    gd = shapely.distance(poly.boundary, shapely.points(gx, gy)) if len(gx) else np.zeros(0)
    keep = gd > st * 1.6; gx = gx[keep]; gy = gy[keep]; gd = gd[keep]
    P = np.vstack([np.array(P), np.c_[gx, gy]]) if len(gx) else np.array(P); D = np.concatenate([np.array(D), gd])
    tri = Delaunay(P)
    T = tri.simplices; c = P[T].mean(axis=1)
    T = T[shapely.contains_xy(poly.buffer(-0.05), c[:, 0], c[:, 1])]
    Z = heights(D, R, dome)
    nb = [[] for _ in range(len(P))]
    for a_, b_, c_ in T:
        nb[a_] += [b_, c_]; nb[b_] += [a_, c_]; nb[c_] += [a_, b_]
    nb = [np.array(sorted(set(n)), dtype=int) for n in nb]
    fixed = D < 1.0
    for _ in range(36):
        Zn = Z.copy()
        for i in range(len(P)):
            if not fixed[i] and len(nb[i]): Zn[i] = 0.5 * Z[i] + 0.5 * Z[nb[i]].mean()
        Z = Zn
    verts = [(x * U, -y * U, z * U * zs) for (x, y), z in zip(P, Z)]
    faces = [(int(a_), int(c_), int(b_)) for a_, b_, c_ in T]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    for f in me.polygons: f.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob


def flat_mat(name, col):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = lin(col); b.inputs['Roughness'].default_value = 0.7
    return m


def backing(name, geoms, col):
    g = shapely.union_all(geoms).buffer(16, quad_segs=24).buffer(-16, quad_segs=24)
    g = shapely.union_all([Polygon(p.exterior) for p in polys(g)])
    ob = curve_obj(name, [g], 0, 0, flat_mat(name + 'm', col)); ob.data.offset = 0; ob.location.z = -0.01
    return ob


objs = {}
for pid, geoms, col, hole in pieces():
    if ONLY and pid != ONLY:
        continue
    minx, miny, maxx, maxy = geoms[0].bounds
    small = pid.startswith('m') and pid != 'M'
    splash = pid.startswith('splash')
    R = 16 if small else 19 if splash else 46
    mat = make_mat(pid + '_m', col, miny, maxy)
    body = geoms[0]
    if hole:
        body = body.difference(affinity.scale(Point(hole['x'], hole['y']).buffer(1, quad_segs=32), hole['rx'], hole['ry']))
    lst = []
    for k, p in enumerate(polys(body)):
        lst.append(inflate_mesh(f'{pid}_{k}', p, R, mat, dome=0.1 if (small or splash) else 0.35))
    for k, g in enumerate(geoms[1:]):
        lst.append(inflate_mesh(f'{pid}_d{k}', g, min(R, (g.bounds[2] - g.bounds[0]) * 0.5), mat, dome=0))
    if not (small or splash):
        lst.append(backing(pid + '_back', geoms[:1], darker(col)))
    if hole:
        bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1, fill_type='NGON', location=(hole['x'] * U, -hole['y'] * U, -0.005))
        disc = bpy.context.active_object; disc.scale = ((hole['rx'] + 2) * U, (hole['ry'] + 2) * U, 1)
        disc.data.materials.append(flat_mat(pid + '_hm', darker(hole['col']))); lst.append(disc)
    objs[pid] = lst

# world: studio softboxes reflected in the clear coat
W = bpy.data.worlds.new('W'); scn.world = W; W.use_nodes = True
N = W.node_tree.nodes; Lk = W.node_tree.links; bg = N['Background']
tc = N.new('ShaderNodeTexCoord')


def softbox(d, lo, hi, s):
    v = N.new('ShaderNodeVectorMath'); v.operation = 'DOT_PRODUCT'
    L = d; l = math.sqrt(sum(c * c for c in L)); v.inputs[1].default_value = tuple(c / l for c in L)
    Lk.new(tc.outputs['Generated'], v.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    mr.inputs['To Max'].default_value = s; Lk.new(v.outputs['Value'], mr.inputs['Value'])
    return mr


# generated coords of world = view direction (x right, y up, z towards camera)
key = softbox((-0.45, 0.62, 0.65), 0.955, 0.975, 6.0)    # big key softbox upper-left -> crescent highlight
dot = softbox((-0.25, 0.35, 0.90), 0.993, 0.996, 14.0)   # small sharp catchlight
fill = softbox((0.5, -0.45, 0.74), 0.90, 0.96, 0.8)      # soft fill lower-right
sky = softbox((0.0, 0.3, 1.0), -0.2, 1.0, 0.2)           # general ambient
a1 = N.new('ShaderNodeMath'); a1.operation = 'ADD'; Lk.new(key.outputs[0], a1.inputs[0]); Lk.new(dot.outputs[0], a1.inputs[1])
a2 = N.new('ShaderNodeMath'); a2.operation = 'ADD'; Lk.new(a1.outputs[0], a2.inputs[0]); Lk.new(fill.outputs[0], a2.inputs[1])
a3 = N.new('ShaderNodeMath'); a3.operation = 'ADD'; Lk.new(a2.outputs[0], a3.inputs[0]); Lk.new(sky.outputs[0], a3.inputs[1])
Lk.new(a3.outputs[0], bg.inputs['Strength'])
bg.inputs['Color'].default_value = (1, 1, 1, 1)

# a soft key light for diffuse shape
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.data.energy = 2.4; sun.data.angle = math.radians(30)
sun.rotation_euler = (math.radians(-35), math.radians(-25), 0)

# camera
bpy.ops.object.camera_add(location=(17.74 / 2, -8.87 / 2, 20))
cam = bpy.context.active_object; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 17.74
cam.rotation_euler = (0, 0, 0); scn.camera = cam
cam.data.clip_end = 100

scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = SAMPLES
scn.cycles.use_denoising = True
scn.render.film_transparent = True
scn.render.resolution_x = int(1774 * SC); scn.render.resolution_y = int(887 * SC); scn.render.resolution_percentage = 100
scn.view_settings.view_transform = 'Standard'
scn.render.image_settings.file_format = 'PNG'; scn.render.image_settings.color_mode = 'RGBA'
scn.render.filepath = out
if out.endswith('/'):  # parts mode: one render per piece, cropped to its box
    import json
    os.makedirs(out, exist_ok=True); meta = {}
    allo = [o for l in objs.values() for o in l]
    for pid, geoms, col, hole in pieces():
        if pid not in objs: continue
        for o in allo: o.hide_render = o not in objs[pid]
        x0, y0, x1, y1 = shapely.union_all(geoms).bounds
        pad = 6; x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
        scn.render.use_border = True; scn.render.use_crop_to_border = True
        scn.render.border_min_x = max(0, x0 / 1774); scn.render.border_max_x = min(1, x1 / 1774)
        scn.render.border_min_y = max(0, 1 - y1 / 887); scn.render.border_max_y = min(1, 1 - y0 / 887)
        scn.render.filepath = out + pid + '.png'
        bpy.ops.render.render(write_still=True)
        W_, H_ = int(1774 * SC), int(887 * SC)
        meta[pid] = dict(x=int(scn.render.border_min_x * W_) / SC, y=(H_ - int(scn.render.border_max_y * H_)) / SC)
    json.dump(meta, open(out + 'meta.json', 'w'))
    print('parts done'); sys.exit(0)
bpy.ops.render.render(write_still=True)
print('done', out)

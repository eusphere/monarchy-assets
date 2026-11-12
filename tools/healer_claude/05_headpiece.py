"""Stage 5: the halo headdress of concept v008, in the team accent.

She is blind to the player: a visor of overlapping metal scales hangs from a
domed cap and covers everything from the brow to just above the lips. Only the
mouth and chin are bare. A fluted disc stands behind the head as a halo, and
thin rods hang at the temples.

Also here, because the mask is what reveals it: the lower face. The source
head is a featureless egg, so lips and a chin are modelled onto it and the
head wrap is opened round them. (The earlier crescent is 05_crescent_legacy.py.)"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
for n in ('Crescent headpiece', 'Halo cap', 'Halo disc', 'Scale visor', 'Temple rods', 'Wimple rim'):
    remove(n)
circ = bpy.data.objects.get('Healer - linked circlet and bow fasteners')
if circ:
    circ.hide_render = circ.hide_viewport = True
accent = bpy.data.materials['TeamAccent']

face = bpy.data.objects['Healer - pearl face']
wrap = bpy.data.objects['Head wrap']
fc = coords(face)
wc = coords(wrap)
crown_z = fc[:, 2].max()
x0 = float(np.median(fc[fc[:, 2] > crown_z - 0.15][:, 0]))
strip = np.abs(fc[:, 0] - x0) < 0.012
zs = np.arange(crown_z - 0.03, crown_z - 0.34, -0.005)
front = np.array([fc[strip & (np.abs(fc[:, 2] - z) < 0.006)][:, 1].min() for z in zs])
brow_y = front.min()
chin_z = float(zs[np.where(front <= brow_y + 0.030)[0][-1]])
H = crown_z - chin_z
mouth_z = crown_z - 0.80 * H
brow_z = crown_z - 0.34 * H                    # lower rim of the cap, low on the forehead
visor_bottom = mouth_z + 0.060 * H             # just above the upper lip
cy = float((fc[fc[:, 2] > crown_z - 0.15][:, 1].min() + fc[fc[:, 2] > crown_z - 0.15][:, 1].max()) / 2)
print('head: crown %.3f chin %.3f mouth %.3f brow %.3f centre x %.3f y %.3f' % (crown_z, chin_z, mouth_z, brow_z, x0, cy), flush=True)

# ------------------------------------------------------------------ lower face
if not face.get('claude_lips'):
    nrm = np.empty(3 * len(face.data.vertices))
    face.data.vertices.foreach_get('normal', nrm)
    nrm = nrm.reshape(-1, 3)
    u = fc[:, 0] - x0
    v = fc[:, 2] - mouth_z
    onface = (fc[:, 1] < cy - 0.02).astype(float)
    g = lambda a, s: np.exp(-(a / s) ** 2)        # noqa: E731
    bow = 1 - 0.28 * g(u, 0.006)                  # the dip of the upper lip's bow
    upper = 0.0062 * g(u, 0.031) * g(v - 0.0085, 0.0068) * bow
    lower = 0.0078 * g(u, 0.026) * g(v + 0.0100, 0.0082)
    part = -0.0052 * g(u, 0.034) * g(v, 0.0028)   # the line between the lips
    hollow = -0.0036 * g(u, 0.024) * g(v + 0.028, 0.008)
    chin = 0.0085 * g(u, 0.026) * g(v + 0.052, 0.017)
    corners = -0.0024 * (g(u - 0.035, 0.007) + g(u + 0.035, 0.007)) * g(v, 0.007)
    d = (upper + lower + part + hollow + chin + corners) * onface
    set_coords(face, fc + nrm * d[:, None])
    lip = np.clip((upper / 0.0062 + lower / 0.0078) * 2.2 - 0.30, 0, 1) * onface
    attr = face.data.attributes.new('Lip', 'FLOAT', 'POINT')
    attr.data.foreach_set('value', lip)
    face['claude_lips'] = 1
    fc = coords(face)
skin = bpy.data.materials.get('Healer skin') or bpy.data.materials.new('Healer skin')
skin.use_nodes = True
nt = skin.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
at = nt.nodes.new('ShaderNodeAttribute')
at.attribute_name = 'Lip'
mix = nt.nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'
mix.inputs[6].default_value = (0.78, 0.70, 0.63, 1)          # pale, bloodless skin
mix.inputs[7].default_value = (0.045, 0.010, 0.012, 1)       # lips the colour of dried blood
nt.links.new(at.outputs['Fac'], mix.inputs[0])
nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.48
bsdf.inputs['Subsurface Weight'].default_value = 0.15
bsdf.inputs['Subsurface Radius'].default_value = (0.012, 0.006, 0.004)
nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
face.data.materials.clear()
face.data.materials.append(skin)
face.hide_render = face.hide_viewport = False

# Open the wrap round the mouth and chin, like a wimple: an oval that narrows to the chin.
remove('Wimple rim')
oz_top = visor_bottom + 0.014
oz_bot = chin_z - 0.016
oz = (oz_top + oz_bot) / 2
oh = (oz_top - oz_bot) / 2


def opening_half_width(z):
    t = (z - oz) / oh
    if abs(t) >= 1:
        return 0.0
    return 0.058 * math.sqrt(1 - t * t) * (1 - 0.30 * max(-t, 0.0))


if not wrap.get('claude_opened'):
    bm = bmesh.new()
    bm.from_mesh(wrap.data)
    kill = [v for v in bm.verts if v.co.y < cy - 0.02 and abs(v.co.x - x0) < opening_half_width(v.co.z)]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(wrap.data)
    bm.free()
    wrap['claude_opened'] = 1
    wc = coords(wrap)

# ------------------------------------------------------------------ surface the metal sits on
tri = BVHTree.FromPolygons([tuple(p) for p in wc], [tuple(p.vertices) for p in wrap.data.polygons])
ftri = BVHTree.FromPolygons([tuple(p) for p in fc], [tuple(p.vertices) for p in face.data.polygons])
centre = Vector((x0, cy, crown_z - 0.115))


def radius(theta, z):
    """Horizontal distance from the head's axis to its outer surface (wrap or face)."""
    d = Vector((math.cos(theta), math.sin(theta), 0))
    o = Vector((x0, cy, z)) + d * 0.5
    best = 0.0
    for t in (tri, ftri):
        hit = t.ray_cast(o, -d, 0.5)
        if hit[0] is not None:
            best = max(best, 0.5 - hit[3])
    return best


def skinned(ob, smooth=True):
    ob.data.materials.append(accent)
    ob.parent = rig
    vg = ob.vertex_groups.new(name='Head')
    vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
    arm = ob.modifiers.new('Healer skin', 'ARMATURE')
    arm.object = rig
    return ob


# ------------------------------------------------------------------ wimple rim
# A soft rolled edge of cloth round the opening, where the wrap is folded back from the face.
NR_, NT_ = 96, 8
rv, rf = [], []
for i in range(NR_):
    a = 2 * math.pi * i / NR_
    z = oz + oh * 0.985 * math.sin(a)
    hwid = opening_half_width(z) + 0.002
    x = x0 + hwid * (1 if math.cos(a) >= 0 else -1)
    if abs(math.sin(a)) > 0.999:
        x = x0
    ang = math.atan2(-1.0, (x - x0) / 0.09)                    # direction from the axis to this point
    d = Vector((x - x0, 0, 0))
    yy = cy - math.sqrt(max(radius(math.atan2(-0.09, x - x0), z) ** 2 - (x - x0) ** 2, 1e-6))
    c = np.array([x, yy - 0.003, z])
    for k in range(NT_):
        b = 2 * math.pi * k / NT_
        rv.append(tuple(c + 0.0045 * np.array([math.cos(b) * math.cos(a), -math.sin(b), math.cos(b) * math.sin(a)])))
for i in range(NR_):
    for k in range(NT_):
        rf.append((i * NT_ + k, ((i + 1) % NR_) * NT_ + k, ((i + 1) % NR_) * NT_ + (k + 1) % NT_, i * NT_ + (k + 1) % NT_))
rimo = new_object('Wimple rim', rv, rf, 'Garments')
face_out(rimo)
rimo.data.materials.append(bpy.data.materials['Voile'])
rimo.parent = rig
vg = rimo.vertex_groups.new(name='Head')
vg.add(list(range(len(rv))), 1.0, 'REPLACE')
am = rimo.modifiers.new('Healer skin', 'ARMATURE')
am.object = rig
sb = rimo.modifiers.new('Smooth', 'SUBSURF')
sb.levels = sb.render_levels = 1

# ------------------------------------------------------------------ cap
T = 72
th = [2 * math.pi * j / T for j in range(T)]
rings = []
for phi in np.radians(np.linspace(6, 88, 12)):               # dome, from near the crown outward
    ring = []
    for t in th:
        d = Vector((math.sin(phi) * math.cos(t), math.sin(phi) * math.sin(t), math.cos(phi)))
        hit = tri.ray_cast(centre + d * 0.5, -d, 0.5)
        r = (0.5 - hit[3]) if hit[0] is not None else 0.11
        p = centre + d * (r + 0.006)
        ring.append((p.x, p.y, p.z))
    rings.append(ring)
for z in np.arange(centre.z - 0.012, brow_z, -0.012):       # straight sides down to the brow
    rings.append([(x0 + (radius(t, z) + 0.006) * math.cos(t), cy + (radius(t, z) + 0.006) * math.sin(t), z) for t in th])
rb = [radius(t, brow_z) for t in th]
for dr, dz in ((0.006, 0.0), (0.0082, 0.002), (0.0082, -0.011), (0.006, -0.0125)):   # a slight rim, barely proud of the dome
    rings.append([(x0 + (rb[j] + dr) * math.cos(th[j]), cy + (rb[j] + dr) * math.sin(th[j]), brow_z + dz) for j in range(T)])
cv = [p for r in rings for p in r]
top = np.mean(np.array(rings[0]), axis=0) + np.array([0, 0, 0.003])
cv.append(tuple(top))
cf = grid_faces(len(rings), T, True) + [(len(cv) - 1, (j + 1) % T, j) for j in range(T)]
cap = new_object('Halo cap', cv, cf, 'Jewelry')
face_out(cap)
skinned(cap)
sub = cap.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1
band_bottom = brow_z - 0.0125

# ------------------------------------------------------------------ halo disc
R_OUT, R_IN, FLUTES, SEG = 0.205, 0.070, 56, 448
hz = crown_z - 0.085                                          # centred on the forehead, as a halo is
hv, hf = [], []
radii = (R_IN, 0.110, 0.150, R_OUT - 0.020, R_OUT - 0.010, R_OUT)
for i in range(SEG):
    a = 2 * math.pi * i / SEG
    flute = 2 * abs((a * FLUTES / (2 * math.pi)) % 1 - 0.5)   # 0..1 zigzag
    for k, r in enumerate(radii):
        depth = 0.0050 * (flute - 0.5) * min(r / 0.11, 1.0) if k < 4 else 0.0
        rim = 0.004 if k >= 4 else 0.0                        # a plain raised rim round the fluting
        hv.append((x0 + r * math.cos(a), cy + 0.012 - depth - rim, hz + r * math.sin(a)))
K = len(radii)
for i in range(SEG):
    for k in range(K - 1):
        a0, a1 = i * K + k, ((i + 1) % SEG) * K + k
        hf.append((a0, a1, a1 + 1, a0 + 1))
disc = new_object('Halo disc', hv, hf, 'Jewelry', smooth=False)
skinned(disc)
sol = disc.modifiers.new('Thickness', 'SOLIDIFY')
sol.thickness = 0.006
sol.offset = 1

# ------------------------------------------------------------------ scale visor
sv, sf = [], []
ROW, SW, SH = 0.0118, 0.0150, 0.0185
SPAN = math.radians(66)
row = 0
z = band_bottom + 0.004
while z - SH > visor_bottom - 0.004:
    r_mid = radius(-math.pi / 2, z - SH / 2)
    n = max(int(2 * SPAN * r_mid / (SW * 0.86)), 6)
    for i in range(n + (row % 2)):
        a = -math.pi / 2 - SPAN + 2 * SPAN * (i + 0.5 * (1 - row % 2)) / n
        if abs(a + math.pi / 2) > SPAN + 0.02:
            continue
        r_top = radius(a, z) + 0.0045 + 0.0012 * (row % 2)
        r_bot = radius(a, z - SH) + 0.0075
        out_v = np.array([math.cos(a), math.sin(a), 0.0])
        side = np.array([-math.sin(a), math.cos(a), 0.0])
        c_top = np.array([x0, cy, z]) + out_v * r_top
        c_bot = np.array([x0, cy, z - SH]) + out_v * r_bot
        base = len(sv)
        outline = [(-0.5, 0.0), (0.5, 0.0), (0.5, 0.55), (0.36, 0.84), (0.0, 1.0), (-0.36, 0.84), (-0.5, 0.55)]
        for (pu, pv) in outline:
            p = c_top * (1 - pv) + c_bot * pv + side * (pu * SW) + out_v * (0.0016 * (1 - (2 * pu) ** 2) * pv)
            sv.append(tuple(p))
        sf.append(tuple(range(base, base + 7)))
    z -= ROW
    row += 1
visor = new_object('Scale visor', sv, sf, 'Jewelry', smooth=False)
face_out(visor)
skinned(visor)
sol = visor.modifiers.new('Thickness', 'SOLIDIFY')
sol.thickness = 0.0014
sol.offset = 1
print('visor rows', row, 'scales', len(sf), flush=True)

# ------------------------------------------------------------------ temple rods
tv, tf = [], []
for sgn in (-1, 1):
    for k, (off, length) in enumerate(((72, 0.150), (80, 0.185), (88, 0.165))):
        a = -math.pi / 2 + sgn * math.radians(off)
        r = rb[int(round((a % (2 * math.pi)) / (2 * math.pi) * T)) % T] + 0.017
        px, py = x0 + r * math.cos(a), cy + r * math.sin(a)
        for (z0, z1, rad) in ((band_bottom + 0.004, band_bottom - length, 0.0026),
                              (band_bottom - length, band_bottom - length - 0.016, 0.0048)):   # rod, then its weight
            base = len(tv)
            for zz in (z0, z1):
                tv += [(px + rad * math.cos(2 * math.pi * q / 8), py + rad * math.sin(2 * math.pi * q / 8), zz) for q in range(8)]
            tf += [(base + q, base + (q + 1) % 8, base + 8 + (q + 1) % 8, base + 8 + q) for q in range(8)]
            tf += [tuple(base + q for q in range(7, -1, -1)), tuple(base + 8 + q for q in range(8))]
rods = new_object('Temple rods', tv, tf, 'Jewelry')
face_out(rods)
skinned(rods)

save()
render('stage5-headpiece-front', 0)
render('stage5-headpiece-portrait', 0, dist=2.0, target_z=crown_z - 0.13, lens=85, res=(900, 1000), samples=64)
render('stage5-headpiece-three-quarter', 32, dist=2.0, target_z=crown_z - 0.13, lens=85, res=(900, 1000), samples=64)
render('stage5-headpiece-side', 90, dist=2.0, target_z=crown_z - 0.13, lens=85, res=(900, 1000), samples=64)
print('stage 5 done')

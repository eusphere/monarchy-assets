"""Stage 5: the halo headdress of concept v008, in the team accent.

She is blind to the player: a visor of overlapping metal scales hangs from a
domed cap and covers everything from the brow to just above the lips. Only the
mouth and chin are bare. A fluted disc stands behind the head as a halo, and
thin rods hang at the temples.

The face itself comes from stage 1b. Here the head wrap is cut back to a hood
behind the ears, so the cheeks, jaw, chin and throat are bare skin.
(The earlier crescent is 05_crescent_legacy.py.)"""
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
crown_z = float(face['lm_crown'])
x0 = float(face['lm_centre_x'])
chin_z = float(face['lm_chin'])
mouth_z = float(face['lm_mouth'])
H = crown_z - chin_z
brow_z = crown_z - 0.34 * H                    # lower rim of the cap, low on the forehead
visor_bottom = float(face['lm_lip_top']) + 0.006   # just above the upper lip: the nose is covered too
skull = fc[fc[:, 2] > crown_z - 0.15]
cy = float((skull[:, 1].min() + skull[:, 1].max()) / 2)
print('head: crown %.3f chin %.3f mouth %.3f brow %.3f visor bottom %.3f centre x %.3f y %.3f'
      % (crown_z, chin_z, mouth_z, brow_z, visor_bottom, x0, cy), flush=True)

# ------------------------------------------------------------------ bare the face and throat
# No cloth round the face: the wrap stays only as a hood over the back and sides of the head,
# behind the line of the ears. Cheeks, jaw, chin and the front of the neck are skin.
OPEN = math.radians(78)                        # half-angle of the opening, measured from straight ahead
if not wrap.get('claude_opened'):
    bm = bmesh.new()
    bm.from_mesh(wrap.data)
    kill = []
    for v in bm.verts:
        ang = math.atan2(v.co.y - cy, v.co.x - x0)
        off = abs((ang + math.pi / 2 + math.pi) % (2 * math.pi) - math.pi)
        if off < OPEN and v.co.z < brow_z + 0.004:
            kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(wrap.data)
    bm.free()
    wrap['claude_opened'] = 1
    wc = coords(wrap)
face.hide_render = face.hide_viewport = False

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
# The visor hangs from the rim like a curtain of mail: it falls straight from whatever stands
# furthest out above it (brow, then nose) and never dips into the eye sockets. So its surface is
# the running maximum of the face's radius from the rim downward, smoothed sideways.
VA = np.radians(np.linspace(-90 - 80, -90 + 80, 81))
VZ = np.arange(brow_z + 0.004, visor_bottom - 0.030, -0.003)
raw = np.array([[radius(a_, z_) for a_ in VA] for z_ in VZ])
hang_grid = np.maximum.accumulate(raw, axis=0)
for _ in range(3):                                      # bridge across the nose and the sockets
    hang_grid = np.maximum(hang_grid, 0.5 * (np.roll(hang_grid, 1, 1) + np.roll(hang_grid, -1, 1)))
    hang_grid[:, 0], hang_grid[:, -1] = raw[:, 0].cummax() if hasattr(raw[:, 0], 'cummax') else np.maximum.accumulate(raw[:, 0]), np.maximum.accumulate(raw[:, -1])
kern = np.array([1, 2, 3, 2, 1]) / 9
hang_grid = np.maximum(hang_grid, np.stack([np.convolve(np.pad(r_, 2, mode='edge'), kern, 'valid') for r_ in hang_grid]))


def hang(a_, z_):
    i = int(np.clip(round((VZ[0] - z_) / 0.003), 0, len(VZ) - 1))
    return float(np.interp(a_, VA, hang_grid[i]))


sv, sf = [], []
ROW, SW, SH = 0.0118, 0.0150, 0.0185
SPAN = math.radians(66)
row = 0
z = band_bottom + 0.004
while z - SH > visor_bottom - 0.004:
    r_mid = hang(-math.pi / 2, z - SH / 2)
    n = max(int(2 * SPAN * r_mid / (SW * 0.86)), 6)
    for i in range(n + (row % 2)):
        a = -math.pi / 2 - SPAN + 2 * SPAN * (i + 0.5 * (1 - row % 2)) / n
        if abs(a + math.pi / 2) > SPAN + 0.02:
            continue
        r_top = hang(a, z) + 0.0050 + 0.0012 * (row % 2)
        r_bot = hang(a, z - SH) + 0.0080
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

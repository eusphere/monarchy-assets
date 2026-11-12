"""Stage 3: the head wrap and the hanging veil.

Dropping one big sheet over the head and cinching it at the neck did not
survive contact with the solver, so the veil is made the way the concept reads:

* `Head wrap`  - a taut, finely striated shell stretched over the head and
  neck, built directly from the head's silhouette (no simulation).
* `Head veil`  - a full, pleated panel hung from a line round the back of the
  head, temple to temple. It falls over the shoulders and arms and down the
  back to about the knee."""
import os
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

SCALE = float(os.environ.get('HEALER_RES', '1.0'))
FRAMES = 150
for n in ('Head veil', 'Head wrap', 'Neck gather', 'Waist guard', 'Collider - Healer - pearl face',
          'Collider - Fit05 posed glove raised', 'Collider - Fit05 posed glove open'):
    remove(n)

head = bpy.data.objects['Healer - pearl face']
hc = coords(head)
crown_z = hc[:, 2].max()
me = head.data
bvh = BVHTree.FromPolygons([tuple(v) for v in hc], [tuple(p.vertices) for p in me.polygons])

# ------------------------------------------------------------------ head wrap
T = 128                                  # round the head
theta = 2 * np.pi * np.arange(T) / T     # 0 = figure's left (+x), 90 deg = back (+y)
dirs = np.stack([np.cos(theta), np.sin(theta)], -1)
top = hc[hc[:, 2] > crown_z - 0.16]
centre = np.array([top[:, 0].mean(), (top[:, 1].min() + top[:, 1].max()) / 2, crown_z - 0.115])
BOTTOM = crown_z - 0.40
rows = []                                # (origin, polar angle from +z or None)
for phi in np.radians(np.linspace(4, 90, 22)):
    rows.append((centre, phi))
for z in np.arange(centre[2] - 0.008, BOTTOM, -0.008):
    sl = hc[np.abs(hc[:, 2] - z) < 0.012]
    c = np.array([sl[:, 0].mean(), (sl[:, 1].min() + sl[:, 1].max()) / 2, z]) if len(sl) > 8 else None
    rows.append((c, None))
# Keep the axis from jumping between slices.
last = centre
fixed = []
for c, phi in rows:
    if c is None:
        c = np.array([last[0], last[1], last[2] - 0.008])
    elif phi is None:
        c = np.array([0.6 * last[0] + 0.4 * c[0], 0.6 * last[1] + 0.4 * c[1], c[2]])
    fixed.append((c, phi))
    last = c
rows = fixed
NR = len(rows)
rad = np.zeros((NR, T))
for i, (c, phi) in enumerate(rows):
    for j in range(T):
        if phi is None:
            d = Vector((dirs[j, 0], dirs[j, 1], 0))
        else:
            d = Vector((np.sin(phi) * dirs[j, 0], np.sin(phi) * dirs[j, 1], np.cos(phi)))
        # Cast inward from outside so the outermost surface is the one found.
        far = Vector(c) + d * 0.6
        hit = bvh.ray_cast(far, -d, 0.6)
        rad[i, j] = (0.6 - hit[3]) if hit[0] is not None else np.nan
# Fill misses from neighbours.
for i in range(NR):
    row = rad[i]
    if np.isnan(row).all():
        rad[i] = rad[i - 1]
    elif np.isnan(row).any():
        ok = ~np.isnan(row)
        rad[i] = np.interp(np.arange(T), np.where(ok)[0], row[ok], period=T)
print('head wrap rows', NR, 'radius range', float(rad.min()), float(rad.max()), flush=True)


def blur(a, sig_r, sig_t):
    nr, nt = int(np.ceil(3 * sig_r)), int(np.ceil(3 * sig_t))
    kr = np.exp(-0.5 * (np.arange(-nr, nr + 1) / sig_r) ** 2)
    kt = np.exp(-0.5 * (np.arange(-nt, nt + 1) / sig_t) ** 2)
    pad = np.pad(a, ((len(kr) // 2, len(kr) // 2), (0, 0)), mode='edge')
    a = np.stack([np.convolve(pad[:, j], kr / kr.sum(), 'valid') for j in range(a.shape[1])], 1)
    pad = np.pad(a, ((0, 0), (len(kt) // 2, len(kt) // 2)), mode='wrap')
    return np.stack([np.convolve(pad[i], kt / kt.sum(), 'valid') for i in range(a.shape[0])], 0)


# Stretch the cloth taut: bridge hollows (eyes, under the nose and chin), soften features.
taut = rad.copy()
for _ in range(3):
    m = np.maximum.reduce([np.roll(taut, 1, 1), np.roll(taut, -1, 1), taut,
                           np.vstack([taut[:1], taut[:-1]]), np.vstack([taut[1:], taut[-1:]])])
    taut = np.maximum(taut, m - 0.004)
soft = blur(taut, 1.2, 1.5)
taut = np.maximum(soft, rad) * 0.7 + soft * 0.3 + 0.004
# Fine vertical striations, as if the cloth were pulled tight from the crown.
stri = 0.0011 * np.sin(46 * theta + 1.3 * np.sin(5 * theta)) + 0.0006 * np.sin(97 * theta)
verts = np.zeros((NR, T, 3))
for i, (c, phi) in enumerate(rows):
    r = taut[i] + stri * min(i / 8, 1.0)
    if phi is None:
        verts[i, :, 0] = c[0] + r * dirs[:, 0]
        verts[i, :, 1] = c[1] + r * dirs[:, 1]
        verts[i, :, 2] = c[2]
    else:
        verts[i, :, 0] = c[0] + r * np.sin(phi) * dirs[:, 0]
        verts[i, :, 1] = c[1] + r * np.sin(phi) * dirs[:, 1]
        verts[i, :, 2] = c[2] + r * np.cos(phi)
cap = verts[0].mean(axis=0) + np.array([0, 0, 0.002])
wv = np.vstack([verts.reshape(-1, 3), cap[None]])
wf = grid_faces(NR, T, True) + [(NR * T, (j + 1) % T, j) for j in range(T)]
wrap = new_object('Head wrap', wv, wf, 'Garments')
# Normals must face out: the cloth solver pushes along them.
import bmesh
bm = bmesh.new()
bm.from_mesh(wrap.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(wrap.data)
bm.free()
rig = bpy.data.objects['Healer Rig']
wrap.parent = rig
wrap.data.materials.append(bpy.data.materials['Voile'])
sub = wrap.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 2
head.hide_render = True                  # the wrap now stands in for the head

if os.environ.get('HEALER_VEIL', '1') == '0':
    # First pass of the pipeline: only the head wrap, which the cowl and sash need before the veil exists.
    save()
    print('stage 3 head wrap only')
    sys.exit(0)

# ------------------------------------------------------------------ colliders
add_collision(bpy.data.objects['Body form'], 0.005)
collide_before_subsurf(wrap, 0.004)
collider_proxy('Fit05 posed glove raised', 0.03, 0.003)
collider_proxy('Fit05 posed glove open', 0.03, 0.003)
# The veil must not catch in the skirt's pleats, so it collides with a smooth,
# frictionless shell fitted just outside the skirt instead of the skirt itself.
skirt = bpy.data.objects['Underdress skirt']
for m in list(skirt.modifiers):
    if m.type == 'COLLISION':
        skirt.modifiers.remove(m)
# The shell covers everything the veil lies on from the shoulders down: torso, wraps and skirt.
bf = coords(bpy.data.objects['Body form'])
parts = [coords(skirt), bf[(np.abs(bf[:, 0]) < 0.15) & (np.abs(bf[:, 1]) < 0.125)]]
for n in ('Shoulder wrap', 'Neck cowl'):
    if n in bpy.data.objects:
        ob = bpy.data.objects[n]
        parts.append(coords(ob))
        for m in list(ob.modifiers):
            if m.type == 'COLLISION':
                ob.modifiers.remove(m)
sk = np.vstack(parts)
GT = 48
gt = 2 * np.pi * np.arange(GT) / GT
zs = np.arange(1.84, 0.20, -0.04)
sa = np.arctan2(sk[:, 1], sk[:, 0]) % (2 * np.pi)
srad = np.hypot(sk[:, 0], sk[:, 1])
shell = np.zeros((len(zs), GT))
for i, z in enumerate(zs):
    band = np.abs(sk[:, 2] - z) < 0.03
    for j in range(GT):
        d = np.abs((sa - gt[j] + np.pi) % (2 * np.pi) - np.pi)
        sel = band & (d < 2 * np.pi / GT)
        shell[i, j] = srad[sel].max() if sel.any() else np.nan
for i in range(len(zs)):
    row = shell[i]
    ok = ~np.isnan(row)
    shell[i] = np.interp(np.arange(GT), np.where(ok)[0], row[ok], period=GT) if ok.any() else shell[i - 1]
# Never narrower than the level above by much: the veil should fall clear, not tuck under ledges.
for i in range(1, len(zs)):
    shell[i] = np.maximum(shell[i], shell[i - 1] - 0.012)
shell = blur(shell, 1.0, 1.5) + 0.007
gr = []
for i in range(len(zs)):
    gr += [(shell[i, j] * np.cos(gt[j]), shell[i, j] * np.sin(gt[j]), zs[i]) for j in range(GT)]
guard = new_object('Waist guard', gr, grid_faces(len(zs), GT, True), 'Sim')
guard.hide_render = True
face_out(guard)
add_collision(guard, 0.004, friction=0)

# ------------------------------------------------------------------ hanging veil
C = int(300 * SCALE)
R = int(210 * SCALE)
A0, A1 = np.radians(-42), np.radians(222)        # temple, round the back, to the other temple
ang = np.linspace(A0, A1, C)
# Attachment line: a ring on the upper skull of the wrap.
pin_row = 14
pc, pphi = rows[pin_row]
r_at = np.interp(ang % (2 * np.pi), theta, taut[pin_row], period=2 * np.pi) + 0.007
start = np.stack([pc[0] + r_at * np.sin(pphi) * np.cos(ang),
                  pc[1] + r_at * np.sin(pphi) * np.sin(ang),
                  pc[2] + r_at * np.cos(pphi) + 0 * ang], -1)
# Profile the cloth follows away from the head: out over the shoulders, then down.
prof = np.array([(0.000, 0.000), (0.060, -0.035), (0.150, -0.130), (0.250, -0.300),
                 (0.310, -0.600), (0.380, -1.100), (0.420, -1.470)])
seg = np.linalg.norm(np.diff(prof, axis=0), axis=1)
dist = np.concatenate([[0], np.cumsum(seg)])
even = np.linspace(0, dist[-1], R)
pr = np.interp(even, dist, prof[:, 0])
pz = np.interp(even, dist, prof[:, 1])
PLEATS = 34
vv = np.zeros((R, C, 3))
for i in range(R):
    t = i / (R - 1)
    amp = 0.004 + 0.022 * t
    rr = pr[i] + amp * np.sin(PLEATS * (ang - A0) / (A1 - A0) * 2 * np.pi + 0.5 * np.sin(4 * ang)) * min(i / 6, 1)
    # The back is cut longer than the sides, like the V-shaped tiers in the rear view.
    longer = 1 + 0.10 * np.clip(np.sin(ang), 0, 1) ** 2 * t
    vv[i, :, 0] = start[:, 0] + rr * np.cos(ang)
    vv[i, :, 1] = start[:, 1] + rr * np.sin(ang)
    vv[i, :, 2] = start[:, 2] + pz[i] * longer
uv = np.stack([np.repeat(np.linspace(0, 2.2, C)[None, :], R, 0), np.repeat(even[:, None], C, 1)], -1)
veil = new_object('Head veil', vv.reshape(-1, 3), grid_faces(R, C, False), 'Garments', uv.reshape(-1, 2))
pin = veil.vertex_groups.new(name='Pin')
pin.add(list(range(2 * C)), 1.0, 'REPLACE')

cloth = veil.modifiers.new('Cloth', 'CLOTH')
cs = cloth.settings
cs.quality = 8
cs.mass = 0.12
cs.tension_stiffness = cs.compression_stiffness = 14
cs.shear_stiffness = 4
cs.bending_stiffness = 0.10
cs.tension_damping = cs.compression_damping = 5
cs.shear_damping = 5
cs.bending_damping = 0.5
cs.air_damping = 1.0
cs.vertex_group_mass = 'Pin'
cc = cloth.collision_settings
cc.use_collision = True
cc.distance_min = 0.006
cc.collision_quality = 4
cc.use_self_collision = True
cc.self_distance_min = 0.003
cc.self_friction = 8

print('simulating veil', C, 'x', R, flush=True)
simulate(veil, FRAMES)
veil.parent = rig
veil.data.materials.append(bpy.data.materials['Voile'])
sub = veil.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1

save()
render('stage3-veil-front', 0)
render('stage3-veil-side', 90)
render('stage3-veil-rear', 180)
render('stage3-veil-portrait', 20, dist=2.6, target_z=1.98, lens=85, res=(800, 1000))
print('stage 3 done')

"""Stage 4: the neck cowl and the diagonal chest wraps.

A free strip wound round the shoulders simply slides down the arms, so the
wraps are made the way they stay on a body:

* `Neck cowl`     - a pleated strip wound twice round the neck; it settles on
  the slope of the shoulders.
* `Shoulder wrap` - a sash laid on the torso: from the left hip up across the
  chest, over the right shoulder, down the back, then twice round the waist.

Both go on before the veil, which is draped over them afterwards."""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

SCALE = float(os.environ.get('HEALER_RES', '1.0'))
for n in ('Neck cowl', 'Shoulder wrap'):
    remove(n)
rig = bpy.data.objects['Healer Rig']

# Torso section of the body form: z, half width, front depth, back depth (as in 01_base.py).
TORSO = np.array([(1.02, 0.150, 0.095, 0.105), (1.10, 0.162, 0.100, 0.112), (1.18, 0.160, 0.098, 0.110),
                  (1.26, 0.140, 0.090, 0.092), (1.34, 0.118, 0.082, 0.076), (1.40, 0.110, 0.080, 0.072),
                  (1.48, 0.118, 0.088, 0.078), (1.56, 0.130, 0.104, 0.086), (1.63, 0.138, 0.116, 0.092),
                  (1.70, 0.148, 0.104, 0.094), (1.76, 0.156, 0.088, 0.090), (1.80, 0.154, 0.076, 0.082),
                  (1.83, 0.120, 0.064, 0.070), (1.855, 0.066, 0.054, 0.058), (1.88, 0.050, 0.050, 0.052)])


def torso_point(angle_deg, z, off):
    """A point `off` outside the torso surface. Angle 0 is the figure's left, -90 the front."""
    a = np.radians(angle_deg)
    hw = np.interp(z, TORSO[:, 0], TORSO[:, 1]) + off
    fr = np.interp(z, TORSO[:, 0], TORSO[:, 2]) + off
    bk = np.interp(z, TORSO[:, 0], TORSO[:, 3]) + off
    s = np.sin(a)
    return np.array([hw * np.cos(a), (bk if s > 0 else fr) * s, z])


def strip(name, line, width, band, folds, pin_rows, frames, mass=0.12):
    """A pleated strip of cloth `width` wide, gathered into `band`, following `line`."""
    nw = max(int(width / 0.011 * SCALE), 12)
    seg = np.linalg.norm(np.diff(line, axis=0), axis=1)
    dist = np.concatenate([[0], np.cumsum(seg)])
    nl = int(dist[-1] / (width / nw))
    even = np.linspace(0, dist[-1], nl)
    line = np.stack([np.interp(even, dist, line[:, i]) for i in range(3)], -1)
    tan = np.gradient(line, axis=0)
    tan /= np.linalg.norm(tan, axis=1)[:, None]
    out = line.copy()
    out[:, 2] = 0
    out /= np.maximum(np.linalg.norm(out, axis=1)[:, None], 1e-6)
    up = np.cross(tan, out)
    up /= np.maximum(np.linalg.norm(up, axis=1)[:, None], 1e-6)
    w = np.linspace(-0.5, 0.5, nw)
    segv = band / folds
    amp = 0.5 * np.sqrt(max((width / folds) ** 2 - segv ** 2, 0))
    zig = amp * (2 * np.abs(((w + 0.5) * folds) % 2 - 1) - 1)
    verts = (line[:, None, :] + up[:, None, :] * (w * band)[None, :, None]
             + out[:, None, :] * (zig + amp)[None, :, None])
    uv = np.stack([np.repeat(even[:, None], nw, 1), np.repeat((w * width)[None, :], nl, 0)], -1)
    ob = new_object(name, verts.reshape(-1, 3), grid_faces(nl, nw, False), 'Garments', uv.reshape(-1, 2))
    pin = ob.vertex_groups.new(name='Pin')
    idx = []
    for r in pin_rows:
        r = r % nl
        idx += list(range(r * nw, (r + 1) * nw))
    pin.add(idx, 1.0, 'REPLACE')
    cloth = ob.modifiers.new('Cloth', 'CLOTH')
    cs = cloth.settings
    cs.quality = 10
    cs.mass = mass
    cs.tension_stiffness = cs.compression_stiffness = 14
    cs.shear_stiffness = 4
    cs.bending_stiffness = 0.08
    cs.tension_damping = cs.compression_damping = 6
    cs.shear_damping = 6
    cs.bending_damping = 0.5
    cs.air_damping = 2.0
    cs.vertex_group_mass = 'Pin'
    cc = cloth.collision_settings
    cc.use_collision = True
    cc.distance_min = 0.005
    cc.collision_quality = 5
    cc.use_self_collision = True
    cc.self_distance_min = 0.003
    cc.self_friction = 12
    print('simulating', name, nl, 'x', nw, flush=True)
    simulate(ob, frames)
    ob.parent = rig
    ob.data.materials.append(bpy.data.materials['Voile'])
    sub = ob.modifiers.new('Smooth', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    return ob


def path(keys, n=400):
    k = np.array(keys, dtype=float)
    pts = []
    for t in np.linspace(0, len(k) - 1, n):
        i = min(int(t), len(k) - 2)
        f = t - i
        a, z, off = k[i] * (1 - f) + k[i + 1] * f
        pts.append(torso_point(a, z, off))
    return np.array(pts)


add_collision(bpy.data.objects['Body form'], 0.005, friction=20)
collide_before_subsurf(bpy.data.objects['Head wrap'])
for n in ('Underdress skirt', 'Head veil'):          # neither takes part here
    if n not in bpy.data.objects:
        continue
    for m in list(bpy.data.objects[n].modifiers):
        if m.type == 'COLLISION':
            bpy.data.objects[n].modifiers.remove(m)
if 'Head veil' in bpy.data.objects:
    bpy.data.objects['Head veil'].hide_render = True  # re-draped over the wraps next

# ---------------------------------------------------------------- sash
# (angle, z, clearance)
T = 0.016
sash = path([(-55, 1.345, T), (-90, 1.50, T), (-135, 1.68, T), (-165, 1.80, T + 0.004), (-180, 1.842, T + 0.006),
             (-200, 1.80, T + 0.004), (-235, 1.68, T), (-270, 1.54, T), (-305, 1.42, T), (-360, 1.385, T),
             (-450, 1.395, T + 0.012), (-540, 1.40, T + 0.012), (-630, 1.385, T + 0.012), (-720, 1.365, T + 0.012),
             (-810, 1.36, T + 0.026), (-900, 1.37, T + 0.026), (-990, 1.355, T + 0.026), (-1060, 1.335, T + 0.026)], 700)
wrap = strip('Shoulder wrap', sash, width=0.30, band=0.13, folds=12, pin_rows=(0, 1, 2, -3, -2, -1), frames=70)
collide_before_subsurf(wrap)

# ---------------------------------------------------------------- cowl
head = bpy.data.objects['Head wrap']
neck_z = 1.875
turns = []
for a in np.linspace(90, 90 - 360 * 2.3, 360):
    f = (90 - a) / (360 * 2.3)
    r = 0.074 + 0.075 * f          # each turn clears the one inside it
    z = neck_z + 0.030 - 0.060 * f
    t = np.radians(a)
    turns.append((r * np.cos(t), 0.006 + 0.92 * r * np.sin(t), z))
cowl = strip('Neck cowl', np.array(turns), width=0.26, band=0.10, folds=12, pin_rows=(0, 1, -2, -1), frames=80)

save()
render('stage4-wrap-front', 0)
render('stage4-wrap-side', 90)
render('stage4-wrap-rear', 180)
render('stage4-wrap-portrait', 15, dist=3.2, target_z=1.72, lens=85, res=(800, 1000))
print('stage 4 done')

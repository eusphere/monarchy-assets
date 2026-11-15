"""Stage 4b: the shoulder shawl.

One piece of cloth cut as a short cape: held round the base of the neck and left to fall over the
shoulders and upper arms under its own weight. It is cut much fuller than the body beneath, so it
gathers into soft folds that run down from the neck, as the shawl does in concept v008.

(A strip wound round the shoulders and tacked along its length was tried first; it sat like a
stack of stiff ruffles with a shelf at the bottom edge.)"""
import os
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

SCALE = float(os.environ.get('HEALER_RES', '1.0'))
remove('Shoulder shawl')
rig = bpy.data.objects['Healer Rig']

for n in ('Sleeve.L', 'Sleeve.R', 'Shoulder wrap'):
    collide_before_subsurf(bpy.data.objects[n])
add_collision(bpy.data.objects['Body form'], 0.005, friction=20)

dg = bpy.context.evaluated_depsgraph_get()
trees = []
for n in ('Body form', 'Shoulder wrap', 'Sleeve.L', 'Sleeve.R', 'Fit05 posed glove raised', 'Fit05 posed glove open'):
    ev = bpy.data.objects[n].evaluated_get(dg)
    m = ev.to_mesh()
    mw = ev.matrix_world
    trees.append(BVHTree.FromPolygons([tuple(mw @ v.co) for v in m.vertices], [tuple(q.vertices) for q in m.polygons]))
    ev.to_mesh_clear()


def outer_radius(theta, z):
    """How far the figure reaches from her axis in this direction at this height."""
    d = Vector((np.cos(theta), np.sin(theta), 0.0))
    o = Vector((0.0, 0.0, z)) + d * 0.7
    best = 0.05
    for tr in trees:
        hit = tr.ray_cast(o, -d, 0.7)
        if hit[0] is not None:
            best = max(best, 0.7 - hit[3])
    return best


def blur(a, n):
    for _ in range(n):
        a = 0.25 * np.roll(a, 1) + 0.5 * a + 0.25 * np.roll(a, -1)
    return a


NA = max(int(300 * SCALE), 120)
NR = max(int(40 * SCALE), 18)
NECK_Z = 1.866
SHELF = 0.13                      # runs out over the shoulder before it turns down
th = np.linspace(0, 2 * np.pi, NA, endpoint=False)
r0 = blur(np.array([outer_radius(t, NECK_Z) for t in th]), 6) + 0.005
front = np.clip(-np.sin(th), 0, 1)
# Longer on her left than her right, shorter in front so the waist and the collar still read.
length = 0.37 + 0.035 * np.cos(th) - 0.035 * front ** 2


def profile(s):
    """Outward and downward travel after `s` of cloth: shallow over the shoulder, then steep."""
    a = np.radians(12 + 53 / (1 + np.exp(-(s - SHELF) / 0.02)))
    ds = np.diff(s, prepend=0.0)
    return np.cumsum(ds * np.cos(a)), np.cumsum(ds * np.sin(a))


# Where the raised forearm or a hand stands in the way the cape is cut shorter, not pushed out.
PUSH = 0.07
fine = np.linspace(0, 1, 60)
for k, t in enumerate(th):
    s = fine * length[k]
    dr, dz = profile(s)
    for i in range(1, len(s)):
        need = outer_radius(t, NECK_Z - dz[i]) + 0.012
        if need - (r0[k] + dr[i]) > PUSH:
            length[k] = max(s[i] - 0.025, 0.12)
            break
W = 5
length = np.min([np.roll(length, j) for j in range(-W, W + 1)], axis=0)
length = blur(length, 10)

verts = np.zeros((NR, NA, 3))
uv = np.zeros((NR, NA, 2))
f = np.linspace(0, 1, NR)
for k, t in enumerate(th):
    s = f * length[k]
    dr, dz = profile(s)
    r = r0[k] + dr
    z = NECK_Z - dz
    for i in range(1, NR):
        r[i] = max(r[i], outer_radius(t, z[i]) + 0.012)
    r += 0.012 * f ** 1.5 * np.sin(22 * t + 0.6)          # seeds the folds
    verts[:, k] = np.stack([r * np.cos(t), r * np.sin(t), z], -1)
    uv[:, k] = np.stack([np.full(NR, t * 0.30), s], -1)
for i in range(1, NR):                                    # no steps between neighbouring gores
    rad = np.hypot(verts[i, :, 0], verts[i, :, 1])
    rs = np.maximum(rad, blur(rad, 3))
    verts[i, :, 0] *= rs / rad
    verts[i, :, 1] *= rs / rad

shawl = new_object('Shoulder shawl', verts.reshape(-1, 3), grid_faces(NR, NA, True), 'Garments', uv.reshape(-1, 2))
face_out(shawl)
pin = shawl.vertex_groups.new(name='Pin')
pin.add(list(range(2 * NA)), 1.0, 'REPLACE')
cloth = shawl.modifiers.new('Cloth', 'CLOTH')
cs = cloth.settings
cs.quality = 10
cs.mass = 0.16
cs.tension_stiffness = cs.compression_stiffness = 12
cs.shear_stiffness = 3
cs.bending_stiffness = 0.04
cs.tension_damping = cs.compression_damping = 6
cs.shear_damping = 6
cs.bending_damping = 0.5
cs.air_damping = 1.5
cs.vertex_group_mass = 'Pin'
cc = cloth.collision_settings
cc.use_collision = True
cc.distance_min = 0.005
cc.collision_quality = 5
cc.use_self_collision = True
cc.self_distance_min = 0.003
cc.self_friction = 8
print('simulating shawl', NR, 'x', NA, flush=True)
simulate(shawl, int(os.environ.get('HEALER_SHAWL_FRAMES', '90')))
shawl.parent = rig
shawl.data.materials.append(bpy.data.materials['Voile'])
for n in ('Sleeve.L', 'Sleeve.R'):                        # the veil, draped next, must not snag on them
    for m in list(bpy.data.objects[n].modifiers):
        if m.type == 'COLLISION':
            bpy.data.objects[n].modifiers.remove(m)
sub = shawl.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1

save()
render('stage4b-shawl-front', 0)
render('stage4b-shawl-side', 90)
render('stage4b-shawl-rear', 180)
render('stage4b-shawl-portrait', 15, dist=3.2, target_z=1.72, lens=85, res=(800, 1000))
print('stage 4b done')

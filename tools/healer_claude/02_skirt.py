"""Stage 2: the pleated underdress skirt.

A gathered tube, about twice as full as the hips at the top and wider at the
hem, hangs from a pinned ring below the waist. It is cut longer than the
figure, so a slowly rising floor makes the hem pool and crumple."""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

SCALE = float(os.environ.get('HEALER_RES', '1.0'))
C = int(360 * SCALE)          # columns round the body
R = int(130 * SCALE)          # rows waist to hem
PLEATS = 60
TOP_Z = 1.31
DROP = 0.30                   # the floor starts this far below z=0 and rises
EXTRA = 0.20                  # cloth beyond floor length, pooled at the hem
TRAIN = 0.16                  # more again at the back
FRAMES = 150

NAME = 'Underdress skirt'
remove(NAME)
remove('Sim floor')
body = bpy.data.objects['Body form']
add_collision(body, 0.005)

u = np.arange(C) / C
theta = 2 * np.pi * u
v = np.linspace(0, 1, R)
verts = np.zeros((R, C, 3))
# Waist ring follows the body section at TOP_Z (half width, front, back).
hw, fr, bk = 0.132, 0.090, 0.088
s, c = np.sin(theta), np.cos(theta)
top_x = (hw + 0.010) * c
top_y = np.where(s > 0, bk + 0.010, fr + 0.010) * s
back = np.clip(s, 0, 1) ** 2      # 1 at the centre back
for r in range(R):
    t = v[r]
    # Radius grows from the waist ring to a wide hem; the back sweeps out further.
    hem_r = 0.40 + 0.10 * back
    x = top_x * (1 - t) + hem_r * c * t
    y = top_y * (1 - t) + (hem_r * s + 0.05 * back) * t
    # Pleats: deep at the gathered waist, shallower toward the hem.
    amp = 0.0075 * (1 - t) + 0.011 * t
    rad = np.sqrt(x * x + y * y)
    k = 1 + amp * np.sin(PLEATS * theta + 0.6 * np.sin(3 * theta)) / np.maximum(rad, 1e-4)
    z = TOP_Z - t * (TOP_Z + DROP - 0.03 + 0 * back)
    verts[r, :, 0] = x * k
    verts[r, :, 1] = y * k
    verts[r, :, 2] = z
# The back is cut longer: push its lower rows outward instead of down.
length = TOP_Z + EXTRA
for r in range(R):
    t = v[r]
    verts[r, :, 1] += TRAIN * back * t ** 2
uv = np.stack([np.repeat(u[None, :], R, 0) * 3.0, np.repeat(v[:, None], C, 1) * length], -1)
skirt = new_object(NAME, verts.reshape(-1, 3), grid_faces(R, C, True), 'Garments', uv.reshape(-1, 2))

pin = skirt.vertex_groups.new(name='Pin')
pin.add(list(range(2 * C)), 1.0, 'REPLACE')

floor = new_object('Sim floor', [(-4, -4, 0), (4, -4, 0), (4, 4, 0), (-4, 4, 0)], [(0, 1, 2, 3)], 'Sim')
floor.location.z = -DROP
floor.hide_render = True
add_collision(floor, 0.004, friction=25)

cloth = skirt.modifiers.new('Cloth', 'CLOTH')
cs = cloth.settings
cs.quality = 8
cs.mass = 0.18
cs.tension_stiffness = cs.compression_stiffness = 18
cs.shear_stiffness = 6
cs.bending_stiffness = 0.25
cs.tension_damping = cs.compression_damping = 6
cs.shear_damping = 6
cs.bending_damping = 0.5
cs.air_damping = 1.2
cs.vertex_group_mass = 'Pin'
cc = cloth.collision_settings
cc.use_collision = True
cc.distance_min = 0.006
cc.collision_quality = 4
cc.use_self_collision = True
cc.self_distance_min = 0.0025
cc.self_friction = 8


def rise(f):
    t = min(max((f - 15) / 90, 0), 1)
    floor.location.z = -DROP * (1 - t * t * (3 - 2 * t))


print('simulating skirt', C, 'x', R, flush=True)
simulate(skirt, FRAMES, rise)
floor.location.z = 0
skirt.parent = bpy.data.objects['Healer Rig']

if 'Voile' not in bpy.data.materials:
    m = bpy.data.materials.new('Voile')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.86, 0.80, 0.69, 1)
    b.inputs['Roughness'].default_value = 0.7
    b.inputs['Sheen Weight'].default_value = 0.5
skirt.data.materials.append(bpy.data.materials['Voile'])
sub = skirt.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1

save()
render('stage2-skirt-front', 0)
render('stage2-skirt-side', 90)
print('stage 2 done')

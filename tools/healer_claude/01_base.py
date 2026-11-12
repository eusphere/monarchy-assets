"""Stage 1: new file with the rig, gloves, head and jewelry from healer.blend,
a slender body form for cloth to fall on, and concept-matched lighting."""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = 'Healer'

# ---------------------------------------------------------------- carry over
KEEP = ['Healer Rig', 'Fit05 posed glove raised', 'Fit05 posed glove open',
        'Healer - pearl face', 'Healer - flat linked plaque necklace',
        'Healer - cuff to cuff plaque chain', 'Healer - linked circlet and bow fasteners',
        'Fit04 tailored glove cuff raised', 'Fit04 tailored glove cuff open']
with bpy.data.libraries.load(SOURCE) as (src, dst):
    dst.objects = [n for n in KEEP if n in src.objects]
    dst.actions = [n for n in src.actions if n.startswith('Healer |')]
rig = None
for ob in dst.objects:
    name = ob.name
    if ob.type == 'ARMATURE':
        collection('Rig').objects.link(ob)
        rig = ob
    elif 'glove' in name and 'cuff' not in name:
        collection('Body').objects.link(ob)
    elif 'pearl face' in name:
        collection('Body').objects.link(ob)
        ob.hide_render = ob.hide_viewport = False
    else:
        collection('Jewelry').objects.link(ob)
for a in dst.actions:
    a.use_fake_user = True
rig.data.pose_position = 'REST'   # garments are built and draped in the rest gesture
rig.show_in_front = False
rig.hide_render = True
bones = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in rig.data.bones}

# ---------------------------------------------------------------- body form
N = 48


def ring_torso(z, hw, front, back, cx=0.0, cy=0.0):
    out = []
    for i in range(N):
        t = 2 * math.pi * i / N
        s = math.sin(t)
        # Slightly squared ellipse so the front and back are flatter than the sides.
        c = math.copysign(abs(math.cos(t)) ** 0.9, math.cos(t))
        y = (back if s > 0 else front) * math.copysign(abs(s) ** 0.9, s)
        out.append((cx + hw * c, cy + y, z))
    return out


def ring_about(p, axis, r):
    axis = axis / np.linalg.norm(axis)
    ref = np.array([0, 1, 0]) if abs(axis[1]) < 0.9 else np.array([1, 0, 0])
    u = np.cross(axis, ref)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    return [tuple(p + r * (math.cos(2 * math.pi * i / N) * u + math.sin(2 * math.pi * i / N) * v))
            for i in range(N)]


def loft(rings):
    verts = [p for r in rings for p in r]
    faces = grid_faces(len(rings), N, True)
    faces.append(tuple(range(N - 1, -1, -1)))
    last = (len(rings) - 1) * N
    faces.append(tuple(range(last, last + N)))
    return verts, faces


parts = []
# z, half width, front depth, back depth
torso = [(1.02, 0.150, 0.095, 0.105), (1.10, 0.162, 0.100, 0.112), (1.18, 0.160, 0.098, 0.110),
         (1.26, 0.140, 0.090, 0.092), (1.34, 0.118, 0.082, 0.076), (1.40, 0.110, 0.080, 0.072),
         (1.48, 0.118, 0.088, 0.078), (1.56, 0.130, 0.104, 0.086), (1.63, 0.138, 0.116, 0.092),
         (1.70, 0.142, 0.104, 0.094), (1.76, 0.140, 0.086, 0.088), (1.80, 0.118, 0.072, 0.078),
         (1.84, 0.075, 0.058, 0.064), (1.88, 0.050, 0.050, 0.052)]
parts.append(loft([ring_torso(z, hw, f, b) for z, hw, f, b in torso]))


def limb(points, radii):
    rings = []
    for i, (p, r) in enumerate(zip(points, radii)):
        a = points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]
        rings.append(ring_about(p, a, r))
    return loft(rings)


for s in ('R', 'L'):
    sh, el = bones['UpperArm.' + s]
    wr = bones['Hand.' + s][0]
    hand_tip = bones['Hand.' + s][1]
    parts.append(limb([sh + (sh - el) * 0.04, sh, (sh + el) / 2, el, (el + wr) / 2, wr,
                       wr + (hand_tip - wr) * 0.15],
                      [0.030, 0.047, 0.041, 0.036, 0.031, 0.025, 0.022]))
    hip, knee = bones['Thigh.' + s]
    ankle = bones['Foot.' + s][0]
    toe = ankle + np.array([0, -0.16, -0.05])
    parts.append(limb([hip + np.array([0, 0, 0.05]), hip, (hip + knee) / 2, knee, (knee + ankle) / 2,
                       ankle, np.array([ankle[0], ankle[1], 0.02])],
                      [0.070, 0.082, 0.068, 0.052, 0.046, 0.036, 0.034]))
    parts.append(limb([ankle + np.array([0, 0.04, -0.03]), (ankle + toe) / 2 + np.array([0, 0, -0.01]), toe],
                      [0.036, 0.034, 0.022]))

verts, faces = [], []
for v, f in parts:
    off = len(verts)
    verts += v
    faces += [tuple(i + off for i in face) for face in f]
body = new_object('Body form', verts, faces, 'Body')
body.parent = rig
sub = body.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1

lining = bpy.data.materials.new('Body lining ivory')
lining.use_nodes = True
b = lining.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.80, 0.74, 0.64, 1)
b.inputs['Roughness'].default_value = 0.8
body.data.materials.append(lining)

# ---------------------------------------------------------------- team accent
accent = bpy.data.materials.get('TeamAccent')
assert accent, 'TeamAccent must come across with the jewelry'

# ---------------------------------------------------------------- studio
floor_mat = bpy.data.materials.new('Studio backdrop')
floor_mat.use_nodes = True
fb = floor_mat.node_tree.nodes['Principled BSDF']
fb.inputs['Base Color'].default_value = (0.052, 0.040, 0.033, 1)
fb.inputs['Roughness'].default_value = 0.95
# Seamless backdrop: floor sweeping up into a wall behind the figure.
prof = [(-14, 0.0), (5.0, 0.0)] + [(5.0 + 2.5 * math.sin(a), 2.5 - 2.5 * math.cos(a))
                                   for a in np.linspace(0, math.pi / 2, 12)[1:]] + [(7.5, 12)]
bv, bf = [], []
for y, z in prof:
    bv += [(-12, y, z), (12, y, z)]
for i in range(len(prof) - 1):
    bf.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
backdrop = new_object('Studio backdrop', bv, bf, 'Studio')
backdrop.data.materials.append(floor_mat)


def area(name, loc, target, energy, size, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name, d)
    collection('Studio').objects.link(o)
    o.location = loc
    from mathutils import Vector
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


area('Key', (-3.2, -4.2, 4.6), (0, 0, 1.3), 1500, 4.0, (1.0, 0.95, 0.88))
area('Fill', (3.5, -3.5, 1.6), (0, 0, 1.0), 220, 5.0, (0.92, 0.94, 1.0))
area('Rim', (2.2, 3.6, 4.2), (0, 0, 1.5), 700, 2.5, (1.0, 0.93, 0.85))

world = bpy.data.worlds.new('Studio world')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.020, 0.016, 0.014, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
sc.world = world

cam = bpy.data.objects.new('Hero camera', bpy.data.cameras.new('Hero camera'))
collection('Studio').objects.link(cam)
sc.camera = cam
sc.render.engine = 'BLENDER_EEVEE_NEXT'
sc.eevee.use_shadows = True
sc.eevee.use_raytracing = False
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'PNG'
sc.render.film_transparent = False

save()
render('stage1-body-front', 0)
render('stage1-body-side', 90)
print('stage 1 done')

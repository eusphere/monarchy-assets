"""Stage 8: posture.

The figure was built bolt upright and symmetric. This bends the whole figure -
body, garments, jewelry and the rig's rest pose together, so everything still
fits - into a quiet contrapposto: weight on one hip, shoulders answering the
other way and sloping, hips a little forward, head inclined and tipped toward
the raised hand.

It moves geometry, so it must run only once; the rig records that it has."""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
assert not rig.get('claude_posture'), 'posture already applied to this file'


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def gauss(z, mid, width):
    return np.exp(-0.5 * ((z - mid) / width) ** 2)


HIP_SHIFT = 0.034          # hips toward the figure's left
SHOULDER_BACK = 0.016      # shoulders travel the other way
HIP_FORWARD = 0.020
CHEST_BACK = 0.012
SHOULDER_TILT = np.radians(2.0)     # figure's left shoulder lower
SHOULDER_DROP = 0.003               # shoulders stay square; she is not meek
HEAD_TILT = np.radians(-6.5)        # crown toward the raised (right) hand
HEAD_NOD = np.radians(6.0)          # face inclined downward


def warp(p):
    p = np.asarray(p, dtype=float).copy()
    x, y, z = p[:, 0].copy(), p[:, 1].copy(), p[:, 2].copy()
    ground = sstep(0.10, 0.60, z)                 # the pooled hem stays where it lies
    # Sloping shoulders: the arms and everything on them come down with the shoulder points.
    drop = SHOULDER_DROP * sstep(0.07, 0.16, np.abs(x)) * sstep(1.00, 1.30, z) * (1 - sstep(1.84, 1.93, z))
    z = z - drop
    # Shoulder girdle tilts about a front-to-back axis through the chest.
    w = sstep(1.38, 1.66, p[:, 2])
    a = SHOULDER_TILT * w
    dx, dz = x, z - 1.60
    x = np.where(w > 0, dx * np.cos(a) + dz * np.sin(a), x)
    z = np.where(w > 0, 1.60 - dx * np.sin(a) + dz * np.cos(a), z)
    # Head: tip and incline about the base of the neck.
    w = sstep(1.85, 1.96, p[:, 2])
    a = HEAD_TILT * w
    dx, dz = x, z - 1.86
    x2 = dx * np.cos(a) + dz * np.sin(a)
    z2 = 1.86 - dx * np.sin(a) + dz * np.cos(a)
    b = HEAD_NOD * w
    dy, dz = y - 0.0, z2 - 1.86
    y2 = dy * np.cos(b) - dz * np.sin(b)
    z3 = 1.86 + dy * np.sin(b) + dz * np.cos(b)
    x, y, z = x2, y2, z3
    # The S-curve: hips out to one side and forward, ribcage back over them.
    zz = p[:, 2]
    x = x + ground * (HIP_SHIFT * gauss(zz, 1.05, 0.34) - SHOULDER_BACK * gauss(zz, 1.70, 0.20))
    y = y + ground * (-HIP_FORWARD * gauss(zz, 1.12, 0.30) + CHEST_BACK * gauss(zz, 1.62, 0.20))
    return np.column_stack([x, y, z])


SKIP = {'Studio backdrop', 'Sim floor'}
done = set()
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name in SKIP or ob.data.name in done:
        continue
    done.add(ob.data.name)
    assert ob.data.shape_keys is None, ob.name
    set_coords(ob, warp(coords(ob)))

# The rig's rest pose follows, so the bones stay inside the body they drive.
hidden = rig.hide_viewport
rig.hide_viewport = False
rig.hide_set(False)
activate(rig)
bpy.ops.object.mode_set(mode='EDIT')
for eb in rig.data.edit_bones:
    h, t = warp([tuple(eb.head), tuple(eb.tail)])
    eb.head, eb.tail = h, t
bpy.ops.object.mode_set(mode='OBJECT')
rig.hide_viewport = hidden
rig['claude_posture'] = 1

save()
render('stage8-front', 0)
render('stage8-three-quarter', 28)
render('stage8-side', 90)
render('stage8-rear', 180)
render('stage8-portrait', 18, dist=2.6, target_z=1.92, lens=85, res=(900, 1125), samples=64)
print('stage 8 done')

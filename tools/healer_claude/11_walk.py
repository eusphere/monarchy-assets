"""Stage 11: a new Walk.

The inherited walk bounced: the pelvis rose and fell nearly 5 cm a step, the
spine twisted hard, the spine and chest bones slid along their length (the
torso visibly stretching), the arms swung, and the hem bones travelled half a
metre. None of that suits her.

She glides. The head does not move at all relative to the ground plane, the
shoulders stay level, the hands hold the blessing gesture, and only the cloth
gives away that there are steps underneath. The old action is kept as
`Healer | Walk legacy`."""
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
rig.data.pose_position = 'POSE'
sc = bpy.context.scene
NAME = 'Healer | Walk'
old = bpy.data.actions.get(NAME)
tracks = set()
if old and not old.get('claude_glide'):
    tracks = {fc.data_path.split('"')[1] for fc in old.fcurves if 'pose.bones' in fc.data_path}
    legacy = bpy.data.actions.get(NAME + ' legacy')
    if legacy:
        bpy.data.actions.remove(old)
    else:
        old.name = NAME + ' legacy'
        old.use_fake_user = True
elif old:
    tracks = {fc.data_path.split('"')[1] for fc in old.fcurves if 'pose.bones' in fc.data_path}
    bpy.data.actions.remove(old)
act = bpy.data.actions.new(NAME)
act.use_fake_user = True
act['claude_glide'] = 1
if not rig.animation_data:
    rig.animation_data_create()
rig.animation_data.action = act

START, END = 1, 33                       # frame 33 repeats frame 1; two steps per cycle
rest = {b.name: b.matrix_local.to_3x3() for b in rig.data.bones}


def world_rot(bone, yaw=0.0, pitch=0.0, roll=0.0):
    """A small rotation given about world axes (degrees): yaw about Z, pitch about X, roll about Y."""
    R = (Matrix.Rotation(math.radians(yaw), 3, 'Z') @ Matrix.Rotation(math.radians(pitch), 3, 'X')
         @ Matrix.Rotation(math.radians(roll), 3, 'Y'))
    M = rest[bone]
    return (M.inverted() @ R @ M).to_quaternion()


def world_loc(bone, v):
    return rest[bone].inverted() @ Vector(v)


for f in range(START, END + 1):
    p = 2 * math.pi * (f - START) / (END - START)        # one full cycle
    step = math.sin(2 * p)                               # twice per cycle
    stride = math.sin(p)                                 # once per cycle, left/right
    pose = {n: (Quaternion(), Vector((0, 0, 0))) for n in tracks}
    # Hips: the faintest turn and drift; no rise and fall to speak of.
    pose['Pelvis'] = (world_rot('Pelvis', yaw=1.6 * stride, roll=0.5 * stride),
                      world_loc('Pelvis', (0.005 * stride, 0.0, 0.003 * math.cos(2 * p))))
    # The spine takes the turn back out, so shoulders and head stay square to her path.
    pose['Spine'] = (world_rot('Spine', yaw=-0.9 * stride, roll=-0.3 * stride), Vector((0, 0, 0)))
    pose['Chest'] = (world_rot('Chest', yaw=-0.7 * stride, roll=-0.2 * stride), Vector((0, 0, 0)))
    pose['Head'] = (world_rot('Head', yaw=0.0), Vector((0, 0, 0)))
    # Cloth: the skirt answers each step a moment late; the hem trails and shifts a little.
    lag = math.sin(2 * p - 0.9)
    pose['Skirt'] = (world_rot('Skirt', pitch=1.3 * lag, roll=0.9 * math.sin(p - 0.7)), Vector((0, 0, 0)))
    pose['Hem.L'] = (Quaternion(), world_loc('Hem.L', (0.0, 0.012 * math.sin(p - 1.2), 0.0)))
    pose['Hem.R'] = (Quaternion(), world_loc('Hem.R', (0.0, -0.012 * math.sin(p - 1.2), 0.0)))
    pose['Chain.Sag'] = (world_rot('Chain.Sag', pitch=1.0 * lag, roll=0.8 * math.sin(p - 1.0)), Vector((0, 0, 0)))
    for name, (q, loc) in pose.items():
        pb = rig.pose.bones[name]
        if pb.rotation_mode == 'QUATERNION':
            pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=f)
        else:
            pb.rotation_euler = q.to_euler(pb.rotation_mode)
            pb.keyframe_insert('rotation_euler', frame=f)
        pb.location = loc
        pb.keyframe_insert('location', frame=f)
for fc in act.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'
print('walk rebuilt:', len(act.fcurves), 'curves over', len(tracks), 'bones', flush=True)

rig.animation_data.action = bpy.data.actions['Healer | Idle']
sc.frame_set(1)
save()
rig.animation_data.action = act
for f in (1, 9, 17, 25):
    sc.frame_set(f)
    render('anim/anim-walk-f%02d' % f, 22, res=(520, 1020), samples=24)
sc.frame_set(9)
render('anim/anim-walk-f09-rear', 160, res=(520, 1020), samples=24)
render('anim/anim-walk-f09-side', 90, res=(520, 1020), samples=24)
print('stage 11 done')

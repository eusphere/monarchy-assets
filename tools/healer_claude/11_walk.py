"""Stage 11: a new Walk.

The inherited walk bounced: the pelvis rose and fell nearly 5 cm a step, the
spine twisted hard, the spine and chest bones slid along their length (the
torso visibly stretching), the arms swung, and the hem bones travelled half a
metre. None of that suits her.

She walks like a runway model, unhurried. The legs really step, and show as knees
pressing the skirt forward; the hips turn and settle a little over each
standing leg; the spine gives that turn back so the head stays level; the
arms hang at her sides and swing with quiet confidence; each foot lands on
the line of travel, as on a runway; the hem trails behind. The old action is kept as
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
# Arms at her sides: the Idle action already carries that pose, so the walk starts from it.
ARM_PARTS = ('Clavicle', 'UpperArm', 'Forearm', 'Hand', 'Index', 'Middle', 'Ring', 'Little', 'Thumb')
if not rig.animation_data:
    rig.animation_data_create()
rig.animation_data.action = bpy.data.actions['Healer | Idle']
sc.frame_set(1)
bpy.context.view_layer.update()
arm_base = {}
for n in tracks:
    if n.split('.')[0] in ARM_PARTS:
        pb = rig.pose.bones[n]
        arm_base[n] = (pb.rotation_quaternion.copy() if pb.rotation_mode == 'QUATERNION'
                       else pb.rotation_euler.to_quaternion())
act = bpy.data.actions.new(NAME)
act.use_fake_user = True
act['claude_glide'] = 1
if not rig.animation_data:
    rig.animation_data_create()
rig.animation_data.action = act

START, END = 1, 43                       # 1.75 s a cycle: a measured runway pace; frame 43 repeats frame 1
rest = {b.name: b.matrix_local.to_3x3() for b in rig.data.bones}


def world_rot(bone, yaw=0.0, pitch=0.0, roll=0.0):
    """A rotation given about world axes (degrees): yaw about Z, pitch about X, roll about Y.
    She faces -Y, so a negative pitch swings a hanging limb forward."""
    R = (Matrix.Rotation(math.radians(yaw), 3, 'Z') @ Matrix.Rotation(math.radians(pitch), 3, 'X')
         @ Matrix.Rotation(math.radians(roll), 3, 'Y'))
    M = rest[bone]
    return (M.inverted() @ R @ M).to_quaternion()


def world_loc(bone, v):
    return rest[bone].inverted() @ Vector(v)


STRIDE = 15.0        # thigh swing, degrees each way
ARM_SWING = 7.5      # upper arm, degrees each way: confident, not emphatic
for f in range(START, END + 1):
    p = 2 * math.pi * (f - START) / (END - START)
    s = math.sin(p)                      # +1: left leg fully forward; -1: right leg fully forward
    c = math.cos(p)                      # > 0 while the left leg travels forward
    pose = {n: (Quaternion(), Vector((0, 0, 0))) for n in tracks}
    # Legs. Each swings from the hip and folds at the knee only while it travels forward.
    # Each foot is set down on the line of travel, crossing slightly in front of the other.
    pose['Thigh.L'] = (world_rot('Thigh.L', pitch=-STRIDE * s - 2, roll=5.0 * max(s, 0)), Vector((0, 0, 0)))
    pose['Thigh.R'] = (world_rot('Thigh.R', pitch=STRIDE * s - 2, roll=-5.0 * max(-s, 0)), Vector((0, 0, 0)))
    pose['Shin.L'] = (world_rot('Shin.L', pitch=4 + 26 * max(c, 0) ** 1.5), Vector((0, 0, 0)))
    pose['Shin.R'] = (world_rot('Shin.R', pitch=4 + 26 * max(-c, 0) ** 1.5), Vector((0, 0, 0)))
    # Hips: the leading hip comes forward, weight settles over the standing leg, and the body
    # sinks very slightly at full stride. Small, but enough to read as walking.
    pose['Pelvis'] = (world_rot('Pelvis', yaw=-6.0 * s, roll=3.2 * c),
                      world_loc('Pelvis', (-0.021 * c, 0.0, -0.007 + 0.007 * math.cos(2 * p))))
    # The spine gives the turn back, so shoulders and head stay square and level: the poise.
    # The shoulders even turn a touch against the hips, as they do when the arms swing.
    pose['Spine'] = (world_rot('Spine', yaw=3.6 * s, roll=-1.9 * c), Vector((0, 0, 0)))
    pose['Chest'] = (world_rot('Chest', yaw=3.4 * s, roll=-1.3 * c), Vector((0, 0, 0)))
    # Chin level, gaze ahead: the head is lifted out of its resting incline and does not turn.
    pose['Head'] = (world_rot('Head', yaw=-1.0 * s, pitch=-3.0), Vector((0, 0, 0)))
    # Arms hang at her sides and swing from the shoulder against the legs. The elbow gives a
    # little as each arm comes forward (easing toward the rest pose bends it).
    for n, q in arm_base.items():
        pose[n] = (q.copy(), Vector((0, 0, 0)))
    for side, fwd in (('L', -s), ('R', s)):                 # fwd > 0 while this arm is forward
        ua, fa = 'UpperArm.' + side, 'Forearm.' + side
        # The Idle pose holds the arms a little behind her; bring them under the shoulder first.
        pose[ua] = (world_rot(ua, pitch=-ARM_SWING * fwd - 11.0) @ arm_base[ua], Vector((0, 0, 0)))
        bend = 0.05 + 0.07 * max(math.sin(p - 0.5) * (-1 if side == 'L' else 1), 0)
        pose[fa] = (arm_base[fa].slerp(Quaternion(), bend), Vector((0, 0, 0)))
    # Cloth: the skirt follows each step a moment late; the hem trails behind her and drags
    # from side to side as each leg pulls it.
    lag = math.sin(2 * p - 0.9)
    pose['Skirt'] = (world_rot('Skirt', pitch=1.8 * lag + 1.0, roll=1.6 * math.sin(p - 0.7)), Vector((0, 0, 0)))
    pose['Hem.L'] = (Quaternion(), world_loc('Hem.L', (0.008 * math.sin(p - 1.0), 0.050 - 0.035 * math.sin(p - 0.6), 0.0)))
    pose['Hem.R'] = (Quaternion(), world_loc('Hem.R', (0.008 * math.sin(p - 1.0), 0.050 + 0.035 * math.sin(p - 0.6), 0.0)))
    pose['Chain.Sag'] = (world_rot('Chain.Sag', pitch=1.6 * lag, roll=1.8 * math.sin(p - 1.0)), Vector((0, 0, 0)))
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
for f in (1, 11, 22, 32):
    sc.frame_set(f)
    render('anim/anim-walk-f%02d' % f, 22, res=(520, 1020), samples=24)
sc.frame_set(11)
render('anim/anim-walk-f11-rear', 160, res=(520, 1020), samples=24)
render('anim/anim-walk-f11-side', 90, res=(520, 1020), samples=24)
print('stage 11 done')

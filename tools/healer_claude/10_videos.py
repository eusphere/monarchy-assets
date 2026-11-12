"""Stage 10: preview videos of the three animations (does not change the model).

Walk and Idle are looped; each clip is an H.264 .mp4 at the scene's 24 fps."""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

sc = bpy.context.scene
rig = bpy.data.objects['Healer Rig']
rig.data.pose_position = 'POSE'
cam = bpy.data.objects['Hero camera']
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 540, 1060
sc.eevee.taa_render_samples = int(os.environ.get('HEALER_VIDEO_SAMPLES', '12'))
sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format = 'MPEG4'
sc.render.ffmpeg.codec = 'H264'
sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.ffmpeg.audio_codec = 'NONE'
os.makedirs(os.path.join(RENDERS, 'anim'), exist_ok=True)


def aim(angle, dist=7.2, target_z=1.12, lens=85):
    if abs(angle) > 100:
        lens, dist = lens * 4.4 / dist, 4.4
    a = math.radians(angle)
    cam.location = (math.sin(a) * dist, -math.cos(a) * dist, target_z)
    cam.rotation_euler = (math.radians(90), 0, a)
    cam.data.lens = lens


def clip(action_name, tag, angle, loops):
    act = bpy.data.actions[action_name]
    rig.animation_data.action = act
    start, end = int(act.frame_range[0]), int(act.frame_range[1])
    added = []
    if loops > 1:
        for fc in act.fcurves:
            if not any(m.type == 'CYCLES' for m in fc.modifiers):
                added.append((fc, fc.modifiers.new('CYCLES')))
    sc.frame_start = start
    sc.frame_end = start + (end - start) * loops - (1 if loops > 1 else 0)
    aim(angle)
    sc.render.filepath = os.path.join(RENDERS, 'anim', 'healer-%s.mp4' % tag)
    bpy.ops.render.render(animation=True)
    for fc, m in added:
        fc.modifiers.remove(m)
    print('clip', tag, sc.frame_start, sc.frame_end, flush=True)


WANT = os.environ.get('HEALER_CLIPS', 'walk,walk-rear,idle,heal').split(',')
CLIPS = {'walk': ('Healer | Walk', 25, 3), 'walk-rear': ('Healer | Walk', 150, 3),
         'walk-side': ('Healer | Walk', 90, 3),
         'idle': ('Healer | Idle', 25, 1), 'heal': ('Healer | Heal', 25, 1)}
for tag in WANT:
    clip(CLIPS[tag][0], tag, CLIPS[tag][1], CLIPS[tag][2])
print('stage 10 done')

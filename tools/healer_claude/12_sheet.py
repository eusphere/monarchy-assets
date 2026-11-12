"""Contact sheets: every Nth frame of an animation laid out in one image, so motion can be
read from a still. Does not change the model.

  HEALER_SHEETS="walk:25,walk:90,walk:160"   action tag : camera angle
  HEALER_SHEET_STEP=2                         frame step"""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

sc = bpy.context.scene
rig = bpy.data.objects['Healer Rig']
rig.data.pose_position = 'POSE'
cam = bpy.data.objects['Hero camera']
sc.camera = cam
W, H = 250, 490
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 8
sc.render.image_settings.file_format = 'PNG'
ACTIONS = {'walk': 'Healer | Walk', 'idle': 'Healer | Idle', 'heal': 'Healer | Heal', 'legacy': 'Healer | Walk legacy'}
STEP = int(os.environ.get('HEALER_SHEET_STEP', '2'))
tmp = os.path.join(RENDERS, 'anim', '_frames')
os.makedirs(tmp, exist_ok=True)


def aim(angle, dist=7.2, target_z=1.12, lens=85):
    if abs(angle) > 100:
        lens, dist = lens * 4.4 / dist, 4.4
    a = math.radians(angle)
    cam.location = (math.sin(a) * dist, -math.cos(a) * dist, target_z)
    cam.rotation_euler = (math.radians(90), 0, a)
    cam.data.lens = lens


for spec in os.environ.get('HEALER_SHEETS', 'walk:25,walk:90').split(','):
    tag, angle = spec.split(':')
    act = bpy.data.actions[ACTIONS[tag]]
    rig.animation_data.action = act
    aim(float(angle))
    frames = list(range(int(act.frame_range[0]), int(act.frame_range[1]), STEP))
    tiles = []
    for f in frames:
        sc.frame_set(f)
        path = os.path.join(tmp, 'f.png')
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(path)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
        bpy.data.images.remove(img)
        tiles.append(px)
    cols = 8
    rows = math.ceil(len(tiles) / cols)
    sheet = np.zeros((rows * H, cols * W, 4), dtype=np.float32)
    sheet[..., 3] = 1
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * H            # image rows run bottom-up
        sheet[y0:y0 + H, c * W:(c + 1) * W] = t
    out = bpy.data.images.new('sheet', cols * W, rows * H, alpha=False)
    out.pixels.foreach_set(sheet.ravel())
    out.filepath_raw = os.path.join(RENDERS, 'anim', 'sheet-%s-%s.png' % (tag, angle))
    out.file_format = 'PNG'
    out.save()
    bpy.data.images.remove(out)
    print('sheet', tag, angle, len(tiles), 'frames', flush=True)
print('sheets done')

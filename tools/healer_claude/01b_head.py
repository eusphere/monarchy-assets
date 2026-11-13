"""Stage 1b: a real head and neck.

The head carried over from healer.blend is a featureless egg. This replaces
its mesh with the head and neck cut from Blender Studio's CC0 Human Base
Meshes (see 00_extract_head.py), scaled and placed to sit where the egg sat,
with the neck drawn down to meet the shoulders of this figure, who is taller
and longer in the neck than the base mesh.

The object keeps its name, so every later stage finds a head where it expects
one. Landmarks (chin, mouth, nose, lip edges) are stored on it for the mask."""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
head = bpy.data.objects['Healer - pearl face']
assert not head.get('claude_real_head'), 'head already replaced'
egg = coords(head)
crown_z = egg[:, 2].max()
upper = egg[egg[:, 2] > crown_z - 0.15]
egg_x = float(np.median(upper[:, 0]))
strip = np.abs(egg[:, 0] - egg_x) < 0.012
zs = np.arange(crown_z - 0.03, crown_z - 0.34, -0.005)
front = np.array([egg[strip & (np.abs(egg[:, 2] - z) < 0.006)][:, 1].min() for z in zs])
egg_chin = float(zs[np.where(front <= front.min() + 0.030)[0][-1]])
egg_forehead = float(front.min())
NECK_BASE = 1.842                               # where the bodice's neckline will sit

with bpy.data.libraries.load(os.path.join(ROOT, 'src', 'healer-head-base.blend')) as (src, dst):
    dst.objects = ['Head base']
base = dst.objects[0]
b = coords(base)
faces = [tuple(p.vertices) for p in base.data.polygons]
top = b[:, 2].max()
dz = top - b[:, 2]


def profile(pts, lo, hi, step=0.002):
    """Front-most y down the centre line, as (dz from the crown, y)."""
    out = []
    for d in np.arange(lo, hi, step):
        s = pts[(np.abs((top - pts[:, 2]) - d) < step) & (np.abs(pts[:, 0]) < 0.006)]
        if len(s):
            out.append((d, s[:, 1].min()))
    return np.array(out)


pf = profile(b, 0.02, 0.26)
nose_i = int(np.argmin(pf[:, 1]))
nose_dz = pf[nose_i, 0]
# The chin is the last point down the face before the profile falls away to the throat.
chin_dz = float(pf[(pf[:, 0] > nose_dz) & (pf[:, 1] <= pf[nose_i, 1] + 0.035), 0].max())
print('profile nose-to-chin:', ' '.join('%.3f:%.4f' % (d, y) for d, y in pf if nose_dz <= d <= chin_dz + 0.01), flush=True)
# Mouth line: the deepest point between the two lips, in the middle of nose-to-chin.
mid = pf[(pf[:, 0] > nose_dz + 0.022) & (pf[:, 0] < chin_dz - 0.020)]
# The mouth is the hollow with a lip standing proud on each side: score every point by how far
# it sits behind the most forward point above it and the most forward point below it.
best, depth = 1, -1.0
for i in range(1, len(mid) - 1):
    d = min(mid[i, 1] - mid[:i, 1].min(), mid[i, 1] - mid[i + 1:, 1].min())
    if d > depth:
        best, depth = i, d
print('mouth hollow depth %.4f from %d profile points' % (depth, len(mid)), flush=True)
mouth_dz = float(mid[best, 0])
up = mid[:best]
lo_ = mid[best + 1:]
upper_peak = float(up[np.argmin(up[:, 1]), 0]) if len(up) else mouth_dz - 0.007
lower_peak = float(lo_[np.argmin(lo_[:, 1]), 0]) if len(lo_) else mouth_dz + 0.008
# ---- Reshape the features on the base mesh, before it is scaled into place.
# A slimmer, shorter nose with a narrower base; thin, flat lips; a slightly narrower jaw.
g = lambda a_, s_: np.exp(-(a_ / s_) ** 2)        # noqa: E731
facing = (b[:, 1] < pf[nose_i, 1] + 0.060).astype(float)
nose_m = g(b[:, 0], 0.024) * g(dz - (nose_dz + 0.004), 0.019) * facing
b[:, 0] *= 1 - 0.26 * nose_m                                           # narrower nostrils and tip
tip_m = g(b[:, 0], 0.016) * g(dz - nose_dz, 0.012) * facing
b[:, 2] += 0.0030 * tip_m                                              # a shorter, slightly lifted tip
b[:, 1] += 0.0020 * tip_m                                              # and a little less projection
bridge_m = g(b[:, 0], 0.007) * g(dz - (nose_dz - 0.032), 0.020) * facing
b[:, 1] -= 0.0030 * bridge_m                                           # a higher, straighter bridge
b[:, 0] *= 1 - 0.18 * g(b[:, 0], 0.014) * g(dz - (nose_dz - 0.030), 0.022) * facing
dz = top - b[:, 2]
lip_m = g(b[:, 0], 0.032) * g(dz - mouth_dz, 0.012) * facing
b[:, 2] = top - (mouth_dz + (dz - mouth_dz) * (1 - 0.30 * lip_m))       # thinner lips, top to bottom
b[:, 1] += 0.0026 * lip_m                                              # set back, not pouting
b[:, 0] *= 1 - 0.07 * g(dz - mouth_dz, 0.014) * g(b[:, 0], 0.040) * facing   # a slightly smaller mouth
jaw_m = g(dz - (chin_dz - 0.020), 0.030) * facing
b[:, 0] *= 1 - 0.05 * jaw_m                                            # a finer jaw and chin
dz = top - b[:, 2]
upper_peak = mouth_dz + (upper_peak - mouth_dz) * 0.70
lower_peak = mouth_dz + (lower_peak - mouth_dz) * 0.70
H_base = chin_dz
scale = (crown_z - egg_chin) / H_base
print('base landmarks (m below crown): nose %.3f mouth %.3f lips %.3f/%.3f chin %.3f | scale %.3f'
      % (nose_dz, mouth_dz, upper_peak, lower_peak, chin_dz, scale), flush=True)

# Place: crown on crown, forehead on forehead, centred.
forehead_base = float(pf[(pf[:, 0] > 0.05) & (pf[:, 0] < 0.09), 1].min())
p = np.empty_like(b)
p[:, 0] = egg_x + b[:, 0] * scale
p[:, 1] = egg_forehead + (b[:, 1] - forehead_base) * scale
p[:, 2] = crown_z - dz * scale
# The neck: everything under the jaw is drawn down so its root reaches the shoulders.
jaw_dz = chin_dz + 0.004
root_dz = dz.max()
t = np.clip((dz - jaw_dz) / (root_dz - jaw_dz), 0, 1)
z_jaw = crown_z - jaw_dz * scale
ease = t * t * (3 - 2 * t)
p[:, 2] = np.where(dz > jaw_dz, z_jaw - (z_jaw - NECK_BASE) * (0.35 * t + 0.65 * ease), p[:, 2])

me = bpy.data.meshes.new('Healer head')
me.from_pydata([tuple(v) for v in p], [], faces)
me.update()
me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
old = head.data
head.data = me
bpy.data.meshes.remove(old)
bpy.data.objects.remove(base)

# Skin weights by height: skull to the head, the drawn-down neck shared with neck and chest.
for g in list(head.vertex_groups):
    head.vertex_groups.remove(g)
nb = rig.data.bones['Neck']
n0, n1 = nb.head_local.z, nb.tail_local.z
z = p[:, 2]


def sstep(a, b_, x):
    tt = np.clip((x - a) / (b_ - a), 0, 1)
    return tt * tt * (3 - 2 * tt)


wh = sstep(n1 - 0.03, n1 + 0.04, z)
wc = 1 - sstep(n0 - 0.03, n0 + 0.03, z)
wn = np.clip(1 - wh - wc, 0, 1)
for name, w in (('Head', wh), ('Neck', wn), ('Chest', wc)):
    g = head.vertex_groups.new(name=name)
    for i in np.where(w > 0.01)[0]:
        g.add([int(i)], float(w[i]), 'REPLACE')
if not any(m.type == 'ARMATURE' for m in head.modifiers):
    am = head.modifiers.new('Healer skin', 'ARMATURE')
    am.object = rig
head.parent = rig

# Landmarks in this figure's space, for the mask and the lip colour.
lm = {'crown': crown_z, 'chin': crown_z - chin_dz * scale, 'mouth': crown_z - mouth_dz * scale,
      'nose': crown_z - nose_dz * scale, 'lip_top': crown_z - (upper_peak - 0.0046) * scale,
      'lip_bottom': crown_z - (lower_peak + 0.0052) * scale, 'centre_x': egg_x}
for kk, vv in lm.items():
    head['lm_' + kk] = float(vv)
u = (p[:, 0] - egg_x) / (0.0235 * scale)
zc = (lm['lip_top'] + lm['lip_bottom']) / 2
hh = (lm['lip_top'] - lm['lip_bottom']) / 2
# A lens: full height at the centre, closing to nothing at the corners of the mouth.
span = np.sqrt(np.clip(1 - u * u, 0, 1))
inside = 1 - np.abs(p[:, 2] - zc) / np.maximum(hh * (0.25 + 0.75 * span), 1e-6)
lip = np.clip(inside * 4.0, 0, 1) * (np.abs(u) < 1) * (p[:, 1] < egg_forehead + 0.07)
# Soften the edge of the colour so it follows the surface instead of the grid.
ev = np.empty(2 * len(me.edges), dtype=np.int64)
me.edges.foreach_get('vertices', ev)
ev = ev.reshape(-1, 2)
deg = np.bincount(ev.ravel(), minlength=len(p)).astype(float)
for _ in range(4):
    acc = np.zeros(len(p))
    np.add.at(acc, ev[:, 0], lip[ev[:, 1]])
    np.add.at(acc, ev[:, 1], lip[ev[:, 0]])
    lip = 0.5 * lip + 0.5 * acc / np.maximum(deg, 1)
lip = np.clip(lip * 1.15, 0, 1)
attr = me.attributes.new('Lip', 'FLOAT', 'POINT')
attr.data.foreach_set('value', lip.astype(np.float32))

skin = bpy.data.materials.get('Healer skin') or bpy.data.materials.new('Healer skin')
skin.use_nodes = True
nt = skin.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
at = nt.nodes.new('ShaderNodeAttribute')
at.attribute_name = 'Lip'
mix = nt.nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'
mix.inputs[6].default_value = (0.78, 0.70, 0.63, 1)          # pale, bloodless skin
mix.inputs[7].default_value = (0.045, 0.010, 0.012, 1)       # lips the colour of dried blood
nt.links.new(at.outputs['Fac'], mix.inputs[0])
nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
rough = nt.nodes.new('ShaderNodeMapRange')
rough.inputs[3].default_value = 0.50
rough.inputs[4].default_value = 0.32                          # lips a little glossier than skin
nt.links.new(at.outputs['Fac'], rough.inputs[0])
nt.links.new(rough.outputs[0], bsdf.inputs['Roughness'])
bsdf.inputs['Subsurface Weight'].default_value = 0.15
bsdf.inputs['Subsurface Radius'].default_value = (0.012, 0.006, 0.004)
nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
me.materials.append(skin)
head.hide_render = head.hide_viewport = False
head['claude_real_head'] = 1

save()
render('stage1b-head-front', 0, dist=1.7, target_z=crown_z - 0.17, lens=85, res=(800, 1000), samples=48)
render('stage1b-head-three-quarter', 35, dist=1.7, target_z=crown_z - 0.17, lens=85, res=(800, 1000), samples=48)
render('stage1b-head-side', 90, dist=1.7, target_z=crown_z - 0.17, lens=85, res=(800, 1000), samples=48)
print('stage 1b done')

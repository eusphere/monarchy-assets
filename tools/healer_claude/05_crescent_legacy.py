"""Stage 5: the crescent headpiece of concept v003, in the team accent.

One folded blade: widest over the brow with a centre crease, sweeping out,
back and down into two thin curved points. It replaces the circlet."""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

NAME = 'Crescent headpiece'
remove(NAME)
head = bpy.data.objects['Healer - pearl face']
hc = coords(head)
crown_z = hc[:, 2].max()
brow_y = hc[:, 1].min()

S = 97          # samples along the crescent
W = 9           # samples across the blade
s = np.linspace(-1, 1, S)
a = np.abs(s)
# Outer (upper) edge: apex above the crown, tips out at the sides near chin height.
ox = 0.215 * np.sign(s) * a ** 0.85
oz = crown_z + 0.040 - 0.300 * a ** 2.0
oy = brow_y + 0.012 + 0.085 * a ** 1.3
width = 0.080 * (1 - a ** 1.2) ** 0.8 + 0.0015
verts = np.zeros((S, W, 3))
for j in range(W):
    t = j / (W - 1)                       # 0 at the outer edge, 1 at the inner edge
    # The blade hangs down and slightly forward from its outer edge, like a visor.
    verts[:, j, 0] = ox * (1 - 0.10 * t * (1 - a))
    verts[:, j, 1] = oy - 0.034 * t * (1 - a ** 2) + 0.006 * np.sin(np.pi * t)
    verts[:, j, 2] = oz - width * t
# Centre crease: fold the two halves back from the middle line.
crease = np.exp(-(s / 0.06) ** 2)
verts[:, :, 1] -= 0.014 * crease[:, None]
uv = np.stack([np.repeat(s[:, None], W, 1) * 0.5 + 0.5, np.repeat(np.linspace(0, 1, W)[None, :], S, 0)], -1)
piece = new_object(NAME, verts.reshape(-1, 3), grid_faces(S, W, False), 'Jewelry', uv.reshape(-1, 2))
piece.data.materials.append(bpy.data.materials['TeamAccent'])
sol = piece.modifiers.new('Thickness', 'SOLIDIFY')
sol.thickness = 0.007
sol.offset = 0
bev = piece.modifiers.new('Edge', 'BEVEL')
bev.width = 0.0015
bev.segments = 2
bev.limit_method = 'ANGLE'
sub = piece.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 1
rig = bpy.data.objects['Healer Rig']
piece.parent = rig
vg = piece.vertex_groups.new(name='Head')
vg.add(list(range(len(piece.data.vertices))), 1.0, 'REPLACE')
arm = piece.modifiers.new('Healer skin', 'ARMATURE')
arm.object = rig
piece.modifiers.move(len(piece.modifiers) - 1, 0)

circ = bpy.data.objects.get('Healer - linked circlet and bow fasteners')
if circ:
    circ.hide_render = circ.hide_viewport = True

save()
render('stage5-headpiece-front', 0)
render('stage5-headpiece-side', 90)
render('stage5-headpiece-portrait', 20, dist=2.6, target_z=1.98, lens=85, res=(800, 1000))
print('stage 5 done')

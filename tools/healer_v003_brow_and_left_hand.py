"""Extend the joined hood crown to brow level and correct the open glove's handedness."""
import math
import bpy
import bmesh

scene = bpy.context.scene
assert not scene.get('brow_and_left_hand')
hood = bpy.data.objects['Fit04 rounded outer hood']
bm = bmesh.new()
bm.from_mesh(hood.data)
bm.verts.ensure_lookup_table()
original = list(bm.verts)
assert len(original) == 10899
previous = [original[3099], *original[10870:10899], original[3000]]
for j in range(31,49):
    left, right = original[j*100+99], original[j*100]
    row = [left]
    t = (j-30)/18
    for k in range(1,30):
        u = k/30
        arch = math.sin(math.pi*u)**.9
        co = left.co.lerp(right.co,u)
        co.z += (.02024*(1-t)+.012*t)*arch
        co.y -= (.0042+.004*t)*arch
        row.append(bm.verts.new(co))
    row.append(right)
    for k in range(30):
        face = bm.faces.new((previous[k],previous[k+1],row[k+1],row[k]))
        face.smooth = True
    previous = row
bm.normal_update()
bm.to_mesh(hood.data)
bm.free()
hood.data.update()

# The open wrist stayed centered at x=.29 before the slender fitting narrowed it.
glove = bpy.data.objects['Fit05 posed glove open']
wrist_x = .29*.955
for v in glove.data.vertices:
    v.co.x = 2*wrist_x-v.co.x
glove.data.flip_normals()
glove.data.update()
scene['brow_and_left_hand'] = True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""Draw the lined veil smooth over a featureless head, retaining its sewn edges."""
import math
import bpy

scene = bpy.context.scene
veil = bpy.data.objects['Fit04 opaque shaped face veil - no facial features']
assert scene.get('rear_drape') and len(veil.data.vertices) == 110*90
name = 'Face veil tension'
if not veil.data.shape_keys:
    veil.shape_key_add(name='Basis')
assert name not in veil.data.shape_keys.key_blocks
key = veil.shape_key_add(name=name)

def ease(x):
    x = min(1, max(0, x))
    return x*x*(3-2*x)

for row in range(110):
    t = row/109
    left = veil.data.vertices[row*90].co
    right = veil.data.vertices[row*90+89].co
    # Fit over the brow and cheeks, then turn beneath the chin toward the neck.
    depth = .029 + .016*math.exp(-((t-.36)/.28)**2) - .024*ease((t-.53)/.23)
    for col in range(90):
        u = col/89
        side = 2*u-1
        span = max(0,1-side*side)
        old = veil.data.vertices[row*90+col].co
        co = key.data[row*90+col].co
        edge = left.lerp(right,u)
        fit = ease(t/.095)*ease((1-t)/.19)
        pleat = .0016*math.sin(23*side+6*t)*ease((t-.62)/.22)*span
        co.y = old.y*(1-fit)+(edge.y-depth*span**.70+pleat)*fit
        co.x = old.x*(1-fit)+edge.x*fit
key.value = 1
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

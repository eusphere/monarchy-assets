"""Seat both glove wrists in their sleeves and fit a repeating ivory lace edging."""
import math
import bpy
import numpy as np
from mathutils import Vector, Quaternion

scene = bpy.context.scene
collection = bpy.data.collections['V003 - fitting 04 tailored']
assert not scene.get('wrist_and_lace')
for side in ('raised', 'open'):
    sleeve = collection.objects['Fit04 continuous fitted sleeve ' + side]
    cuff = collection.objects['Fit04 tailored glove cuff ' + side]
    rings = sleeve.data.vertices
    def center(vertices):
        return sum((v.co for v in vertices), Vector()) / len(vertices)
    proximal = center(cuff.data.vertices[:64])
    distal = center(cuff.data.vertices[-64:])
    axis = (distal - proximal).normalized()
    end = center(rings[-64:])
    direction = (end - center(rings[-128:-64])).normalized()
    rotation = direction.rotation_difference(axis)
    # Turn the forearm into the wrist gradually. Sleeve terminates inside the cuff.
    target = distal - axis * .010
    for j in range(80, 110):
        t = (j - 80) / 29
        w = t * t * (3 - 2 * t)
        row = rings[64*j:64*(j+1)]
        origin = center(row)
        turn = Quaternion().slerp(rotation, w)
        for v in row:
            radial = turn @ (v.co - origin)
            v.co = origin + (target-end)*w + radial*(1-.46*w)
    # Flare cuff mouth to seat the palm root with a tailored overlap.
    for j in range(20):
        row = cuff.data.vertices[j*64:(j+1)*64]
        origin = center(row)
        for v in row:
            v.co += (v.co-origin)*(.12*j/19)

# Tile a six-petal embroidered rosette over a fine diamond net.
n = 512
y, x = (np.indices((n,n))+.5)/n-.5
angle = np.arctan2(y,x)
radius = np.hypot(x,y)
def thread(distance, width):
    return np.clip(.5 + (width - np.abs(distance))*n, 0, 1)
net = thread(np.sin(4*math.pi*(x+y))/(4*math.pi), .006)
net = np.maximum(net, thread(np.sin(4*math.pi*(x-y))/(4*math.pi), .006))
petals = thread(radius-(.22+.105*np.cos(6*angle)), .021)
border = thread(radius-.40, .012)
opacity = np.maximum.reduce([net*.72, petals, border, thread(radius-.073,.023)])
pixels = np.ones((n,n,4), dtype=np.float32)
pixels[:,:,:3] = opacity[:,:,None]
tile = bpy.data.images.new('Healer embroidered rosette repeat', n, n, alpha=False)
tile.colorspace_settings.name = 'Non-Color'
tile.pixels.foreach_set(pixels.ravel())
tile.pack()
mat = bpy.data.materials['Fit04 clean warm ivory cloth'].copy()
mat.name = 'Ivory rosette lace - hanging sleeve borders'
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
texture = nodes.new('ShaderNodeTexImage')
texture.image = tile
texture.label = 'Embroidered rosette and open diamond net'
links.new(texture.outputs['Color'], bsdf.inputs['Alpha'])
bsdf.inputs['Sheen Weight'].default_value = .35
for side in ('right','left'):
    mesh = collection.objects['Fit04 retained hanging sleeve drape '+side].data
    uv = mesh.uv_layers.new(name='Sleeve lace repeat')
    mesh.uv_layers.active = uv
    uv.active_render = True
    mesh.materials.append(mat)
    for poly in mesh.polygons:
        cols = [i%50 for i in poly.vertices]
        if min(cols) >= 39 and max(cols) <= 48:
            poly.material_index = len(mesh.materials)-1
        for loop in poly.loop_indices:
            row,col = divmod(mesh.loops[loop].vertex_index,50)
            uv.data[loop].uv = (row/89*7, (col-39)/9*2)
scene['wrist_and_lace'] = True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""Unify the textile ground colors and tailor the sleeves inside the hanging lace."""
import math
import bpy
from mathutils import Vector

s = bpy.context.scene
group = bpy.data.collections['V003 - fitting 04 tailored']
assert not s.get('pearl_sleeve_fitting')
materials = {m for o in group.objects if not o.hide_render and hasattr(o.data,'materials')
             for m in o.data.materials if m}
for mat in materials:
    shader = next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    color = shader.inputs['Base Color']
    if mat.name.startswith('White ivory'):
        continue
    if color.is_linked:
        ramp = color.links[0].from_node.color_ramp
        ramp.elements[0].color = (.74,.74,.73,1)
        ramp.elements[-1].color = (.97,.965,.95,1)
    else:
        color.default_value = (.82,.815,.80,1)
    mat.diffuse_color = (.81,.81,.80,1)

for side,drape_side,sign in [('raised','right',-1),('open','left',1)]:
    sleeve = group.objects['Fit04 continuous fitted sleeve '+side]
    sheet = group.objects['Fit04 retained hanging sleeve drape '+drape_side]
    if not sleeve.data.shape_keys:
        sleeve.shape_key_add(name='Basis')
    fit = sleeve.shape_key_add(name='Tailored sleeve')
    centers = []
    for j in range(110):
        t = j/109
        row = sleeve.data.vertices[64*j:64*(j+1)]
        center = sum((v.co for v in row),Vector())/64
        # Seat the shoulder and ease into the existing glove overlap at the wrist.
        inset = .014*(1-t)**2
        scale = 1-(.24+.07*math.sin(math.pi*t))*min(1,(1-t)/.19)
        center_fit = center-Vector((sign*inset,0,0))
        for v in row:
            fit.data[v.index].co = center_fit+(v.co-center)*scale
        centers.append(center_fit)
    fit.value = 1
    if not sheet.data.shape_keys:
        sheet.shape_key_add(name='Basis')
    key = sheet.shape_key_add(name='Lace on fitted sleeve')
    for j in range(90):
        t = j/89
        sleeve_row = round(t*54)
        center = centers[sleeve_row]
        # Anchor the sheer panel to the outside of the newly fitted upper arm.
        anchor = max((fit.data[sleeve_row*64+k].co for k in range(64)),key=lambda p:sign*p.x)
        old = sheet.data.vertices[j*50].co
        offset = anchor-old
        for i in range(50):
            v = sheet.data.vertices[j*50+i]
            w = i/49
            key.data[v.index].co = v.co+offset*(1-.33*w)
    key.value = 1
s['pearl_sleeve_fitting'] = True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

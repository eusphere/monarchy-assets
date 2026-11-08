"""Fit the undergown, fitted sleeves and cuffs in pearl-white embroidered cloth."""
import bpy

scene = bpy.context.scene
collection = bpy.data.collections['V003 - fitting 04 tailored']
material = collection.objects['Fit04 softly fitted covered gown'].data.materials[0]
shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
ramp = shader.inputs['Base Color'].links[0].from_node.color_ramp
ramp.elements[0].color = (.76, .75, .72, 1)
ramp.elements[-1].color = (.96, .95, .92, 1)
material.diffuse_color = ramp.elements[0].color
material.name = 'Healer lace - pearl white foundation'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

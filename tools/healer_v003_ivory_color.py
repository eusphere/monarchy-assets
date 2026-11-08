"""First clean color study: pearl head coverings, warm outer lace and flax lining."""
import bpy

scene=bpy.context.scene
assert scene.get('right_palm_sculpt') and not scene.get('ivory_color')
# Scene-linear ground and embroidery colors. Only the BSDF color ramp changes.
palette=[
    ('Healer lace - corded ivory',(.35,.24,.15),(.80,.68,.50)),
    ('Healer lace - openwork',(.49,.385,.27),(.90,.79,.62)),
    ('Healer lace - fine sleeve',(.52,.43,.32),(.92,.83,.69)),
    ('Placed ivory lace - Fit04 retained continuous',(.54,.425,.30),(.91,.81,.64)),
    ('Placed ivory lace - Fit04 retained diagonal',(.47,.355,.245),(.88,.76,.58)),
    ('Healer lace - white lined',(.69,.67,.62),(.95,.94,.89)),
    ('Ivory hood lace',(.62,.575,.495),(.94,.89,.78)),
    ('Healer lace - lined ivory glove',(.66,.61,.53),(.91,.87,.78))]
group=bpy.data.collections['V003 - fitting 04 tailored']
materials={m for o in group.objects if not o.hide_render and hasattr(o.data,'materials') for m in o.data.materials if m}
for prefix,ground,yarn in palette:
    mat,=[m for m in materials if m.name.startswith(prefix)]
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    ramp=bsdf.inputs['Base Color'].links[0].from_node.color_ramp
    ramp.elements[0].color=(*ground,1)
    ramp.elements[-1].color=(*yarn,1)
scene['ivory_color']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

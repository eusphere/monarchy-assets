"""Carve tapered flutes into the front and back of the bowed ivory headpiece."""
import bpy
import math

piece = bpy.data.objects['Fit04 shallow bowed white headpiece']
source = piece.data
assert len(source.vertices) == 404
vertices, faces, recess = [], [], []
steps = 96
ring = 2*(steps+1)
for j in range(101):
    top, bottom, back_bottom, back_top = [v.co.copy() for v in source.vertices[j*4:j*4+4]]
    wing = abs(j-50)/50
    fade = max(0,1-wing**3)
    for rear in (False,True):
        start,end = (back_bottom,back_top) if rear else (top,bottom)
        for i in range(steps+1):
            t = i/steps
            h = 1-t if rear else t
            cut = 0
            for k,center in enumerate((.21,.39,.63,.78)):
                line = center+.035*math.sin(wing*4.6+k*.86)*math.sin(math.pi*wing)
                cut += (1 if k in (1,2) else .56)*math.exp(-((h-line)/.027)**2)
            p=start.lerp(end,t)
            p.y += (-1 if rear else 1)*.0016*fade*cut
            vertices.append(p)
            recess.append(cut*fade)
for j in range(100):
    for i in range(ring):
        a=j*ring+i
        b=j*ring+(i+1)%ring
        faces.append((a,b,b+ring,a+ring))
# Bridge the two ends in strips to keep their bevels predictable.
for j in (0,100):
    for i in range(steps):
        cap=[j*ring+i,j*ring+ring-1-i,j*ring+ring-2-i,j*ring+i+1]
        faces.append(cap if j==0 else cap[::-1])
mesh=bpy.data.meshes.new('Bowed ivory with incised longitudinal striations')
mesh.from_pydata(vertices,[],faces)
mesh.update()
piece.data=mesh
for poly in mesh.polygons[:100*ring]:
    poly.use_smooth=poly.index%ring not in (steps,ring-1)
attr=mesh.attributes.new('Incision depth','FLOAT','POINT')
attr.data.foreach_set('value',recess)
mat=source.materials[0].copy()
mat.name='White ivory - incised'
mesh.materials.append(mat)
nodes=mat.node_tree.nodes
links=mat.node_tree.links
bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
ivory=tuple(bsdf.inputs['Base Color'].default_value)
depth=nodes.new('ShaderNodeAttribute')
depth.attribute_name=attr.name
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=ivory
ramp.color_ramp.elements[1].color=tuple(.78*v for v in ivory[:3])+(1,)
links.new(depth.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],bsdf.inputs['Base Color'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

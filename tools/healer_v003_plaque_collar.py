"""Seat a linked plaque collar over the dressed figure and assign the team accent."""
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
group = bpy.data.collections['V003 - fitting 04 tailored']
assert scene.get('pearl_sleeve_fitting') and not bpy.data.materials.get('TeamAccent')
metal = bpy.data.materials.new('TeamAccent')
metal.use_nodes = True
shader = next(n for n in metal.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
metal.diffuse_color = (.47,.29,.121,1)
shader.inputs['Base Color'].default_value = metal.diffuse_color
shader.inputs['Metallic'].default_value = .79
shader.inputs['Roughness'].default_value = .37
metal['colorRole'] = 'teamAccent'
for name in ('Fit04 shallow bowed white headpiece','Fit04 tailored glove cuff raised','Fit04 tailored glove cuff open'):
    obj = group.objects[name]
    obj.data.materials[0] = metal

deps = bpy.context.evaluated_depsgraph_get()
surfaces = [o.evaluated_get(deps) for o in group.objects if o.type=='MESH' and
            not o.hide_render and any(part in o.name for part in ('hood','veil','mantle','shoulder cowl','covered gown'))]
def point(angle,depth,offset):
    direction=Vector((math.sin(angle),-math.cos(angle),0))
    front=(1+math.cos(angle))*.5
    z=1.814-.076*front**2-depth*(.042+.081*front**3)
    start=direction*.48+Vector((0,0,z))
    hits=[]
    for o in surfaces:
        inv=o.matrix_world.inverted()
        hit,p,_,_=o.ray_cast(inv@start,inv.to_3x3()@(-direction))
        if hit:
            hits.append((o.matrix_world@p).dot(direction))
    radius=max(hits,default=.094)
    return direction*(radius+offset)+Vector((0,0,z))

vertices=[]
faces=[]
def ring(coords):
    base=len(vertices)
    vertices.extend(coords)
    return list(range(base,len(vertices)))
def bridge(a,b):
    for i in range(len(a)):
        j=(i+1)%len(a)
        faces.append((a[i],a[j],b[j],b[i]))
# A narrow collar band connects the articulated plaques all around the neck.
count=32
loops=[ring([point(math.tau*i/128,t,h) for i in range(128)])
       for t,h in ((.04,.003),(.17,.003),(.17,.006),(.04,.006))]
for a,b in zip(loops,loops[1:]+loops[:1]):
    bridge(a,b)
for i in range(count):
    angle=math.tau*i/count
    half=math.pi/count*.94
    length=.80+.19*math.cos(angle*0.5)**8
    outline=[(-.62,0),(.62,0),(1,.14),(.90,.75),(.48,.93),(0,1),(-.48,.93),(-.90,.75),(-1,.14)]
    # Each rigid plaque bridges the underlying cloth folds on one plane.
    outward=Vector((math.sin(angle),-math.cos(angle),0))
    across=Vector((math.cos(angle),math.sin(angle),0))
    middle=point(angle,.45*length,0)
    top=point(angle,.08*length,0)
    bottom=point(angle,.90*length,0)
    slope=max(-1.1,min(.7,(bottom-top).dot(outward)/(bottom.z-top.z)))
    corners=[point(angle+x*half,y*length,0) for x,y in outline]
    base=max(p.dot(outward)-slope*(p.z-middle.z) for p in corners+[middle])
    def plaque(x,y,height):
        surface=point(angle+x*half,y*length,0)
        lateral=x*half*middle.dot(outward)
        return across*lateral+outward*(base+slope*(surface.z-middle.z)+height)+Vector((0,0,surface.z))
    loops=[]
    for shrink,height in ((1,.005),(1,.0085),(.87,.010),(.76,.008),(.68,.009)):
        coords=[plaque(x*shrink,.46+(y-.46)*shrink,height) for x,y in outline]
        loops.append(ring(coords))
    for a,b in zip(loops,loops[1:]):
        bridge(a,b)
    faces.append(tuple(reversed(loops[0])))
    center=ring([plaque(0,.45,.0092)])[0]
    for j,k in enumerate(loops[-1]):
        faces.append((k,loops[-1][(j+1)%len(outline)],center))
mesh=bpy.data.meshes.new('Articulated repoussé collar')
mesh.from_pydata(vertices,[],faces)
mesh.update()
import bmesh
bm=bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
collar=bpy.data.objects.new('Healer - flat linked plaque necklace',mesh)
group.objects.link(collar)
mesh.materials.append(metal)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""A fitted plaque circlet with two metal stays pinned to the bowed headpiece."""
import bpy
import math
import bmesh
from mathutils import Vector

group=bpy.data.collections['V003 - fitting 04 tailored']
name='Healer - linked circlet and bow fasteners'
assert name not in group.objects
metal=group.objects['Healer - cuff to cuff plaque chain'].data.materials[0]
deps=bpy.context.evaluated_depsgraph_get()
cloth=[o.evaluated_get(deps) for o in group.objects if not o.hide_render and
       any(k in o.name for k in ('rounded outer hood','flowing back mantle','opaque shaped face veil'))]
bow=group.objects['Fit04 shallow bowed white headpiece']
verts=[]
faces=[]
def ring(points):
    first=len(verts)
    verts.extend(points)
    return list(range(first,len(verts)))
def join(a,b):
    faces.extend((a[i],a[(i+1)%len(a)],b[(i+1)%len(b)],b[i]) for i in range(len(a)))
def frame(a):
    n=Vector((math.sin(a),-math.cos(a),0))
    t=Vector((math.cos(a),math.sin(a),0))
    z=2.05+.015*math.sin(a)**2+.004*math.cos(a)
    distances=[]
    for o in cloth:
        inv=o.matrix_world.inverted()
        for dz in (-.009,0,.009):
            start=n*.32+Vector((0,0,z+dz))
            hit,p,_,_=o.ray_cast(inv@start,inv.to_3x3()@(-n))
            if hit:
                distances.append((o.matrix_world@p).dot(n))
    return n*(max(distances,default=.09)+.004)+Vector((0,0,z)),t,n
up=Vector((0,0,1))
outline=[(-1,-.48),(-.76,-.9),(.53,-1),(1,-.28),(1,.28),(.53,1),(-.76,.9),(-1,.48)]
def plate(p,t,w,n,length,width):
    loops=[]
    for scale,h in ((1,-.002),(1,.001),(.84,.0026),(.72,.0019)):
        loops.append(ring([p+t*(x*length*.5*scale)+w*(y*width*.5*scale)+n*h for x,y in outline]))
    for a,b in zip(loops,loops[1:]):
        join(a,b)
    faces.extend((tuple(reversed(loops[0])),tuple(loops[-1])))
# Follow the outer envelope of the textile with a continuous narrow backing.
count=30
samples=[frame(math.tau*j/(count*6)) for j in range(count*6)]
loops=[ring([p+up*z+n*h for p,t,n in samples]) for z,h in
       ((-.003,-.002),(.003,-.002),(.003,.001),(-.003,.001))]
for a,b in zip(loops,loops[1:]+loops[:1]):
    join(a,b)
for j in range(count):
    a=math.tau*j/count
    p,t,n=frame(a)
    prev=samples[(6*j-3)%len(samples)][0]
    nxt=samples[(6*j+3)%len(samples)][0]
    tangent=(nxt-prev).normalized()
    plate(p+n*.002,tangent,up,tangent.cross(up).normalized(),(nxt-prev).length*.88,.018)
    q,t,n=frame(a+math.pi/count)
    oval=[]
    for k in range(16):
        b=math.tau*k/16
        radial=t*math.cos(b)+up*math.sin(b)
        center=q+n*.002+t*.0047*math.cos(b)+up*.003*math.sin(b)
        oval.append(ring([center+.0012*(radial*math.cos(v*math.tau/8)+n*math.sin(v*math.tau/8)) for v in range(8)]))
    for u,v in zip(oval,oval[1:]+oval[:1]):
        join(u,v)
for j in (32,68):
    pin=bow.matrix_world@bow.data.vertices[j*194+50].co
    a=math.atan2(pin.x,-pin.y)
    seat,_,n=frame(a)
    pin.y-=.003
    axis=(pin-seat).normalized()
    width=axis.cross(n).normalized()
    if width.length<.1:
        width=up
    plate((seat+pin)*.5,axis,width,width.cross(axis).normalized(),(pin-seat).length+.009,.013)
    # A domed rivet is visible on the front face of each engraved wing.
    rings=[]
    for r,h in ((.005,0),(.005,.0016),(.0034,.003),(.0008,.0038)):
        rings.append(ring([pin+Vector((r*math.cos(k*math.tau/16),-h,r*math.sin(k*math.tau/16))) for k in range(16)]))
    for u,v in zip(rings,rings[1:]):
        join(u,v)
    faces.append(tuple(rings[-1]))
mesh=bpy.data.meshes.new('Linked circlet with temple stays')
mesh.from_pydata(verts,[],faces)
bm=bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
obj=bpy.data.objects.new(name,mesh)
group.objects.link(obj)
mesh.materials.append(metal)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""Drape a continuous line of beveled collar plaques between the two cuffs."""
import bisect
import math
import bpy
import bmesh
from mathutils import Vector

group = bpy.data.collections['V003 - fitting 04 tailored']
name = 'Healer - cuff to cuff plaque chain'
assert name not in group.objects
metal = group.objects['Healer - flat linked plaque necklace'].data.materials[0]

def mount(side, sign):
    cuff = group.objects['Fit04 tailored glove cuff '+side]
    verts = cuff.data.vertices[8*64:9*64]
    return max((cuff.matrix_world@v.co for v in verts), key=lambda p: sign*p.x)

right, left = mount('raised',-1), mount('open',1)
path = [right, right+Vector((-.020,-.002,-.048)), Vector((-.264,-.222,1.30)),
        Vector((-.302,-.135,1.16)), Vector((-.307,.015,1.03)),
        Vector((-.259,.149,.921)), Vector((-.151,.220,.835)),
        Vector((0,.244,.805)), Vector((.16,.219,.830)),
        Vector((.261,.153,.891)), Vector((.307,.045,.978)),
        Vector((.316,-.088,1.10)),left+Vector((.012,.022,-.062)),left]
# Sample equal arc lengths so plaque spacing holds around the curved sides.
curve=[]
for i in range(len(path)-1):
    a,b,c,d = [path[max(0,min(len(path)-1,i+k))] for k in (-1,0,1,2)]
    for j in range(48):
        t=j/48
        curve.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3))
curve.append(left)
dist=[0.]
for a,b in zip(curve,curve[1:]):
    dist.append(dist[-1]+(a-b).length)
def at(s):
    i=max(1,min(len(dist)-1,bisect.bisect_left(dist,s)))
    return curve[i-1].lerp(curve[i],(s-dist[i-1])/(dist[i]-dist[i-1]))
vs=[]
fs=[]
def ring(coords):
    ids=list(range(len(vs),len(vs)+len(coords)))
    vs.extend(coords)
    return ids
def bridge(a,b):
    fs.extend((a[i],a[(i+1)%len(a)],b[(i+1)%len(a)],b[i]) for i in range(len(a)))
def frame(s):
    p=at(s)
    tangent=(at(min(dist[-1],s+.002))-at(max(0,s-.002))).normalized()
    normal=Vector((p.x,p.y,0)).normalized()
    across=tangent.cross(normal).normalized()
    return p,tangent,across,across.cross(tangent).normalized()
count=round(dist[-1]/.047)
pitch=dist[-1]/count
outline=[(-.62,-1),(.62,-1),(1,-.72),(.90,.50),(.48,.86),(0,1),(-.48,.86),(-.90,.50),(-1,-.72)]
for j in range(count):
    p,t,w,n=frame((j+.5)*pitch)
    loops=[]
    for scale,height in ((1,-.0017),(1,.001),(.84,.0028),(.72,.0017)):
        loops.append(ring([p+scale*(x*.0095*w+y*pitch*.45*t)+height*n for x,y in outline]))
    for a,b in zip(loops,loops[1:]):
        bridge(a,b)
    fs+=[tuple(reversed(loops[0])),tuple(loops[-1])]
# Oval connecting links meet the plaques at both ends, including the cuff mounts.
for j in range(count+1):
    p,t,w,n=frame(j*pitch)
    loops=[]
    for i in range(20):
        a=math.tau*i/20
        radial=math.cos(a)*t+math.sin(a)*w
        center=p+.0075*math.cos(a)*t+.0044*math.sin(a)*w
        loops.append(ring([center+.0015*(math.cos(math.tau*k/8)*radial+math.sin(math.tau*k/8)*n) for k in range(8)]))
    for a,b in zip(loops,loops[1:]+loops[:1]):
        bridge(a,b)
mesh=bpy.data.meshes.new('Beveled cuff plaques with oval joining links')
mesh.from_pydata(vs,[],fs)
bm=bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
obj=bpy.data.objects.new(name,mesh)
group.objects.link(obj)
mesh.materials.append(metal)
print(count,'plaques', tuple(right), tuple(left))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

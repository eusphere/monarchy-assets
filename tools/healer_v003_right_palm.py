"""Sculpt the raised glove as a continuous field, including thumb pad and finger webs."""
import bpy
import bmesh
import math
import numpy as np
from mathutils import Matrix, Vector

scene=bpy.context.scene
assert not scene.get('right_palm_sculpt')
obj=bpy.data.objects['Fit05 posed glove raised']
step=1.05
origin=np.array([-54.,-57.,-71.])
axes=[np.arange(low,high,step,dtype=np.float32) for low,high in zip(origin,(49,25,103))]
x,y,z=np.ix_(*axes)
field=np.full(tuple(map(len,axes)),1000.,dtype=np.float32)
def join(distance,blend):
    global field
    h=np.maximum(blend-np.abs(field-distance),0)/blend
    field=np.minimum(field,distance)-h*h*blend*.25

def ellipsoid(center,radii,blend):
    a,b,c=[(q-m)/r for q,m,r in zip((x,y,z),center,radii)]
    norm=np.sqrt(a*a+b*b+c*c)
    grad=np.sqrt((a/radii[0])**2+(b/radii[1])**2+(c/radii[2])**2)
    join(norm*(norm-1)/np.maximum(grad,.001),blend)

def segment(start,end,r1,r2,blend):
    axis=np.array(end)-start
    delta=[q-m for q,m in zip((x,y,z),start)]
    t=np.clip(sum(d*v for d,v in zip(delta,axis))/np.dot(axis,axis),0,1)
    dist=np.sqrt(sum((d-v*t)**2 for d,v in zip(delta,axis)))
    join(dist-(r1+(r2-r1)*t),blend)

ellipsoid((0,0,-45),(14,8.6,22),5)
ellipsoid((0,1,-14),(22,10,33),6)
ellipsoid((-.5,1,5),(24,10,21),5)
ellipsoid((-11,-5,-12),(12,8.5,22),5)
ellipsoid((13,-2,-13),(9,8,22),5)
# Finger centre lines run from inside each metacarpal to the tip. The index
# leads, then the middle finger, with a progressively deeper PIP and DIP curl.
digits=[
 ([(-16,0,6),(-18,-1,22),(-21,-4,45),(-22,-10,62),(-20,-17,72)],[8,7.4,6.4,5.3,4.1]),
 ([(-5,2,8),(-5,2,26),(-7,-3,51),(-7,-14,68),(-5,-23,74)],[8,7.6,6.7,5.5,4.3]),
 ([(6,2,7),(8,2,22),(10,-6,43),(10,-22,55),(8,-32,56)],[7.7,7.0,6.1,5.1,4.0]),
 ([(16,0,1),(18,0,13),(21,-7,30),(21,-20,39),(19,-29,38)],[7,6.0,5.4,4.5,3.6]),
 ([(-9,-3,-26),(-19,-7,-11),(-27,-10,2),(-32,-17,14),(-30,-25,24)],[10,9.2,7.1,6.1,4.6])]
for path,radii in digits:
    for i,(a,b) in enumerate(zip(path,path[1:])):
        segment(a,b,radii[i],radii[i+1],4.2 if i==0 else 2.2)

# Surface nets: one vertex at the mean edge crossing in each occupied cell.
corners=np.array([(i,j,k) for i in (0,1) for j in (0,1) for k in (0,1)])
shape=np.array(field.shape)-1
samples=[field[tuple(slice(a,a+n) for a,n in zip(c,shape))] for c in corners]
active=(np.minimum.reduce(samples)<0)&(np.maximum.reduce(samples)>=0)
idx=np.where(active)
coords=np.array(idx).T
total=np.zeros_like(coords,dtype=float)
count=np.zeros(len(coords))
for i,c in enumerate(corners):
    for j,d in enumerate(corners[i+1:],i+1):
        if np.sum(np.abs(d-c))!=1:
            continue
        a,b=samples[i][idx],samples[j][idx]
        mask=(a<0)!=(b<0)
        t=a[mask]/(a[mask]-b[mask])
        total[mask]+=c+t[:,None]*(d-c)
        count[mask]+=1
vertices=origin+step*(coords+total/count[:,None])
ids=np.full(shape,-1)
ids[idx]=np.arange(len(coords))
faces=[]
for axis in range(3):
    a,b=(axis+1)%3,(axis+2)%3
    edges=np.array(np.where(np.diff(field<0,axis=axis))).T
    offsets=np.zeros((4,3),dtype=int)
    offsets[1,a]=-1
    offsets[2,[a,b]]=-1
    offsets[3,b]=-1
    quads=np.stack([ids[tuple((edges+offset).T)] for offset in offsets],axis=1)
    faces.extend(quads.tolist())

rot=Matrix.Rotation(math.radians(-8),3,'X')
mirror=Matrix.Diagonal(Vector((-1,1,1)))
posed=[]
for q in vertices*.001:
    t=max(0,min(1,(q[2]+.050)/.075))
    twist=Matrix.Rotation(math.radians(16)*t,3,'Z')
    p=Vector((-.175,-.265,1.44))+rot@mirror@twist@Vector(q)
    posed.append((p.x*.955,p.y,p.z+.148))
mesh=bpy.data.meshes.new('Raised right glove with opposed thumb and cupped palm')
mesh.from_pydata(posed,[],faces)
bm=bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.materials.append(obj.data.materials[0])
obj.data=mesh
for poly in mesh.polygons:
    poly.use_smooth=True
scene['right_palm_sculpt']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

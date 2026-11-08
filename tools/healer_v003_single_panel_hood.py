"""Lay a single continuous panel over the crown, turning its front hem around the face."""
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
assert scene.get('brow_and_left_hand') and not scene.get('single_panel_hood')
hood = bpy.data.objects['Fit04 rounded outer hood']
old = hood.data
# Cross-sections run from the centre of the brow, around a temple and down
# onto the shoulder. Each landmark connects the face opening to the back drape.
front = [(0,-.159,2.020),(.032,-.157,2.013),(.055,-.154,1.990),
         (.067,-.153,1.951),(.071,-.150,1.894),(.069,-.143,1.836),
         (.085,-.133,1.779),(.120,-.110,1.721),(.146,-.080,1.678)]
crown = [(0,-.025,2.124),(.047,-.025,2.114),(.084,-.021,2.090),
         (.111,-.015,2.043),(.121,-.008,1.966),(.119,-.003,1.88),
         (.126,.004,1.808),(.166,.009,1.75),(.183,.012,1.703)]
back = [(0,.112,2.077),(.032,.115,2.072),(.061,.115,2.051),
        (.082,.114,2.015),(.091,.112,1.950),(.093,.106,1.870),
        (.094,.099,1.793),(.115,.110,1.727),(.140,.112,1.673)]

def sample(path,u):
    pos=min(8,abs(u)*8)
    k=min(7,int(pos))
    t=pos-k
    p0,p1,p2,p3=[Vector(path[max(0,min(8,k+i))]) for i in (-1,0,1,2)]
    if k==0:
        p0=Vector((-p2.x,p2.y,p2.z))
    p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
    if u<0:
        p.x=-p.x
    return p

rows,cols=145,73
verts=[]
faces=[]
for i in range(rows):
    u=2*i/(rows-1)-1
    a,b,c=[sample(path,u) for path in (front,crown,back)]
    for j in range(cols):
        t=j/(cols-1)
        # An interpolating quadratic keeps the grain and the surface tangent
        # continuous from the front fold across the crown to the rear edge.
        p=(1-t)*(1-2*t)*a+4*t*(1-t)*b+t*(2*t-1)*c
        slack=abs(u)**1.45
        fold=.007*slack*math.sin(12*t+1.7*u)*math.sin(math.pi*t)
        p.x+=math.copysign(1,u)*fold
        p.z+=.003*math.cos(9*t+2*u)*slack
        p.y-=.0018*math.exp(-((t-.018)/.019)**2)
        verts.append(p)
        if i and j:
            n=i*cols+j
            faces.append((n-cols-1,n-1,n,n-cols))
mesh=bpy.data.meshes.new('Crown-to-shoulder hood cloth')
mesh.from_pydata(verts,[],faces)
mesh.update()
mat=old.materials[0].copy()
mat.name='Ivory hood lace on continuous grain'
mesh.materials.append(mat)
uv=mesh.uv_layers.new(name='Hood cloth grain')
for poly in mesh.polygons:
    poly.use_smooth=True
    for k in poly.loop_indices:
        i,j=divmod(mesh.loops[k].vertex_index,cols)
        uv.data[k].uv=(i/(rows-1)*12,j/(cols-1)*4.3)
tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
for link in list(tex.inputs['Vector'].links):
    mat.node_tree.links.remove(link)
tex.projection='FLAT'
hood.data=mesh
for obj in bpy.data.collections['V003 - fitting 04 tailored'].objects:
    if 'continuous ivory hood hem' in obj.name:
        obj.hide_render=True
        obj.hide_set(True)
scene['single_panel_hood']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""Build an exploratory silhouette lineup in the open, empty healer.blend scene."""
import bpy, math
from mathutils import Vector
if bpy.context.scene.objects:
    raise RuntimeError('Requires an empty scene; will not replace existing work')

def material(name, color, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.75; p.inputs['Metallic'].default_value=metallic
    return m
ivory=material('Old ivory cloth',(.64,.57,.41)); gold=material('Tarnished ceremonial gold',(.31,.19,.065),.55)
red=material('Dried wine lining',(.15,.025,.035)); dark=material('Opaque face veil',(.025,.023,.029))

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    ob=bpy.data.objects.new(name,data); coll.objects.link(ob); ob.location.x=offset; ob.data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    return ob

def cloth(name,rings,mat,pleats=12,amp=.04):
    vs=[]; fs=[]; count=96
    for z,rx,ry,cy in rings:
        for i in range(count):
            t=2*math.pi*i/count; f=amp*math.cos(pleats*t)
            vs.append(((rx+f)*math.cos(t),cy+(ry+f*.65)*math.sin(t),z))
    for j in range(len(rings)-1):
        for i in range(count):
            a=j*count+i;b=j*count+(i+1)%count;fs.append((a,b,b+count,a+count))
    return mesh(name,vs,fs,mat)

def ellipsoid(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(offset+loc[0],loc[1],loc[2]))
    ob=bpy.context.object; ob.name=name; ob.scale=scale
    for c in list(ob.users_collection):c.objects.unlink(ob)
    coll.objects.link(ob); ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def ribbon(name,points,widths,mat):
    vs=[]
    for (x,y,z),w in zip(points,widths):vs.extend([(x-w,y,z),(x+w,y,z)])
    ob=mesh(name,vs,[(i,i+1,i+3,i+2) for i in range(0,len(vs)-2,2)],mat)
    sol=ob.modifiers.new('Cloth thickness','SOLIDIFY');sol.thickness=.012
    sub=ob.modifiers.new('Soft drape','SUBSURF');sub.levels=2
    return ob

def crown(name,outline,mat,y=.01):
    n=len(outline);vs=[(x,y-.045,z) for x,z in outline]+[(x,y+.045,z) for x,z in outline]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh(name,vs,fs,mat);be=ob.modifiers.new('Soft edges','BEVEL');be.width=.018;be.segments=3
    return ob

for index,(name,offset) in enumerate([('A - Processional',-2.4),('B - Reliquary',0),('C - Vesper',2.4)]):
    coll=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(coll)
    cloth('Pleated underrobe',[(.06,.47,.32,0),(.18,.46,.31,0),(.65,.34,.25,0),(1.08,.22,.18,0),(1.45,.3,.19,0),(1.62,.28,.18,0)],ivory,16,.035)
    cloth('Wine mantle',[(.10,.54,.34,.11),(.4,.5,.32,.11),(1,.37,.26,.10),(1.5,.47,.25,.08),(1.69,.31,.20,.05)],red,10,.035)
    # opaque veil surrounds an absent face: concealed from all angles
    cloth('Face shroud',[(1.48,.21,.17,-.025),(1.65,.19,.18,-.02),(1.9,.17,.16,0),(2.01,.06,.08,0),(2.025,.001,.001,0)],dark,8,.009)
    for s in [-1,1]:
        ribbon('Ivory shoulder fall',[(s*.12,-.17,1.83),(s*.34,-.20,1.65),(s*.41,-.23,1.25),(s*.43,-.25,.7),(s*.50,-.24,.16)],[.11,.18,.16,.15,.19],ivory)
        # broad bell sleeves suspended from shoulders, hands offered forward
        ribbon('Hanging bell sleeve',[(s*.30,0,1.60),(s*.48,-.07,1.48),(s*.65,-.16,1.30),(s*.62,-.12,.94),(s*.46,-.04,.66)],[.12,.15,.20,.22,.06],ivory)
        hand=ellipsoid('Unarmed offered hand',(s*.65,-.24,1.32),(.09,.15,.045),red);hand.rotation_euler.y=s*.25
    ribbon('Central ceremonial stole',[(0,-.21,1.61),(0,-.24,1.3),(.03,-.29,.85),(0,-.37,.1)],[.12,.13,.13,.18],ivory)
    if index==0:
        for s in [-1,1]:
            crown('Ascending split mitre',[(s*.04,1.9),(s*.07,2.39),(s*.30,2.18),(s*.29,1.91)],ivory)
            ribbon('Gold stole edge',[(s*.12,-.23,1.61),(s*.13,-.26,1.3),(s*.16,-.32,.85),(s*.18,-.39,.1)],[.012]*4,gold)
    elif index==1:
        # a broken, architectural fan behind the head, without literal wings
        for k in range(7):
            t=(k-3)*.27; x=math.sin(t); z=math.cos(t)
            crown('Radial ceremonial crest',[(x*.28-.045,1.80+z*.22),(x*.60-.055,1.80+z*.62),(x*.60+.055,1.80+z*.62),(x*.28+.045,1.80+z*.22)],gold,y=.16)
        ribbon('Outer veil',[(0,.12,2.02),(0,.23,1.8),(0,.30,1.25),(0,.40,.28)],[.16,.30,.41,.60],ivory)
    else:
        crown('Crescent ceremonial headdress',[(-.57,2.26),(-.39,1.95),(-.18,1.87),(.18,1.87),(.39,1.95),(.57,2.26),(.38,2.14),(.15,2.04),(-.15,2.04),(-.38,2.14)],ivory,y=.10)
        for s in [-1,1]:
            ribbon('Long head veil',[(s*.36,.1,2.14),(s*.40,.18,1.76),(s*.55,.23,1.14),(s*.67,.28,.18)],[.08,.12,.18,.22],ivory)
    # Label kept separate from character geometry
    data=bpy.data.curves.new(name,'FONT');data.body=name;data.align_x='CENTER';data.size=.16
    ob=bpy.data.objects.new(name,data);coll.objects.link(ob);ob.location=(offset,-.1,-.19);ob.rotation_euler=(math.pi/2,0,0);data.materials.append(gold)

scene=bpy.context.scene
if scene.world is None: scene.world=bpy.data.worlds.new('Studio world')
scene.world.color=(.13,.13,.13)
# Studio camera and soft lights are presentation-only.
def aim(ob,point):ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-11,5));cam=bpy.context.object;cam.name='Lineup camera';aim(cam,(0,0,1.1));cam.data.type='ORTHO';cam.data.ortho_scale=8.5;scene.camera=cam
for loc,power,size in [((0,-5,7),1800,7),((-5,-1,3),900,5),((3,3,6),2200,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;aim(ob,(0,0,1))
scene.render.resolution_x=1600;scene.render.resolution_y=850;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Saved three exploratory silhouette blockouts:',bpy.data.filepath)

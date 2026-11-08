"""Fit posed gloves, a gathered veil and a shoulder wrap to the approved gesture."""
import bpy
import math
from mathutils import Vector, Matrix

scene = bpy.context.scene
assert not scene.get('gesture_fitting')
group = bpy.data.collections['V003 - fitting 04 tailored']
material = bpy.data.materials['Fit04 clean fitted ivory gloves - no blood']
# Loft overlapping anatomical volumes in millimetres, then fuse at glove scale.
def loft(sections):
    offset = len(points)
    count = 24
    for j, (x,y,z,width,depth) in enumerate(sections):
        prev = Vector(sections[max(0,j-1)][:3])
        nxt = Vector(sections[min(len(sections)-1,j+1)][:3])
        axis = (nxt-prev).normalized()
        across = Vector((1,0,0))
        across = (across-axis*across.dot(axis)).normalized()
        normal = axis.cross(across)
        for i in range(count):
            a = math.tau*i/count
            p = Vector((x,y,z)) + across*(width*math.cos(a)) + normal*(depth*math.sin(a))
            points.append(p*.001)
    faces.append(tuple(offset+i for i in reversed(range(count))))
    for j in range(len(sections)-1):
        for i in range(count):
            k = offset+j*count+i
            h = offset+j*count+(i+1)%count
            faces.append((k,h,h+count,k+count))
    faces.append(tuple(range(len(points)-count,len(points))))

for raised in (True,False):
    side = 'raised' if raised else 'open'
    points, faces = [], []
    loft([(0,0,-65,13,8),(0,0,-48,15,9),(.5,1,-31,19,10),(1,2,-12,24,11),
          (0,2,4,25,10),(-1,1,14,23,8),(-2,0,22,18,6),(-3,0,26,9,3)])
    # Thumb pad rises out of the wrist and turns across the fingers in opposition.
    loft([(-4,0,-39,7,6),(-11,-2,-24,11,10),(-18,-4,-11,11,10),
          (-25,-7,0,8,8),(-31,-11,9,6.5,6.5),
          (-32 if raised else -39,-18,17,5.8,5.7),
          (-26 if raised else -43,-23,24,4.4,4.4),
          (-24 if raised else -44,-24,25,1.6,2)])
    for i,(x,z,length,rad) in enumerate([(-18,20,58,7),(-5.5,24,64,7.2),(7,20,59,6.6),(18,12,48,5.9)]):
        bend = ([17,30,47,56] if raised else [20,29,38,45])[i]
        spread = (i-1.4)*(3.6 if raised else 4.6)
        root_y = abs(i-1.4)*-2
        parts = []
        for t, width, thick in [(-.30,1.15,1.15),(0,1.03,1.04),(.17,.90,.93),(.42,.89,.90),
                                (.51,.95,.94),(.62,.80,.83),(.76,.77,.78),(.84,.78,.78),(.95,.65,.67),(1,.22,.28)]:
            f=max(t,0)
            parts.append((x+spread*f,root_y-bend*f**1.7,
                          z+length*t-bend*.57*f**2,rad*width,rad*thick))
        loft(parts)
    mesh = bpy.data.meshes.new('Posed glove '+side)
    mesh.from_pydata(points,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('Fit05 posed glove '+side,mesh)
    group.objects.link(obj)
    mesh.materials.append(material)
    bpy.context.view_layer.objects.active=obj
    remesh=obj.modifiers.new('Fuse finger webs','REMESH')
    remesh.mode='VOXEL'
    remesh.voxel_size=.00095
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=obj.modifiers.new('Soften glove transitions','SMOOTH')
    smooth.factor=.9
    smooth.iterations=14
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    rotation=Matrix.Rotation(math.radians(-8 if raised else 112),3,'X')
    mirror=Matrix.Diagonal(Vector((-1,1,1) if raised else (1,-1,1)))
    origin=Vector((-.175,-.265,1.44) if raised else (.29,-.245,1.17))
    for vert in obj.data.vertices:
        t=max(0,min(1,(vert.co.z+.052)/.064))
        twist=Matrix.Rotation(math.radians(36 if raised else -20)*t,3,'Z')
        vert.co=origin+rotation@mirror@twist@vert.co
    obj.data.flip_normals()  # Both hand placements reflect the local construction.
    for poly in obj.data.polygons:
        poly.use_smooth=True
    old=group.objects['Fit04 clean tailored glove '+side]
    old.hide_render=True
    old.hide_set(True)

veil=group.objects['Fit04 opaque shaped face veil - no facial features']
for j in range(110):
    t=j/109
    for i in range(90):
        u=i/89*2-1
        v=veil.data.vertices[j*90+i]
        phase=u*(14+6*t)+1.9*t*t+.55*math.sin(3*u+t)
        v.co.y-=(.003+.004*t)*math.cos(phase)*(1-u*u)*math.sin(math.pi*t)**.6
        v.co.x+=.008*t*t*(1-u*u)

# Carry the low side of the cowl down into a gathered fall at the hip.
wrap=group.objects['Fit04 retained continuous diagonal shoulder cowl']
for j in range(65):
    t=j/64
    for i in range(180):
        a=math.tau*i/180
        v=wrap.data.vertices[j*180+i]
        d=math.atan2(math.sin(a+1.04),math.cos(a+1.04))
        fall=math.exp(-.5*(d/.43)**2)
        drop=.37*t**2.4*fall
        v.co.z-=drop
        v.co.y-=.028*fall*t+.012*math.sin(21*d+2*t)*t*t*fall
        v.co.x+=.025*fall*t*t
scene['gesture_fitting']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

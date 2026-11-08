"""Pool the layered skirts at the floor and lift one edge of the bias drape."""
import bpy
import math
from mathutils import Vector

scene = bpy.context.scene
assert not scene.get('floor_drape')
group = bpy.data.collections['V003 - fitting 04 tailored']
for name in ('Fit04 softly fitted covered gown','Fit04 open-front flowing back mantle'):
    mantle = 'mantle' in name
    for vertex in group.objects[name].data.vertices:
        x,y,z = vertex.co
        a = math.atan2(y-.025 if mantle else y,x*.77)
        fall = max(0,1-z/1.14)
        floor = max(0,1-z/.31)**2.6
        phase = 13*a + 3*z + .9*math.sin(3*a-1.7*z)
        flutes = (.029*math.cos(phase)+.009*math.cos(2*phase+.6))*fall**1.2
        fan = floor*(.10+.045*math.sin(5*a+.3)+.05*max(0,math.sin(a)))
        vertex.co.x += (flutes+fan)*math.cos(a)
        vertex.co.y += (.8*flutes+fan)*math.sin(a)
        if mantle:
            vertex.co.z -= .052*floor
        vertex.co.z += .009*floor*(1+math.cos(phase))
panel = group.objects['Fit04 retained diagonal waist and skirt drape']
for j in range(150):
    t=j/149
    for i in range(90):
        u=i/89
        v=panel.data.vertices[j*90+i]
        a=math.atan2(v.co.y+.025,v.co.x*.75)
        # Sweep a free edge upward from a pooled corner to reveal the underskirt.
        h=.016+.44*u**1.6+.025*math.sin(3*math.pi*u)*u
        bottom=panel.data.vertices[149*90+i].co.z
        v.co.z+=(h-bottom)*t**1.65
        phase=math.tau*(4.7*u+.26*t+.17*math.sin(4*u-3*t))
        ripple=(.017*math.cos(phase)+.006*math.cos(2*phase))*(.12+.88*t)
        fan=.13*t**4*(1-u)**2
        v.co.x+=(fan+ripple)*math.cos(a)
        v.co.y+=(fan+ripple+.025*t)*math.sin(a)
# A side key makes overlapping surfaces legible in the review lighting.
key=scene.objects['Area']
key.location=(-3,-4,4.3)
key.rotation_euler=(Vector((0,0,1.0))-key.location).to_track_quat('-Z','Y').to_euler()
key.data.size=2.8
key.data.energy=820
key.data.color=(1,.92,.83)
fill=scene.objects['Area.001']
fill.location=(3,-2,2.8)
fill.rotation_euler=(Vector((0,0,1.0))-fill.location).to_track_quat('-Z','Y').to_euler()
fill.data.energy=190
scene['floor_drape']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

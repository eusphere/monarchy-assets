"""Fit a crown-hung back mantle and lengthen the Healer below the waist."""
import math
import bpy
from mathutils import Matrix, Vector

scene = bpy.context.scene
assert scene.get('placed_lace') and not scene.get('rear_drape')
pieces = bpy.data.collections['V003 - fitting 04 tailored']
mantle = pieces.objects['Fit04 open-front flowing back mantle']
# These are section measurements in the original fitting coordinates. The upper
# edge sits inside the hood, and the panels broaden over the shoulder blades.
sections = [
    # height, half-width, rear reach, front opening angle
    (.12,.33,.26,.90),(.38,.281,.215,.99),(.71,.238,.178,1.03),
    (1.04,.189,.146,1.05),(1.19,.171,.125,1.12),(1.37,.187,.142,1.16),
    (1.52,.218,.150,1.24),(1.58,.198,.143,1.26),(1.69,.129,.136,1.31),
    (1.77,.143,.149,1.37),(1.87,.142,.158,1.42),(1.96,.116,.139,1.48),
    (2.016,.043,.065,1.54)]
def section(z):
    for low,high in zip(sections,sections[1:]):
        if z<=high[0]:
            t=max(0,(z-low[0])/(high[0]-low[0]))
            return [a+(b-a)*t for a,b in zip(low[1:],high[1:])]
    return sections[-1][1:]

for j in range(180):
    t=j/179
    for i in range(120):
        u=i/119
        # The bias-cut free edge exposes the undergown in two uneven cascades.
        hem=.26+.27*math.sin(math.pi*u)**2+.12*math.sin(math.tau*u+.45)
        hem+=.39*(abs(2*u-1)**4)
        z=2.016+(hem-2.016)*t
        width,depth,opening=section(z)
        a=-math.pi/2+opening+(math.tau-2*opening)*u
        phase=math.tau*(8*u+.25*math.sin(math.tau*u)+.30*t*math.sin(math.pi*u)+.20*t*t)
        fold=(.014+.010*t)*min(1,.12+5*t)
        ridge=fold*(math.cos(phase)+.26*math.cos(2*phase+.48))
        x=(width+ridge)*math.cos(a)
        y=.017+(depth+ridge)*math.sin(a)
        mantle.data.vertices[j*120+i].co=(x,y,z)

# Change shared proportions continuously so cuffs, embroidery, and garment edges
# still coincide. The upper body rides above a longer floor-to-waist interval.
def smoothstep(value):
    t=max(0,min(1,value))
    return t*t*(3-2*t)
def fit(p):
    x,y,z=p
    head=smoothstep((z-1.57)/.23)
    return Vector((x*.955*(1-.12*head),y*(1-.13*head),
                   z+.148*smoothstep(z/1.22)-.12*max(0,z-1.61)))
for obj in pieces.objects:
    if obj.hide_render:
        continue
    world=obj.matrix_world.copy()
    inverse=world.inverted()
    if obj.type=='MESH':
        for v in obj.data.vertices:
            v.co=inverse@fit(world@v.co)
        obj.data.update()
    elif obj.type=='CURVE':
        for spline in obj.data.splines:
            for point in spline.points:
                p=inverse@fit(world@point.co.xyz)
                point.co=(*p,point.co.w)
scene.camera.location=(1.15,-8,2.5)
scene.camera.rotation_euler=(Vector((0,0,1.10))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=2.53
scene['rear_drape']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

"""Ease the layered cloth into the nape, shoulder shelves and upper back."""
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
assert not scene.get('back_contour')
pieces = bpy.data.collections['V003 - fitting 04 tailored']
def smooth(x):
    x = max(0,min(1,x))
    return x*x*(3-2*x)
def bell(value,center,width):
    return math.exp(-((value-center)/width)**2)
def fit(co):
    x,y,z = co
    rear = smooth((y+.074)/.13)
    neck = bell(z,1.833,.085)
    # Take in the sides below the occiput and allow the cloth to widen again
    # over the shoulder caps. The anterior face opening sits outside this field.
    x *= 1-.33*neck*rear
    y -= .047*neck*rear
    blade = bell(abs(x),.085,.043)*bell(z,1.644,.104)
    spine = bell(x,0,.047)*bell(z,1.636,.145)
    y -= rear*(.023*bell(z,1.59,.18)+.014*spine-.013*blade)
    # Lower the cloth just medial to each acromion to define its shoulder slope.
    z -= .019*rear*bell(abs(x),.116,.054)*bell(z,1.744,.081)
    return Vector((x,y,z))
for obj in pieces.objects:
    if obj.hide_render or not any(k in obj.name for k in (
        'rounded outer hood','flowing back mantle','covered gown','continuous diagonal shoulder cowl',
        'flat linked plaque necklace')):
        continue
    if obj.type=='MESH':
        for vertex in obj.data.vertices:
            vertex.co = fit(vertex.co)
        obj.data.update()
    elif obj.type=='CURVE':
        for spline in obj.data.splines:
            for point in spline.points:
                point.co=(*fit(point.co.xyz),point.co.w)
scene['back_contour']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

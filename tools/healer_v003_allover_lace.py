"""Dress the active Healer fitting in lined and unlined botanical lace."""
import math
from pathlib import Path
import bpy
import numpy as np

scene = bpy.context.scene
assert not scene.get('botanical_lace')
collection = bpy.data.collections['V003 - fitting 04 tailored']

# A seamless tile of branching vines, veined leaves and small bell flowers.
n = 768
y, x = (np.indices((n, n)) + .5) / n
def cord(distance, width):
    return np.clip((width - abs(distance))*n + .5, 0, 1)
def wrapped(value):
    return (value + .5) % 1 - .5

vine = np.zeros_like(x)
for shift in (0, .5):
    h = (y + shift) % 1
    stem = .25 + shift + .078*np.sin(math.tau*h)
    vine = np.maximum(vine, cord(wrapped(x-stem), .010))
    for index in range(4):
        base = (index+.25)/4
        sign = (-1)**index
        dx = wrapped(x-(.25+shift+.078*math.sin(math.tau*base)))
        dy = wrapped(h-base)
        # Elliptical leaves angle away from the stem. Cordonnet outlines enclose
        # diagonal bars with open spaces between the stitches.
        along = dx*sign*.79 + dy*.613
        across = -dx*sign*.613 + dy*.79
        radius = .040*np.sin(math.pi*np.clip(along/.19,0,1))**.82
        inside = (along>0) & (along<.19)
        outline = cord(abs(across)-radius,.0065)*inside
        spine = cord(across,.004)*inside
        bars = cord(wrapped((along-abs(across)*.72)/.024)*.024,.004)*(abs(across)<radius)
        vine = np.maximum.reduce([vine,outline,spine,bars])
    dx = wrapped(x-(.25+shift+.22))
    dy = wrapped(h-.51)
    angle = np.arctan2(dy,dx)
    r = np.hypot(dx,dy)
    petals = cord(r-(.045+.021*np.cos(5*angle)),.008)
    vine = np.maximum.reduce([vine,petals,cord(r-.013,.006)])
net = np.maximum(cord(wrapped(8*(x+y))/8,.0035),cord(wrapped(8*(x-y))/8,.0035))
height = np.maximum(vine,net*.42)
tile = bpy.data.images.new('Healer - leaf sprig and flower lace',n,n,alpha=False)
tile.colorspace_settings.name='Non-Color'
pixels=np.ones((n,n,4), dtype=np.float32)
pixels[:,:,:3]=height[:,:,None]
tile.pixels.foreach_set(pixels.ravel())
tile.pack()

def fabric(name, lining, contrast, box_scale=None):
    m=bpy.data.materials.new('Healer lace - '+name)
    m.use_nodes=True
    nodes=m.node_tree.nodes
    links=m.node_tree.links
    p=next(node for node in nodes if node.type=='BSDF_PRINCIPLED')
    tex=nodes.new('ShaderNodeTexImage')
    tex.image=tile
    if box_scale:
        coords=nodes.new('ShaderNodeTexCoord')
        scale=nodes.new('ShaderNodeVectorMath')
        scale.operation='SCALE'
        scale.inputs['Scale'].default_value=box_scale
        links.new(coords.outputs['Object'],scale.inputs[0])
        links.new(scale.outputs[0],tex.inputs['Vector'])
        tex.projection='BOX'
        tex.projection_blend=.18
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(contrast,contrast*.94,contrast*.85,1)
    ramp.color_ramp.elements[1].color=(.93,.89,.80,1)
    links.new(tex.outputs['Color'],ramp.inputs[0])
    links.new(ramp.outputs[0],p.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.22
    bump.inputs['Distance'].default_value=.00045
    links.new(tex.outputs['Color'],bump.inputs['Height'])
    links.new(bump.outputs[0],p.inputs['Normal'])
    if lining<1:
        coverage=nodes.new('ShaderNodeMapRange')
        coverage.inputs['To Min'].default_value=lining
        links.new(tex.outputs['Color'],coverage.inputs['Value'])
        links.new(coverage.outputs[0],p.inputs['Alpha'])
    p.inputs['Sheen Weight'].default_value=.32
    p.inputs['Roughness'].default_value=.69
    return m

# Row/column UVs keep the embroidery on the bias-cut cloth as it turns.
def dress(obj,mat,layout=None):
    mesh=obj.data
    if layout:
        cols,rows,around,length,closed=layout
        uv=mesh.uv_layers.new(name='Botanical yardage')
        uv.active_render=True
        mesh.uv_layers.active=uv
        for face in mesh.polygons:
            seam=closed and max(i%cols for i in face.vertices)-min(i%cols for i in face.vertices)>cols/2
            for k in face.loop_indices:
                row,col=divmod(mesh.loops[k].vertex_index,cols)
                if seam and col==0:
                    col=cols
                uv.data[k].uv=(col*around/(cols if closed else cols-1),row*length/(rows-1))
    mesh.materials.clear()
    mesh.materials.append(mat)
    for face in mesh.polygons:
        face.material_index=0

lined=fabric('corded ivory over warm lining',1,.47)
wrap=fabric('embroidered shoulder net',.58,.51)
outer=fabric('openwork skirt and mantle',.28,.56)
sleeve=fabric('fine sleeve net',.13,.54)
face=fabric('white lined face veil',1,.68)
hood=fabric('lined hood embroidery',1,.57,16)
glove=fabric('lined ivory glove lace',1,.63,39)
for key,mat,layout in [
    ('softly fitted covered gown',lined,(192,190,16,21,True)),
    ('diagonal waist and skirt drape',outer,(90,150,7,13,False)),
    ('flowing back mantle',outer,(120,180,12,18,False)),
    ('diagonal shoulder cowl',wrap,(180,65,10,4,True)),
    ('opaque shaped face veil',face,(90,110,4,7,False)),
    ('rounded outer hood',hood,None),
    ('continuous fitted sleeve',lined,(64,110,4,10,True)),
    ('hanging sleeve drape',sleeve,(50,90,4,4,False)),
    ('tailored glove cuff',lined,(64,20,4,1,True)),
    ('Fit05 posed glove',glove,None)]:
    matches=[o for o in collection.objects if key in o.name and not o.hide_render]
    assert matches,key
    for obj in matches:
        dress(obj,mat,layout)
scene['botanical_lace']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

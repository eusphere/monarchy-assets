"""Shape the bias folds and place embroidery along the shoulder wrap and overskirt."""
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
assert scene.get('botanical_lace') and not scene.get('placed_lace')
pieces = bpy.data.collections['V003 - fitting 04 tailored']
wrap = pieces.objects['Fit04 retained continuous diagonal shoulder cowl']
skirt = pieces.objects['Fit04 retained diagonal waist and skirt drape']

# Stagger the shoulder folds as they sweep over the chest and gather to one side.
for j in range(65):
    t = j/64
    for i in range(180):
        a = math.tau*i/180
        v = wrap.data.vertices[j*180+i]
        front = max(0,-math.sin(a))
        bias = .14*math.cos(a+.22) + .045*math.sin(2*a)
        ridge = 0
        for h,w,depth in ((.25,.055,.013),(.53,.075,.021),(.80,.060,.016)):
            offset = t-h-bias
            ridge += depth*(math.exp(-(offset/w)**2) - .47*math.exp(-((offset-.076)/(.65*w))**2))
        v.co.y -= ridge * front * math.sin(math.pi*t)**.55
        v.co.z += .035*math.cos(a)*front*math.sin(math.pi*t)

# A separate normalized UV map controls placement while the original UV map
# continues to govern thread size and direction.
def place_lace(obj, cols, rows, closed, quiet):
    mesh = obj.data
    yardage = mesh.uv_layers.active.name
    placement = mesh.uv_layers.new(name='Distance along panel')
    for poly in mesh.polygons:
        for k in poly.loop_indices:
            row,col = divmod(mesh.loops[k].vertex_index,cols)
            placement.data[k].uv=(col/(cols-1),row/(rows-1))
    mesh.uv_layers[yardage].active_render=True
    mesh.uv_layers.active=mesh.uv_layers[yardage]
    mat=mesh.materials[0].copy()
    mat.name='Placed ivory lace - '+obj.name
    mesh.materials[0]=mat
    tree=mat.node_tree
    tex=next(n for n in tree.nodes if n.type=='TEX_IMAGE')
    coord=tree.nodes.new('ShaderNodeUVMap')
    coord.uv_map=placement.name
    axes=tree.nodes.new('ShaderNodeSeparateXYZ')
    tree.links.new(coord.outputs[0],axes.inputs[0])
    border=tree.nodes.new('ShaderNodeValToRGB')
    stops=border.color_ramp
    stops.interpolation='EASE'
    levels=[(0,.72),(.055,.35),(.13,quiet),(.78,quiet),(.85,.37),(.91,1),(1,1)]
    stops.elements.remove(stops.elements[1])
    for index,(pos,val) in enumerate(levels):
        e=stops.elements.new(pos) if index else stops.elements[0]
        e.color=(val,val,val,1)
    tree.links.new(axes.outputs['Y'],border.inputs[0])
    # Quiet the yarn contrast while keeping mid-panel cloth dense enough to model light.
    mix=tree.nodes.new('ShaderNodeMixRGB')
    mix.inputs[1].default_value=(.36,.36,.36,1)
    destinations=[link.to_socket for link in tex.outputs['Color'].links]
    tree.links.new(border.outputs[0],mix.inputs[0])
    tree.links.new(tex.outputs['Color'],mix.inputs[2])
    for socket in destinations:
        tree.links.new(mix.outputs[0],socket)

    # Couch two cords into the border, with one following a shallow scallop.
    thread=bpy.data.materials['Fit04 hood hem ivory thread']
    for line in range(2):
        curve=bpy.data.curves.new('Couched border thread','CURVE')
        curve.dimensions='3D'
        curve.bevel_depth=.0011 if line==0 else .00085
        curve.bevel_resolution=3
        spline=curve.splines.new('POLY')
        spline.points.add(cols-1)
        for i,point in enumerate(spline.points):
            phase=i/(cols if closed else cols-1)*math.tau*(16 if closed else 10)
            row=(rows-1)*(.980 if line==0 else .950+.014*math.cos(phase))
            idx=int(row)*cols+i
            vertex=mesh.vertices[idx]
            p=vertex.co.lerp(mesh.vertices[idx+cols].co,row%1)
            normal=vertex.normal.copy()
            if normal.dot(Vector((p.x,p.y,0)))<0:
                normal.negate()
            point.co=(*(p+normal*.0016),1)
        spline.use_cyclic_u=closed
        edging=bpy.data.objects.new(obj.name+' ivory cord '+str(line+1),curve)
        pieces.objects.link(edging)
        curve.materials.append(thread)

wrap.data.update()
place_lace(wrap,180,65,True,.20)
place_lace(skirt,90,150,False,.24)
scene['placed_lace']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

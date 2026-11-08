"""Non-destructive first sculpt/detail pass over the approved C2 silhouette."""
import bpy, math, random
from mathutils import Vector
SRC='C2 - Veiled Vesper'; DST='C3 - Vesper sculpt'
if bpy.data.collections.get(DST): raise RuntimeError('C3 exists; refusing to overwrite')
source=bpy.data.collections.get(SRC)
if not source: raise RuntimeError('Approved C2 collection missing')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-sculpt-v002.blend',copy=True)
coll=bpy.data.collections.new(DST);bpy.context.scene.collection.children.link(coll)

def mat(name,col,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.77;p.inputs['Metallic'].default_value=metal
 return m
cloth=mat('Sculpt - ivory silk with weathered hem',(.76,.72,.62))
n=cloth.node_tree.nodes;l=cloth.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED')
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],noise.inputs['Vector'])
height=n.new('ShaderNodeMath');height.operation='MULTIPLY';height.inputs[1].default_value=3.8;l.new(sep.outputs['Z'],height.inputs[0])
add=n.new('ShaderNodeMath');add.operation='ADD';l.new(height.outputs[0],add.inputs[0]);l.new(noise.outputs['Fac'],add.inputs[1])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.065,.042,.023,1);ramp.color_ramp.elements[1].position=1;ramp.color_ramp.elements[1].color=(.76,.72,.62,1);ramp.color_ramp.elements.new(.6).color=(.36,.29,.19,1);l.new(add.outputs[0],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=650;fine.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],fine.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.0008;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
veilmat=cloth.copy();veilmat.name='Sculpt - opaque white veil';vp=next(n for n in veilmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');vp.inputs['Sheen Weight'].default_value=.25
skin=mat('Sculpt - pale hands',(.43,.32,.24));blood=mat('Sculpt - dried blood',(.10,.009,.008));gold=mat('Sculpt - worn pale gold',(.32,.22,.09),.7)

def newmesh(name,vs,fs,material):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o);o.data.materials.append(material)
 for f in d.polygons:f.use_smooth=True
 return o

def interp(points,t):
 # Catmull-Rom preserves the source silhouette with softer cloth transitions.
 f=t*(len(points)-1);i=min(int(f),len(points)-2);u=f-i
 a=Vector(points[max(0,i-1)]);b=Vector(points[i]);c=Vector(points[i+1]);d=Vector(points[min(len(points)-1,i+2)])
 return .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
for original in source.objects:
 if 'unarmed hand' in original.name:continue
 o=original.copy();o.data=original.data.copy();o.name=original.name.replace('C2','C3');coll.objects.link(o)
 o.data.materials.clear();o.data.materials.append(gold if ('diadem' in o.name or 'ornament' in o.name) else veilmat if 'face veil' in o.name else cloth)
 if any(m.type=='SUBSURF' for m in o.modifiers):
  # Replace the sparse flat strips with shaped, finely sampled folds.
  vertices=[v.co.copy() for v in original.data.vertices];centers=[(vertices[i]+vertices[i+1])*.5 for i in range(0,len(vertices),2)];widths=[(vertices[i+1].x-vertices[i].x)*.5 for i in range(0,len(vertices),2)]
  vs=[];fs=[];rows=100;cols=32
  for j in range(rows):
   t=j/(rows-1);center=interp(centers,t);w=interp([(v,0,0) for v in widths],t).x
   for k in range(cols):
    u=2*k/(cols-1)-1
    fold=.014*math.cos(u*math.pi*3.5+t*1.8)+.006*math.sin(u*math.pi*7-t*3)
    y=center.y+fold*(.4+.6*math.sin(math.pi*t))+.015*u*u
    z=center.z+.012*math.sin(u*5+t*2)*(t**5)
    vs.append((center.x+u*w,y,z))
  for j in range(rows-1):
   for k in range(cols-1):a=j*cols+k;fs.append((a,a+1,a+1+cols,a+cols))
  d=bpy.data.meshes.new(o.name+' sculpt surface');d.from_pydata(vs,[],fs);d.update();o.data=d;o.data.materials.append(cloth)
  for m in list(o.modifiers):o.modifiers.remove(m)
  sol=o.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.006
  for f in d.polygons:f.use_smooth=True
 else:
  if not ('diadem' in o.name or 'ornament' in o.name):
   bpy.context.view_layer.objects.active=o;o.select_set(True)
   sub=o.modifiers.new('Sculpt surface subdivision','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=3
   bpy.ops.object.modifier_apply(modifier=sub.name);o.select_set(False)
   for v in o.data.vertices:
    x,y,z=v.co
    if 'gown' in o.name:
     angle=math.atan2(y,x);wave=.004*math.sin(z*22+angle*3)+.003*math.cos(z*43-angle*7)
     v.co.x+=wave*math.cos(angle);v.co.y+=wave*math.sin(angle)
     if z<.15:v.co.z+=.008*math.sin(angle*9)*(1-z/.15)
    elif 'face veil' in o.name:
     v.co.y+=.003*math.sin(z*27+x*50)+.002*math.sin(x*110+z*3)
    elif 'hood' in o.name:
     v.co.y+=.004*math.sin(z*25+x*32)
   if not any(m.type=='SOLIDIFY' for m in o.modifiers):o.modifiers.new('Cloth body thickness','SOLIDIFY').thickness=.004

# Hand anatomy: palms, wrists, four gently articulated fingers, and opposing thumbs.
def sphere(name,center,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=center);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=True
 return o

def segment(name,a,b,r,material):
 a=Vector(a);b=Vector(b);o=sphere(name,(a+b)/2,(r,r,(b-a).length/2+r),material);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
random.seed(8)
for side,z in [(-1,1.30),(1,1.11)]:
 parts=[];center=Vector((side*.15,-.31,z+.02))
 # Raised left hand and lower open right hand share deliberate slender proportions.
 direction=Vector((-.10*side,-.18,.98 if side<0 else -.98)).normalized();across=Vector((1,0,.10*side)).normalized()
 palm=sphere('C3 palm',center,(.033,.021,.052),skin);parts.append(palm)
 parts.append(segment('C3 wrist',center-direction*.07,center-direction*.025,.022,skin))
 for i,length in enumerate([.072,.084,.079,.062]):
  root=center+across*((i-1.5)*.017)+direction*.033
  bend=root+direction*length*.55+Vector((0,-.008,0))
  tip=root+direction*length+Vector((0,-.019,0))+across*((i-1.5)*.003)
  parts.append(segment('C3 finger proximal',root,bend,.008,skin));parts.append(segment('C3 finger distal',bend,tip,.0065,skin))
 root=center-across*.025;mid=root-across*.025+direction*.01;tip=mid+direction*.035+Vector((0,-.008,0))
 parts.extend([segment('C3 thumb base',root,mid,.010,skin),segment('C3 thumb tip',mid,tip,.008,skin)])
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=palm;bpy.ops.object.join();palm.name='C3 sculpted healing hand '+('raised' if side<0 else 'lowered')
 rem=palm.modifiers.new('Unified hand surface','REMESH');rem.mode='VOXEL';rem.voxel_size=.003;bpy.ops.object.modifier_apply(modifier=rem.name)
 sm=palm.modifiers.new('Gentle sculpt polish','SMOOTH');sm.factor=.6;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
 for f in palm.data.polygons:f.use_smooth=True

# Sparse surface specks on the front veil, kept below the concealed face.
for i in range(18):
 x=random.uniform(-.10,.11);z=random.uniform(1.40,1.64)
 # Original veil lies near y=-.19, add a restrained raised stain surface.
 y=-.168-.035*(1-(x/.15)**2)+.006*math.cos(x/.15*math.pi*6)+.025*((1.91-z)/.52)-.006
 sphere('C3 sparse blood fleck',(x,y,z),(random.uniform(.0008,.0028),.001,random.uniform(.001,.004)),blood)
# Irregular dried blood embedded in the hand shader rather than raised dots.
n=skin.node_tree.nodes;l=skin.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=42;tex.inputs['Detail'].default_value=4;tex.inputs['Roughness'].default_value=.8
geo=n.new('ShaderNodeNewGeometry');l.new(geo.outputs['Position'],tex.inputs[0])
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.38;r.color_ramp.elements[0].color=(.065,.008,.006,1);r.color_ramp.elements[1].position=.52;r.color_ramp.elements[1].color=(.43,.32,.24,1);l.new(tex.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],p.inputs['Base Color'])

source.hide_render=True;source.hide_viewport=True
scene=bpy.context.scene;cam=scene.camera;cam.location=(2.4,-8,2.65);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.55
scene.render.resolution_x=1100;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/vesper-sculpt-v003.png'
# Use a darker backdrop to read the white veil and fine folds.
scene.world.color=(.055,.055,.055)
scene.eevee.taa_render_samples=64
bpy.ops.object.select_all(action='DESELECT')
scene['sculpt_stage']='First sculpt pass: layered cloth, hand forms, weathering. Retopology, UV baking and rigging pending.'
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer.blend')
bpy.ops.render.render(write_still=True)
print('Saved sculpt and rendered preview:',scene.render.filepath)

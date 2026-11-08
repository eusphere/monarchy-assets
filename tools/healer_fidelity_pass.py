"""C4 art-source pass: cloth tension, tailored edges, hands and ceremonial detail."""
import bpy, math
from mathutils import Vector
src=bpy.data.collections['C3 - Vesper sculpt']
if bpy.data.collections.get('C4 - Vesper detailed source'):raise RuntimeError('C4 already exists')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-detail-v003.blend',copy=True)
coll=bpy.data.collections.new('C4 - Vesper detailed source');bpy.context.scene.collection.children.link(coll)
objects={}
for old in src.objects:
 o=old.copy();o.data=old.data.copy();o.name=old.name.replace('C3','C4');coll.objects.link(o);objects[old.name]=o
src.hide_render=True;src.hide_viewport=True
cloth=bpy.data.materials['Sculpt - ivory silk with weathered hem'];gold=bpy.data.materials['Sculpt - worn pale gold'];skin=bpy.data.materials['Sculpt - pale hands']
# Use discrete dense folds with varied widths, converging towards their attachment points.
for o in coll.objects:
 if o.type!='MESH' or any(s in o.name for s in ['blood','diadem','ornament','hand']):continue
 if len(o.data.vertices)==3200:
  cols=32;rows=100
  # Reconstruct the centerline, retaining the approved cut and overall width.
  for j in range(rows):
   t=j/(rows-1);row=[o.data.vertices[j*cols+k] for k in range(cols)]
   cy=sum(v.co.y for v in row)/cols
   for k,v in enumerate(row):
    u=2*k/(cols-1)-1
    # Broad, irregular hanging folds; finer compression only near attachments.
    phase=(u+.08*math.sin(t*5))*math.pi
    main=.015*math.cos(phase*2.3+.7*math.sin(t*4))+.008*math.cos(phase*4.2-t*1.7)
    tension=.005*math.sin(t*46+u*9)*math.exp(-t*5)
    edge=.006*math.exp(-((abs(u)-.91)/.09)**2)
    v.co.y=cy+main*(.35+.65*math.sin(t*math.pi*.8))+tension+edge
    # Uneven, gently scalloped cloth ends, with no repetitive sawtooth pleats.
    v.co.z+=.005*math.sin(u*5+.7)*(t**10)
  sub=o.modifiers.new('Secondary fold surface','SUBSURF');sub.levels=2
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.modifier_move_up(modifier=sub.name)
  bpy.ops.object.modifier_apply(modifier=sub.name)
 elif 'gown' in o.name:
  for v in o.data.vertices:
   x,y,z=v.co;a=math.atan2(y,x);low=max(0,1-z/.45)
   # Fabric bunches above contact; long folds taper towards the waist.
   bulge=.009*math.sin(z*36+2*math.sin(a*3))*low + .004*math.sin(z*61+a*4)*low
   v.co.x+=bulge*math.cos(a);v.co.y+=bulge*math.sin(a)
 elif 'face veil' in o.name:
  for v in o.data.vertices:
   x,y,z=v.co;t=max(0,min(1,(1.91-z)/.52))
   v.co.y+=.005*math.sin(x*35+z*4)*math.sin(t*math.pi)+.002*math.sin(z*37+x*9)*(t**4)
   v.co.z+=.012*math.cos(x*13)*(t**8)
 elif 'hood' in o.name:
  for v in o.data.vertices:
   x,y,z=v.co;a=math.atan2(y-.04,x)
   v.co.y+=.006*math.sin(a*5+z*10)*max(0,1-abs(z-1.7)/.4)

# Fine piping and seams are separate editable curves, kept subtle.
def curve(name,points,rad,material):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=rad;d.bevel_resolution=3
 sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(material);return o

def sphere(name,center,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=center);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=True
 return o

def newmat(name,col,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
thread=newmat('C4 ivory seam thread',(.49,.44,.35));nailmat=newmat('C4 aged natural nails',(.38,.29,.22));crease=newmat('C4 skin crease',(.21,.13,.09));stone=newmat('C4 dark garnet ornament',(.045,.008,.012),.23)
# Hood framing: a clean sewn border around the face-covering fabric.
for side in [-1,1]:
 pts=[]
 for i in range(60):
  t=i/59;pts.append((side*(.105+.095*t),-.111-.05*math.sin(math.pi*t),2.02-.54*t))
 curve('C4 tailored hood border',pts,.0024,thread)
# Hem stitch line and restrained tiny stitch runs.
pts=[]
for i in range(257):
 a=i/256*math.pi*2;r=.312+.013*math.cos(a*14);pts.append((r*math.cos(a),(.231+.008*math.cos(a*14))*math.sin(a),.06+.004*math.sin(a*9)))
curve('C4 sewn gown hem',pts,.0013,thread)

# Improve the continuity of the wrists and cuffs without increasing shoulder width.
for side,z in [(-1,1.30),(1,1.11)]:
 center=Vector((side*.15,-.31,z+.02));direction=Vector((-.10*side,-.18,.98 if side<0 else -.98)).normalized();across=Vector((1,0,.10*side)).normalized()
 wrist=center-direction*.06
 sleeve=Vector((side*.20,-.25,z))
 # A skin bridge under a fitted textile cuff meets the existing pose.
 mid=(wrist+sleeve)*.5
 ob=sphere('C4 wrist transition',mid,(.022,.022,(wrist-sleeve).length*.5+.025),skin);ob.rotation_euler=(wrist-sleeve).to_track_quat('Z','Y').to_euler()
 axis=(wrist-sleeve).normalized();basis=axis.cross(Vector((0,0,1)))
 if basis.length<.01:basis=axis.cross(Vector((0,1,0)))
 basis.normalize();other=axis.cross(basis).normalized()
 for offset in [0,.012]:
  p=sleeve+axis*offset;pts=[p+.028*(math.cos(t*2*math.pi/64)*basis+math.sin(t*2*math.pi/64)*other) for t in range(65)]
  curve('C4 cuff stitching',pts,.0014,thread)
 hand=objects['C3 sculpted healing hand '+('raised' if side<0 else 'lowered')]
 sub=hand.modifiers.new('Hand polish surface','SUBSURF');sub.levels=2
 bpy.context.view_layer.objects.active=hand;bpy.ops.object.modifier_apply(modifier=sub.name)
 # Small nail beds and finger joint creases distinguish anatomy from the blockout.
 for i,length in enumerate([.072,.084,.079,.062]):
  root=center+across*((i-1.5)*.017)+direction*.033
  tip=root+direction*length+Vector((0,-.019,0))+across*((i-1.5)*.003)
  pos=tip-direction*.008+Vector((0,.0055,0))
  nail=sphere('C4 finger nail',pos,(.0045,.0018,.0075),nailmat);nail.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
  joint=root+direction*(length*.53)+Vector((0,-.015,0))
  pts=[joint+across*((k/10-.5)*.010)+direction*(.001*math.cos(k/10*math.pi)) for k in range(11)]
  curve('C4 finger flexion crease',pts,.0005,crease)
 # Subtle back-of-hand tendons, very low relief rather than large cords.
 for i in [-1,0,1]:
  pts=[center+across*(i*.012)+direction*(t*.044-.025)+Vector((0,.019+.001*math.sin(t*math.pi),0)) for t in [j/20 for j in range(21)]]
  curve('C4 hand tendon',pts,.0012,skin)

# Engraved crescent edging and a single garnet setting preserve the simple silhouette.
for side in [-1,1]:
 pts=[]
 for j in range(60):
  t=j/59;x=side*(.04+.213*t);z=2.007+.073*t*t
  pts.append((x,-.085,z))
 curve('C4 inset crescent engraving',pts,.0018,thread)
 for i in range(5):
  t=(i+1)/7;x=side*(.04+.213*t);z=2.007+.073*t*t
  sphere('C4 diadem granulation',(x,-.087,z+.014),(.0026,.0026,.0026),gold)
center=objects['C3 central diadem ornament'];center.data.materials.clear();center.data.materials.append(gold)
sphere('C4 set garnet',(0,-.112,2.02),(.012,.006,.019),stone)
# Small side ornaments hang close to the veil, rather than widening the crest.
for side in [-1,1]:
 pts=[(side*(.19+.003*math.sin(i*.6)),-.06,1.99-i*.006) for i in range(22)]
 curve('C4 temple chain',pts,.0016,gold)
 sphere('C4 temple drop',(side*.19,-.06,1.85),(.009,.005,.018),gold)
scene=bpy.context.scene;cam=scene.camera
cam.location=(2.0,-8,2.5);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
scene.render.resolution_x=1500;scene.render.resolution_y=1900;scene.eevee.taa_render_samples=96
scene.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/vesper-detail-v004.png'
scene['sculpt_stage']='C4 detailed source; procedural materials unbaked; retopology and rigging pending'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer.blend')
bpy.ops.render.render(write_still=True)
print('Saved fidelity pass and hero render')

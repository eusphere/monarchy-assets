"""Fit03: clean ivory, slender gloved hands, feminine garment silhouette."""
import bpy, math
from mathutils import Vector, Matrix
NAME='V003 - fitting 03 gloved'
if bpy.data.collections.get(NAME):raise RuntimeError('Fit03 exists; refusing overwrite')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-fit03.blend',copy=True)
s=bpy.context.scene;src=bpy.data.collections['V003 - fitting 02'];coll=bpy.data.collections.new(NAME);s.collection.children.link(coll)
# New clean materials isolate the change from historical checkpoints.
def material(name,col,rough=.72):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 return m
cloth=material('Fit03 clean ivory woven cloth',(.75,.72,.65));veil=material('Fit03 clean opaque veil',(.81,.79,.72));glove=material('Fit03 ivory gloves with intentional blood',(.72,.68,.59),.63)
# Subtle fabric surface only; no height-based dirt ramp or weathering.
for m in [cloth,veil,glove]:
 n=m.node_tree.nodes;l=m.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=850;noise.inputs['Detail'].default_value=1
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.10;b.inputs['Distance'].default_value=.0003;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
for old in src.objects:
 if old.hide_render or old.hide_get():continue
 if 'temporary sculpted healing hand' in old.name:continue
 o=old.copy();o.data=old.data.copy();o.name=old.name.replace('Fit02','Fit03',1);coll.objects.link(o)
 if 'headpiece' not in o.name:
  o.data.materials.clear();o.data.materials.append(veil if 'veil' in o.name else cloth)
src.hide_render=True;src.hide_viewport=True
# Continuous smoothly interpolated tailoring profiles: fully covered, not skin tight.
def interp(points,z):
 for i in range(len(points)-1):
  if points[i][0]<=z<=points[i+1][0]:
   t=(z-points[i][0])/(points[i+1][0]-points[i][0]);t=t*t*(3-2*t)
   return points[i][1]*(1-t)+points[i+1][1]*t
 return points[0][1] if z<points[0][0] else points[-1][1]
# Re-form foundation with a defined waist, modest bust and hips, and a loose skirt.
gown=bpy.data.objects['Fit03 fitted foundation gown'];N=160;R=145
oldprofiles=[(.02,.325,.23),(.12,.31,.22),(.45,.255,.185),(.82,.205,.145),(1.02,.16,.12),(1.15,.145,.12),(1.35,.185,.14),(1.53,.215,.12),(1.61,.075,.07)]
def original_sample(t):
 f=t*(len(oldprofiles)-1);i=min(int(f),len(oldprofiles)-2);u=f-i;return Vector(oldprofiles[i]).lerp(Vector(oldprofiles[i+1]),u)
xprof=[(.02,.31),(.45,.255),(.80,.205),(.96,.192),(1.10,.132),(1.20,.127),(1.33,.158),(1.43,.19),(1.53,.205),(1.61,.075)]
yprof=[(.02,.22),(.45,.18),(.80,.14),(.96,.14),(1.10,.105),(1.20,.10),(1.33,.12),(1.43,.145),(1.53,.115),(1.61,.07)]
for j in range(R):
 t=j/(R-1);z,_,_=original_sample(t);rx=interp(xprof,z);ry=interp(yprof,z)
 for i in range(N):
  a=i/N*2*math.pi;x=rx*math.cos(a);y=ry*math.sin(a)
  front=max(0,-math.sin(a));bust=.024*(math.exp(-((x-.085)/.062)**2)+math.exp(-((x+.085)/.062)**2))*math.exp(-((z-1.425)/.085)**2)*front**3
  y-=bust
  folds=(.005*math.cos(a*11+.2*math.sin(a*3)+z))*(1-math.exp(-((z-1.15)/.25)**2))
  gown.data.vertices[j*N+i].co=(x+folds*math.cos(a),y+folds*.6*math.sin(a),z)
# Outer layers taper at the waist but leave room over the hips and loose hem.
for o in coll.objects:
 if not any(k in o.name for k in ['rear mantle','waist and skirt drape']):continue
 for v in o.data.vertices:
  x,y,z=v.co
  narrowing=math.exp(-((z-1.17)/.19)**2)
  # Mantle stays free at the back; narrowing affects lateral/front edges most.
  frontside=1 if 'skirt' in o.name else .45+.55*max(0,1-abs(y)/.25)
  v.co.x*=1-.24*narrowing*frontside
  if y<0:v.co.y*=1-.16*narrowing
# Let the shoulder cowl follow the covered bust without swelling the shoulders.
cowl=bpy.data.objects['Fit03 continuous diagonal shoulder cowl']
for v in cowl.data.vertices:
 x,y,z=v.co
 if y<0:
  fullness=.013*(math.exp(-((x-.085)/.075)**2)+math.exp(-((x+.085)/.075)**2))*math.exp(-((z-1.44)/.08)**2)
  v.co.y-=fullness
# Glove shader: localized dark-red palm/finger staining, not random skin mottling.
n=glove.node_tree.nodes;l=glove.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');att=n.new('ShaderNodeAttribute');att.attribute_name='Blood coverage'
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.72,.68,.59,1);mix.inputs[2].default_value=(.12,.008,.006,1);l.new(att.outputs['Fac'],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color'])
def sphere(name,pos,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def segment(name,a,b,r1,r2):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u);vs=[];fs=[];N=24;R=10
 for j in range(R):
  t=j/(R-1);p=a.lerp(b,t);r=r1*(1-t)+r2*t
  for i in range(N):q=i/N*math.pi*2;vs.append(p+r*(math.cos(q)*u+math.sin(q)*v))
 for j in range(R-1):
  for i in range(N):k=j*N+i;d=j*N+(i+1)%N;fs.append((k,d,d+N,k+N))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range((R-1)*N,R*N))])
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();o=bpy.data.objects.new(name,data);coll.objects.link(o);return o
for raised in [True,False]:
 # Build at the origin in a consistent anatomical frame, then position the whole glove.
 parts=[sphere('Slender glove palm',(0,0,0),(.024,.011,.035)),segment('Fitted glove wrist',(0,0,-.067),(0,0,-.023),.014,.017)]
 # Narrow palm, tapered fingers; unequal lengths, articulated spread, no nail geometry.
 for i,(length,rad) in enumerate([(.065,.0054),(.075,.0057),(.069,.0053),(.053,.0046)]):
  root=Vector(((i-1.5)*.0128,0,.024-abs(i-1.5)*.002))
  spread=(i-1.5)*.008
  middle=root+Vector((spread*.5,-.004,length*.52));tip=root+Vector((spread,-.012,length))
  parts.extend([segment('Gloved proximal digit',root,middle,rad,rad*.90),segment('Gloved distal digit',middle,tip,rad*.9,rad*.61),sphere('Rounded glove fingertip',tip,(rad*.62,rad*.62,rad*.78))])
 # Thumb has an opposing base, separate from the index knuckle.
 a=Vector((-.020,-.001,-.014));b=Vector((-.037,-.004,.001));d=Vector((-.043,-.012,.025))
 parts.extend([segment('Gloved thumb web',a,b,.008,.0065),segment('Gloved thumb',b,d,.0065,.0045),sphere('Thumb tip',d,(.0045,.0045,.005))])
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name='Fit03 slender ivory glove '+('raised' if raised else 'open')
 rem=hand.modifiers.new('Unified glove silhouette','REMESH');rem.mode='VOXEL';rem.voxel_size=.0012;bpy.ops.object.modifier_apply(modifier=rem.name)
 smooth=hand.modifiers.new('Glove surface polish','SMOOTH');smooth.factor=.5;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
 for f in hand.data.polygons:f.use_smooth=True
 hand.data.materials.append(glove)
 attr=hand.data.attributes.new('Blood coverage','FLOAT','POINT')
 for v in hand.data.vertices:
  x,y,z=v.co;palmside=max(0,min(1,(-y+.001)/.009));fingers=max(0,min(1,(z-.014)/.028));wristfade=max(0,min(1,(z+.035)/.035))
  edge=.72+.14*math.sin(x*170+z*65)+.1*math.sin(z*230-y*120)
  value=max(fingers*.88,palmside*edge)*wristfade;attr.data[v.index].value=max(0,min(.96,value))
 # Glove coordinates are at the palm origin, unlike the inherited old hand geometry.
 position=Vector((-.175,-.265,1.44)) if raised else Vector((.29,-.245,1.17))
 rotation=Matrix.Rotation(math.radians(-8 if raised else 112),3,'X')
 # Mirror the raised (right) hand: thumbs point toward the body's center.
 mirror=Matrix.Diagonal(Vector((-1 if raised else 1,1 if raised else -1,1)))
 for v in hand.data.vertices:
  if v.co.z>.025:v.co.z=.025+(v.co.z-.025)*.90
  v.co=position+rotation@mirror@v.co
 # Extend wrist to meet the existing cuff, without a bulbous exposed skin join.
 hand['design']='Slender fitted opaque ivory glove; intentional blood on palm and digits, clean wrist.'
# Neutral views for silhouette review.
from mathutils import Vector
cam=s.camera;cam.location=(1.1,-8,2.45);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.45
s.render.resolution_x=1200;s.render.resolution_y=1600;s.eevee.taa_render_samples=64
s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting03-front.png';s['sculpt_stage']='Fitting03 clean ivory, newly built slender gloves, feminine tailoring; draping still in development'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rot=cam.rotation_euler.copy();cam.location=(7,-.4,2.4);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting03-side.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting03-front.png'
print('Fit03 saved with clean cloth and rebuilt gloves.')

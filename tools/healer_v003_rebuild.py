"""Build a new v003 construction study; preserve previous sculpt experiments."""
import bpy, math
from mathutils import Vector
NAME='V003 - garment construction'
if bpy.data.collections.get(NAME):raise RuntimeError('Rebuild exists; refusing to overwrite')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-v003-rebuild.blend',copy=True)
for c in bpy.context.scene.collection.children:
 if c.name.startswith(('A -','B -','C -','C2','C3','C4')):c.hide_viewport=True;c.hide_render=True
coll=bpy.data.collections.new(NAME);bpy.context.scene.collection.children.link(coll)
bodycol=bpy.data.collections.new('V003 - body fitting scaffold');bpy.context.scene.collection.children.link(bodycol)
refs=bpy.data.collections.new('V003 - approved concept references');bpy.context.scene.collection.children.link(refs);refs.hide_render=True
cloth=bpy.data.materials['Sculpt - ivory silk with weathered hem']
veilmat=bpy.data.materials['Sculpt - opaque white veil']
def material(name,color,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
white=material('V003 matte white carved ivory',(.77,.75,.68),.5)
under=material('V003 fitting body clay',(.22,.15,.12))
thread=material('V003 ivory seam',(.50,.46,.36))
def mesh(name,vs,fs,mat=cloth,collection=None):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);(collection or coll).objects.link(o);d.materials.append(mat)
 for p in d.polygons:p.use_smooth=True
 return o
def surface_finish(o,thick=.004,sub=1):
 if sub:m=o.modifiers.new('Surface continuity','SUBSURF');m.levels=sub
 if thick:m=o.modifiers.new('Physical fabric edge','SOLIDIFY');m.thickness=thick
 return o
def sample(points,t):
 f=t*(len(points)-1);i=min(int(f),len(points)-2);u=f-i
 return Vector(points[i]).lerp(Vector(points[i+1]),u)
def ellipsoid(name,p,scale,collection=bodycol,mat=under):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p);o=bpy.context.object;o.name=name;o.scale=scale
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
 return o
def limb(name,a,b,r1,r2,collection=coll,mat=cloth,fold=.002):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u);vs=[];fs=[];N=48;R=25
 for j in range(R):
  t=j/(R-1);p=a.lerp(b,t);r=r1*(1-t)+r2*t
  for i in range(N):
   q=2*math.pi*i/N;wr=fold*math.sin(t*math.pi*12+q*2)*(math.sin(math.pi*t)**2)
   vs.append(p+(r+wr)*(u*math.cos(q)+v*math.sin(q)))
 for j in range(R-1):
  for i in range(N):k=j*N+i;n=j*N+(i+1)%N;fs.append((k,n,n+N,k+N))
 return surface_finish(mesh(name,vs,fs,mat,collection),.003,1)
# Proportion guide; not claimed as final anatomical sculpt.
for name,p,sc in [('pelvis',(0,.015,1.00),(.155,.105,.15)),('rib cage',(0,0,1.37),(.19,.115,.22)),('neck',(0,0,1.66),(.063,.063,.12)),('head',(0,0,1.85),(.115,.095,.165))]:ellipsoid('Fitting '+name,p,sc)
# Anatomical right is image-left in front view.
for s,z in [(-1,1.30),(1,1.11)]:
 shoulder=(s*.20,0,1.54);elbow=(s*.255,-.07,1.28);wrist=(s*.15,-.29,z+(.015 if s<0 else .075))
 limb('Fitting upper arm',shoulder,elbow,.055,.04,bodycol,under,0)
 limb('Fitting forearm',elbow,wrist,.04,.023,bodycol,under,0)
 limb('V003 fitted upper sleeve',shoulder,elbow,.063,.046)
 limb('V003 fitted forearm sleeve',elbow,wrist,.047,.028,fold=.003)
bodycol.hide_render=True
for o in bodycol.objects:o.hide_set(True)
# Gown: silhouette fitted through torso, widening gradually at the feet.
profiles=[(.02,.325,.23),(.12,.31,.22),(.45,.255,.185),(.82,.205,.145),(1.02,.16,.12),(1.15,.145,.12),(1.35,.185,.14),(1.53,.215,.12),(1.61,.075,.07)]
vs=[];fs=[];N=160;R=145
for j in range(R):
 t=j/(R-1);z,rx,ry=sample(profiles,t);weight=max(.12,1-abs(z-1.12)/.8)
 for i in range(N):
  a=2*math.pi*i/N;phase=a*11+.24*math.sin(a*3)+z*.6
  folds=(.010*math.cos(phase)+.004*math.cos(a*19-z*2))*(1-weight*.65)
  bunch=.007*math.sin(z*45+a*3)*max(0,1-z/.25)
  vs.append(((rx+folds+bunch)*math.cos(a),(ry+folds*.7+bunch)*math.sin(a),z+.006*math.sin(a*7)*max(0,1-z/.1)))
for j in range(R-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
surface_finish(mesh('V003 fitted foundation gown',vs,fs))
# Hood-mantle is a continuous open-front surface with an actual side/back volume.
# Rows from crown down to ground; front opening widens at the shoulders.
profiles=[(2.025,.008,.008,.01),(2.01,.07,.08,.08),(1.95,.135,.13,.27),(1.78,.17,.15,.35),(1.61,.21,.16,.50),(1.48,.255,.17,.70),(1.25,.255,.18,.76),(.85,.27,.20,.73),(.40,.30,.22,.72),(.04,.365,.27,.70)]
vs=[];fs=[];N=100;R=180
for j in range(R):
 t=j/(R-1);z,rx,ry,opening=sample(profiles,t)
 for i in range(N):
  u=i/(N-1);a=-math.pi/2+opening+(2*math.pi-2*opening)*u
  amp=.003+.009*max(0,(1.6-z)/1.6);fold=amp*(math.cos(a*9+z)+.35*math.cos(a*17-z*3))
  vs.append(((rx+fold)*math.cos(a),.04+(ry+fold)*math.sin(a),z+.007*math.sin(a*5)*max(0,1-z/.15)))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
mantle=surface_finish(mesh('V003 continuous hood and rear mantle',vs,fs),.004,1)
# Face-covering fabric has no nose or facial modeling; tension from top, loose below.
vs=[];fs=[];R=90;N=65
for j in range(R):
 t=j/(R-1);z=1.97-.43*t;w=.085+.035*math.sin(t*math.pi*.8)
 for i in range(N):
  u=2*i/(N-1)-1;dome=.025*(1-u*u)*math.sin(t*math.pi*.85)
  y=-.113-dome+.003*math.cos(u*15+t*2)*(.15+.85*t)
  vs.append((u*w,y,z+.012*math.cos(u*2)*t**7))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
surface_finish(mesh('V003 opaque suspended face veil',vs,fs,veilmat),.003,1)
# Broad shoulder wrap, continuous around body, with diagonal tension folds.
vs=[];fs=[];N=150;R=42
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  a=2*math.pi*i/N;x=(.21+.04*t)*math.cos(a);front=max(0,-math.sin(a));z=1.60-.22*t+.045*math.cos(a)*front
  radius=.145+.026*t+.012*math.sin(t*math.pi*5+a*1.5)
  y=radius*math.sin(a)-.015
  vs.append((x,y,z+.009*math.sin(a*3+t*8)))
for j in range(R-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
surface_finish(mesh('V003 wrapped shoulder shawl',vs,fs),.004,1)
# Bias-cut overskirt sweep anchored near the waist, with nonuniform broad folds.
vs=[];fs=[];R=130;N=75
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  u=i/(N-1);a=-math.pi*.87+u*math.pi*.88+.38*t
  radius=.172+.15*t;fold=.016*math.sin(u*math.pi*7+.8*t)*(t*.7+.3)+.005*math.cos(u*math.pi*13-t)
  z=1.15-t*(.99-.10*math.sin(u*math.pi))+.055*math.sin(u*math.pi*1.5)*(1-t)
  vs.append(((radius+fold)*math.cos(a),(radius*.73+fold)*math.sin(a)-.02,z))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
surface_finish(mesh('V003 bias-cut front drape',vs,fs),.004,1)
# Hanging sleeves are continuous tubes, instead of separate flat paddles.
for s in [-1,1]:
 vs=[];fs=[];N=72;R=70
 for j in range(R):
  t=j/(R-1);z=1.49-.69*t;cx=s*(.215+.03*math.sin(t*math.pi));cy=-.025-.045*t
  for i in range(N):
   a=2*math.pi*i/N;rx=.071+.014*t;ry=.08+.005*t;fold=.007*math.cos(a*7+t)
   vs.append((cx+(rx+fold)*math.cos(a),cy+(ry+fold)*math.sin(a),z+.06*math.sin(a)*t**3))
 for j in range(R-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 surface_finish(mesh('V003 hanging outer sleeve',vs,fs),.003,1)
# Reuse the existing hand studies as temporary placeholders, clearly labeled.
for old in bpy.data.collections['C4 - Vesper detailed source'].objects:
 if 'sculpted healing hand' in old.name:
  o=old.copy();o.data=old.data.copy();o.name=old.name.replace('C4','V003 temporary');coll.objects.link(o)
# Original white headpiece: a shallow transverse faceted bow with downward tips.
vs=[];fs=[];N=81
for j in range(N):
 x=-.36+.72*j/(N-1);u=abs(x)/.36
 top=2.10-.34*u**1.5;band=.078*(1-u**2)+.006
 for y,z in [(-.13,top),(-.145,top-band),(-.075,top-band+.006),(-.06,top+.006)]:vs.append((x,y,z))
for j in range(N-1):
 for k in range(4):a=j*4+k;b=j*4+(k+1)%4;fs.append((a,b,b+4,a+4))
fs.extend([(3,2,1,0),tuple(range((N-1)*4,N*4))])
head=mesh('V003 white inverted bowed headpiece',vs,fs,white)
for f in head.data.polygons:f.use_smooth=False
be=head.modifiers.new('Subtle carved bevel','BEVEL');be.width=.0025;be.segments=2
# Persist approved source images inside the file as optional inspection references.
for view,filename,x in [('front','angel-healer-v003.png',-2),('side','angel-healer-v003-side.png',0),('rear','angel-healer-v003-rear.png',2)]:
 image=bpy.data.images.load('/Users/adu/workspace/monarchy-assets/ideas/healer/concepts/'+filename,check_existing=True);image.pack()
 o=bpy.data.objects.new('V003 reference '+view,None);refs.objects.link(o);o.empty_display_type='IMAGE';o.data=image;o.empty_display_size=2.3;o.location=(x,1.2,1.1);o.rotation_euler=(math.pi/2,0,0);o.hide_render=True
refs.hide_viewport=True
scene=bpy.context.scene;cam=scene.camera;cam.location=(1.5,-8,2.6);cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
scene.render.resolution_x=1200;scene.render.resolution_y=1600;scene.eevee.taa_render_samples=64
scene.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-rebuild-construction.png';scene.render.image_settings.file_format='PNG'
scene['sculpt_stage']='V003 structural rebuild, no cloth simulation yet, temporary hand studies, no embroidery or rig'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer.blend');bpy.ops.render.render(write_still=True)
print('Saved V003 construction study')

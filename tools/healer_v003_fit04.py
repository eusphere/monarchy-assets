"""Fit04: rebuild the upper garments and gloves, clean materials, tailored flowing layers.
This is an editable modeled drapery study, not a cloth simulation or runtime asset.
"""
import bpy, math
from mathutils import Vector, Matrix
NAME='V003 - fitting 04 tailored'
if bpy.data.collections.get(NAME):raise RuntimeError('Fit04 already exists; will not overwrite')
s=bpy.context.scene;bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-fit04.blend',copy=True)
source=bpy.data.collections['V003 - fitting 03 gloved'];coll=bpy.data.collections.new(NAME);s.collection.children.link(coll)
source.hide_render=True;source.hide_viewport=True

def material(name,color,rough=.72,weave=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if weave:
  coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1100;noise.inputs['Detail'].default_value=1;l.new(coord.outputs['Object'],noise.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.00022;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 return m
cloth=material('Fit04 clean warm ivory cloth',(.76,.73,.66),.78,True)
veilmat=material('Fit04 opaque soft white veil',(.81,.79,.73),.82,True)
glove=material('Fit04 clean fitted ivory gloves - no blood',(.78,.75,.69),.61,True)
white=material('Fit04 matte carved white ivory',(.79,.77,.71),.52)
thread=material('Fit04 raised ivory stitching',(.57,.52,.42),.72)

def mesh(name,verts,faces,mat=cloth,sub=1,thick=.003):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(mat)
 for p in d.polygons:p.use_smooth=True
 if sub:q=o.modifiers.new('Smooth textile surface','SUBSURF');q.levels=sub
 if thick:q=o.modifiers.new('Textile thickness','SOLIDIFY');q.thickness=thick
 return o

def cat(points,t):
 f=t*(len(points)-1);i=min(int(f),len(points)-2);u=f-i
 a,b,c,d=[Vector(points[max(0,min(len(points)-1,k))]) for k in [i-1,i,i+1,i+2]]
 return .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u**3)

def interp(points,z):
 for i in range(len(points)-1):
  if points[i][0]<=z<=points[i+1][0]:
   t=(z-points[i][0])/(points[i+1][0]-points[i][0]);t=t*t*(3-2*t);return points[i][1]*(1-t)+points[i+1][1]*t
 return points[0][1] if z<points[0][0] else points[-1][1]

xprof=[(0,.32),(.35,.27),(.70,.22),(.92,.19),(1.06,.155),(1.18,.128),(1.28,.142),(1.40,.18),(1.48,.196),(1.55,.205),(1.64,.065)]
yprof=[(0,.23),(.35,.185),(.70,.15),(.92,.14),(1.06,.117),(1.18,.099),(1.28,.106),(1.40,.136),(1.48,.134),(1.55,.11),(1.64,.06)]
def bodyfront(x,z):
 rx=interp(xprof,z);ry=interp(yprof,z)
 depth=ry*math.sqrt(max(.02,1-(x/max(rx,.01))**2))
 bust=.020*(math.exp(-((x-.078)/.058)**2)+math.exp(-((x+.078)/.058)**2))*math.exp(-((z-1.425)/.085)**2)
 return -depth-bust
# Continuous, softly tailored gown, with broad asymmetric lower folds.
vs=[];fs=[];N=192;R=190
for j in range(R):
 t=j/(R-1);z=.015+t*1.625;rx=interp(xprof,z);ry=interp(yprof,z)
 for i in range(N):
  a=2*math.pi*i/N;x=rx*math.cos(a);y=ry*math.sin(a);front=max(0,-math.sin(a))
  if y<0:y=bodyfront(x,z)
  fall=max(0,min(1,(1.10-z)/.9));fold=(.010*math.cos(a*9+.4*math.sin(a*2)+z*1.8)+.004*math.cos(a*14-z*2))*fall
  x+=fold*math.cos(a);y+=fold*.7*math.sin(a)
  hem=.006*math.sin(a*7)*max(0,1-z/.12)
  vs.append((x,y,z+hem))
for j in range(R-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
gown=mesh('Fit04 softly fitted covered gown',vs,fs)
# Fitted sleeves preserve the reviewed gesture. All materials are clean copies.
for old in source.objects:
 if 'continuous fitted sleeve' not in old.name:continue
 o=old.copy();o.data=old.data.copy();o.name=old.name.replace('Fit03','Fit04');coll.objects.link(o);o.data.materials.clear();o.data.materials.append(cloth)
# A rounded hood over the head, separate from the lower mantle, not one long cylinder.
profiles=[(2.025,.003,.006,.15),(2.01,.060,.073,.23),(1.97,.112,.11,.35),(1.88,.139,.133,.48),(1.76,.145,.125,.58),(1.65,.127,.108,.63),(1.57,.156,.12,.72)]
vs=[];fs=[];R=100;N=100
for j in range(R):
 z,rx,ry,opening=cat(profiles,j/(R-1))
 for i in range(N):
  u=i/(N-1);a=-math.pi/2+opening+(2*math.pi-2*opening)*u
  f=.0025*math.cos(a*7+z*9)*max(0,(1.99-z)/.42)
  vs.append(((rx+f)*math.cos(a),.023+(ry+f)*math.sin(a),z))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
hood=mesh('Fit04 rounded outer hood',vs,fs,veilmat)
# Head covering gently follows a featureless head volume; no flat rectangular face patch.
vs=[];fs=[];R=110;N=90
for j in range(R):
 t=j/(R-1);z=1.995-.40*t
 width=interp([(0,.035),(.1,.088),(.35,.111),(.65,.108),(1,.088)],t)
 for i in range(N):
  u=2*i/(N-1)-1
  dome=.035*max(0,1-u*u)**.65*math.sin(math.pi*min(.95,t+.12))
  fold=.0018*math.sin(u*15+t*2)*max(0,(t-.45)/.55)
  vs.append((u*width,-.104-dome+fold,z+.014*(1-u*u)*t**6))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
face=mesh('Fit04 opaque shaped face veil - no facial features',vs,fs,veilmat)
# Back mantle opens in front and leaves the waist visible; gently flared lower fullness.
profiles=[(1.69,.105,.095,.75),(1.60,.20,.125,.85),(1.49,.235,.16,.91),(1.25,.208,.18,.95),(1.05,.194,.18,.94),(.80,.225,.195,.90),(.45,.269,.22,.88),(.06,.335,.29,.88)]
vs=[];fs=[];R=180;N=120
for j in range(R):
 t=j/(R-1);z,rx,ry,opening=cat(profiles,t)
 for i in range(N):
  u=i/(N-1);a=-math.pi/2+opening+(2*math.pi-2*opening)*u
  f=(.004+.008*t)*math.cos(a*8+.4*math.sin(a*3)+t*2)+.003*t*math.cos(a*13-t)
  train=.045*max(0,math.sin(a))*t**6
  vs.append(((rx+f)*math.cos(a),.040+(ry+f+train)*math.sin(a),z+.012*math.sin(a*6)*t**8))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
mantle=mesh('Fit04 open-front flowing back mantle',vs,fs)
# Supported bias-cut wraps: paths run over shoulder, across chest and down into a fall.
# Each surface follows the body envelope with deliberately varied fold widths.
def drape(name,points,widths,layer):
 vs=[];fs=[];edges=[[],[]];R=190;N=72
 for j in range(R):
  t=j/(R-1);p=cat(points,t);w=cat([(x,0,0) for x in widths],t).x
  tang=cat(points,min(1,t+.001))-cat(points,max(0,t-.001))
  cross=Vector((-tang.z,0,tang.x)).normalized()
  for i in range(N):
   u=2*i/(N-1)-1
   q=p+cross*(u*w)
   # Broad valleys/crests flow with the bias, tapering near attachment zones.
   fold=.0
   for pos,amp,spread in [(-.65,.011,.24),(-.12,.015,.27),(.47,.009,.22)]:
    d=(u-pos-.09*math.sin(t*4))/spread;fold+=amp*(1-d*d)*math.exp(-d*d*.5)
   amp=.35+.65*math.sin(math.pi*min(.95,t+.1))
   q.y-=fold*amp
   if -.22<q.x<.22 and .76<q.z<1.65:
    q.y=min(q.y,bodyfront(q.x,q.z)-.007-layer*.006-fold*.4)
   # Curved free end rather than a straight rigid cutoff.
   q.z+=.018*math.cos(u*2.0)*t**10
   vs.append(q)
  edges[0].append(vs[j*N]);edges[1].append(vs[j*N+N-1])
 for j in range(R-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
 o=mesh(name,vs,fs);return o,edges
wrapA,edgeA=drape('Fit04 shoulder wrap and left bias fall',[
 (-.205,.010,1.60),(-.155,-.145,1.575),(.045,-.170,1.49),(.195,-.075,1.425),(.145,-.120,1.28),(.015,-.157,1.10),(-.145,-.166,.72),(-.215,-.160,.125)],
 [.060,.085,.095,.070,.070,.115,.135,.120],0)
wrapB,edgeB=drape('Fit04 crossing wrap and right bias fall',[
 (.200,.015,1.57),(.12,-.145,1.54),(-.040,-.180,1.465),(-.185,-.092,1.405),(-.125,-.135,1.30),(.075,-.162,1.20),(.180,-.165,.87),(.235,-.180,.31)],
 [.060,.080,.083,.065,.067,.100,.130,.140],1)
# Very fine seam piping emphasizes layer separation without adding new ornaments.
def curve(name,points,rad,mat=thread):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=rad;d.bevel_resolution=2;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(mat);return o
for label,edges in [('A',edgeA),('B',edgeB)]:
 for i,edge in enumerate(edges):curve('Fit04 sewn wrap edge '+label+str(i),[(p.x,p.y-.0013,p.z) for p in edge],.0007)
# Shallow, bowed fore-aft profile; the previous profile was a deep flat slab.
vs=[];fs=[];N=101
for j in range(N):
 x=-.335+.67*j/(N-1);u=abs(x)/.335;top=2.075-.285*u**1.30;band=.060*(1-u**1.8)+.003
 bow=-.103+.057*u*u;depth=.024*(1-.65*u)
 for y,z in [(bow,top),(bow-.003,top-band),(bow+depth,top-band+.003),(bow+depth,top+.002)]:vs.append((x,y,z))
for j in range(N-1):
 for k in range(4):a=j*4+k;b=j*4+(k+1)%4;fs.append((a,b,b+4,a+4))
fs.extend([(3,2,1,0),tuple(range((N-1)*4,N*4))])
headpiece=mesh('Fit04 shallow bowed white headpiece',vs,fs,white,0,0)
for p in headpiece.data.polygons:p.use_smooth=False
q=headpiece.modifiers.new('Carved bevel','BEVEL');q.width=.0018;q.segments=3
# Glove construction: shaped metacarpal body, tapered articulated digits, no skin or blood shader.
def ellipsoid(name,pos,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o

def tube(name,path,radii):
 vs=[];fs=[];R=28;N=24
 for j in range(R):
  t=j/(R-1);p=cat(path,t);axis=(cat(path,min(1,t+.002))-cat(path,max(0,t-.002))).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u);r=cat([(x,0,0) for x in radii],t).x
  for i in range(N):a=i/N*2*math.pi;vs.append(p+r*(u*math.cos(a)+v*math.sin(a)))
 for j in range(R-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range((R-1)*N,R*N))])
 return mesh(name,vs,fs,glove,0,0)
for raised in [True,False]:
 pieces=[];vs=[];fs=[];R=18;N=40
 for j in range(R):
  t=j/(R-1);z=-.062+.089*t;rx=interp([(0,.014),(.35,.019),(.75,.026),(1,.023)],t);ry=interp([(0,.008),(.5,.011),(1,.008)],t)
  for i in range(N):a=i/N*2*math.pi;vs.append((rx*math.cos(a),ry*math.sin(a),z))
 for j in range(R-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range((R-1)*N,R*N))]);palm=mesh('Fit04 glove palm',vs,fs,glove,0,0);pieces.append(palm)
 for i,(length,radius) in enumerate([(.058,.0062),(.066,.0065),(.061,.0062),(.047,.0053)]):
  x=(i-1.5)*.0135;root=Vector((x,0,.021-abs(i-1.5)*.002));spread=(i-1.5)*.003
  if raised:
   path=[root,root+Vector((spread*.4,-.001,length*.36)),root+Vector((spread,-.010,length*.73)),root+Vector((spread*1.15,-.020,length*.90))]
  else:
   path=[root,root+Vector((spread*.4,-.001,length*.33)),root+Vector((spread,-.007,length*.68)),root+Vector((spread*1.2,-.016,length*.91))]
  pieces.append(tube('Fit04 articulated glove digit',path,[radius,radius*.95,radius*.78,radius*.50]));pieces.append(ellipsoid('Fit04 glove fingertip',path[-1],(radius*.5,radius*.5,radius*.63)))
 thumb=[(-.019,-.001,-.010),(-.032,-.010,.001),(-.039,-.018,.015),(-.034,-.025,.031)]
 pieces.append(tube('Fit04 opposing glove thumb',thumb,[.009,.008,.006,.0045]));pieces.append(ellipsoid('Fit04 thumb tip',thumb[-1],(.0045,.0045,.0055)))
 bpy.ops.object.select_all(action='DESELECT')
 for o in pieces:o.select_set(True)
 bpy.context.view_layer.objects.active=palm;bpy.ops.object.join();o=palm;o.name='Fit04 clean tailored glove '+('raised' if raised else 'open')
 q=o.modifiers.new('Unified glove skin','REMESH');q.mode='VOXEL';q.voxel_size=.00085;bpy.ops.object.modifier_apply(modifier=q.name)
 q=o.modifiers.new('Glove seam surface smoothing','SMOOTH');q.factor=.45;q.iterations=3;bpy.ops.object.modifier_apply(modifier=q.name)
 o.data.materials.clear();o.data.materials.append(glove)
 for p in o.data.polygons:p.use_smooth=True
 pos=Vector((-.175,-.265,1.44)) if raised else Vector((.29,-.245,1.17));rot=Matrix.Rotation(math.radians(-8 if raised else 112),3,'X');mirror=Matrix.Diagonal(Vector((-1 if raised else 1,1 if raised else -1,1)))
 for v in o.data.vertices:v.co=pos+rot@mirror@v.co
 # A fine glove back seam and cuff edge follow the same transformation.
 def world(q):return pos+rot@mirror@Vector(q)
 curve('Fit04 glove wrist seam',[world((.0143*math.cos(a*2*math.pi/64),.0083*math.sin(a*2*math.pi/64),-.055)) for a in range(65)],.00045)
# Save consistent full-figure review views.
s['sculpt_stage']='Fitting04: clean gloves, modeled bias-cut garment layers and hood rebuild. No simulation, retopology, rig or animation.'
s['material_direction']='No blood, dirt or soiling on any visible Fit04 surface.'
cam=s.camera;cam.location=(1.15,-8,2.42);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.43
s.render.resolution_x=1350;s.render.resolution_y=1800;s.eevee.taa_render_samples=80;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-front.png'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rot=cam.rotation_euler.copy()
for name,position,target,scale in [('side',(7,-.4,2.4),(0,0,1.045),2.43),('rear',(1.5,7,2.4),(0,0,1.045),2.43),('detail',(1.0,-6,2.15),(0,-.1,1.49),1.32)]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-'+name+'.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=2.43;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-front.png'
print('Fit04 saved; front, side, rear and detail rendered for review.')

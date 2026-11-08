"""Review pass 02: shoulder cowl, arm gesture, sleeve continuity and veil coverage."""
import bpy, math
from mathutils import Vector, Matrix
NAME='V003 - fitting 02'
if bpy.data.collections.get(NAME):raise RuntimeError('Fitting 02 already exists')
s=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-fit02.blend',copy=True)
source=bpy.data.collections['V003 - garment construction'];coll=bpy.data.collections.new(NAME);s.collection.children.link(coll)
for old in source.objects:
 if old.hide_render or old.hide_get():continue
 o=old.copy();o.data=old.data.copy();o.name=old.name.replace('V003','Fit02',1);coll.objects.link(o)
source.hide_render=True;source.hide_viewport=True
cloth=bpy.data.materials['Sculpt - ivory silk with weathered hem']
for o in list(coll.objects):
 if any(key in o.name for key in ['shoulder wrap','fitted upper sleeve','fitted forearm sleeve','hanging outer sleeve']):bpy.data.objects.remove(o,do_unlink=True)

def mesh(name,vs,fs,material=cloth,sub=1):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(material)
 for f in d.polygons:f.use_smooth=True
 if sub:m=o.modifiers.new('Tailored surface smoothing','SUBSURF');m.levels=sub
 m=o.modifiers.new('Fabric thickness','SOLIDIFY');m.thickness=.003
 return o

def bezier(points,t):
 a,b,c,d=map(Vector,points);return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
# A single cowl is shaped around neck and shoulders rather than a rigid chest band.
# The cloth edges follow different paths; major folds sag between shoulder support points.
N=180;R=65;vs=[];fs=[]
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  a=i/N*math.pi*2;front=max(0,-math.sin(a));back=max(0,math.sin(a));side=math.cos(a)
  # Narrow neckline widens over shoulders then returns onto upper ribs.
  bulge=math.sin(math.pi*t)**.7
  rx=.095+.137*bulge+.09*t;ry=.088+.062*bulge+.037*t
  # Difference in elevation makes the wrap cross diagonally across the front.
  z=1.66-.23*t-.065*front*math.sin(math.pi*t)+.070*side*front*(.3+.7*t)
  # Three broad folds taper at the shoulder and neck supports.
  fold=(.010*math.cos(t*math.pi*6+.7*side)+.003*math.cos(t*math.pi*10-side))*math.sin(math.pi*t)**.6
  x=(rx+fold*.6)*math.cos(a);y=(ry+fold)*math.sin(a)-.010
  # Catenary-like sag is largest at the unsupported front center.
  z-=.028*front**2*math.sin(math.pi*t)
  vs.append((x,y,z))
for j in range(R-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
cowl=mesh('Fit02 continuous diagonal shoulder cowl',vs,fs)
# Close the veil's upper gap, keeping all features concealed.
veil=next(o for o in coll.objects if 'opaque suspended face veil' in o.name)
for v in veil.data.vertices:
 z=v.co.z;top=max(0,min(1,(z-1.80)/.17));v.co.z+=.052*top;v.co.y+=.016*top
# Make the suspended fabric narrower at the neck and gently convex, rather than a flat curtain.
for v in veil.data.vertices:
 x,y,z=v.co;weight=max(0,1-abs(z-1.78)/.24);v.co.y-=.006*math.cos(x*22)*weight
# Preserve hand topology for now, but correct the gestures and their anatomical placement.
handmat=bpy.data.materials['Sculpt - pale hands'].copy();handmat.name='Fit02 pressure-stained hands'
n=handmat.node_tree.nodes
ramp=next((q for q in n if q.type=='VALTORGB'),None)
if ramp:
 ramp.color_ramp.elements[0].position=.39;ramp.color_ramp.elements[0].color=(.095,.009,.006,1)
 ramp.color_ramp.elements[-1].position=.66;ramp.color_ramp.elements[-1].color=(.39,.22,.14,1)
for o in coll.objects:
 if 'temporary sculpted healing hand' not in o.name:continue
 raised='raised' in o.name
 old=Vector((-.15,-.31,1.32)) if raised else Vector((.15,-.31,1.13))
 new=Vector((-.175,-.265,1.44)) if raised else Vector((.29,-.245,1.17))
 rotation=Matrix.Rotation(math.radians(-8 if raised else -68),3,'X')
 # Remeshed hand coordinates are local to the original palm object's location.
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;v.co=inv@(new+rotation@(p-old))
 o.data.materials.clear();o.data.materials.append(handmat)
# Continuous sleeves along a curved arm path, with a correctly placed elbow and cuff.
for side in [-1,1]:
 raised=side<0
 if raised:
  # shoulder to elbow; elbow to wrist rising toward the healing gesture
  first=[(-.195,.005,1.54),(-.235,.005,1.48),(-.265,-.025,1.31),(-.25,-.075,1.28)]
  second=[first[-1],(-.24,-.12,1.28),(-.19,-.22,1.34),(-.18,-.255,1.385)]
 else:
  first=[(.195,.005,1.54),(.23,.005,1.47),(.25,-.025,1.31),(.25,-.07,1.27)]
  second=[first[-1],(.26,-.12,1.25),(.28,-.18,1.20),(.288,-.208,1.19)]
 vs=[];fs=[];R=110;N=64
 for j in range(R):
  t=j/(R-1);p=bezier(first,t*2) if t<.5 else bezier(second,(t-.5)*2)
  eps=.001
  def path(q):return bezier(first,q*2) if q<.5 else bezier(second,(q-.5)*2)
  tangent=(path(min(1,t+eps))-path(max(0,t-eps))).normalized()
  u=tangent.cross(Vector((0,1,0))).normalized();v=tangent.cross(u)
  radius=.055*(1-t)+.026*t
  for i in range(N):
   a=i/N*math.pi*2
   # Finer compression folds collect near the elbow, not uniformly along the arm.
   compression=math.exp(-((t-.50)/.14)**2)
   r=radius+.003*math.cos(t*80+math.sin(a)*2)*compression
   pos=p+r*(u*math.cos(a)+v*math.sin(a));vs.append(pos)
 for j in range(R-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 mesh('Fit02 continuous fitted sleeve '+('raised' if raised else 'open'),vs,fs)
 # Separate hanging sleeve textile suspended from the upper arm, with an open fore edge.
 # This is an actual continuous cloth sheet, not a pipe with a floating top rim.
 vs=[];fs=[];R=90;N=50
 for j in range(R):
  t=j/(R-1);p=bezier(first,t)
  for i in range(N):
   w=i/(N-1);drop=(.06+.35*math.sin(t*math.pi*.8))*w
   y=p.y+.045-.09*w-.012*math.sin(w*math.pi*5+t*2)*math.sin(w*math.pi)
   x=p.x+side*(.045+.018*math.sin(w*math.pi*3+t)*w)
   z=p.z-drop
   vs.append((x,y,z))
 for j in range(R-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
 mesh('Fit02 hanging sleeve drape '+('right' if raised else 'left'),vs,fs)
# Replace the skirt's high horizontal bib edge with a diagonal bias fall from one hip.
old=next(o for o in coll.objects if 'bias-cut front drape' in o.name);old.hide_render=True;old.hide_set(True)
vs=[];fs=[];R=150;N=90
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  u=i/(N-1);a=-math.pi*.95+u*math.pi*.93+.55*t
  # Pinch near the right waist, then fan naturally across the lower gown.
  rad=.17+.16*t;gather=.009*math.sin(u*math.pi*7+.3*t)*(.2+.8*t)
  z=1.37-.28*u-t*(1.13-.20*u)
  x=(rad+gather)*math.cos(a);y=(rad*.73+gather)*math.sin(a)-.025
  vs.append((x,y,z))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
mesh('Fit02 diagonal waist and skirt drape',vs,fs)
# Studio exposure for inspection: keep white surfaces readable.
s.view_settings.exposure=-.45
s['sculpt_stage']='V003 fitting02: continuous cowl and sleeves, gesture correction. Construction stage; final draping, hands and embroidery pending.'
bpy.ops.object.select_all(action='DESELECT')
cam=s.camera;cam.location=(1.3,-8,2.5);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.45
s.render.resolution_x=1200;s.render.resolution_y=1600;s.eevee.taa_render_samples=64
s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rot=cam.rotation_euler.copy();cam.location=(7,-.4,2.4);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-side.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-front.png'
print('Fitting02 saved; front and side ready for review.')

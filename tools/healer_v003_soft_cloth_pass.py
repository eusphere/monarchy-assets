"""Focused art pass over the accepted hood layering and shoulder cowl."""
import bpy,math
from mathutils import Vector
s=bpy.context.scene
if s.get('soft_cloth_pass_01'):raise RuntimeError('Soft cloth pass already applied')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-soft-cloth.blend',copy=True)
backup=bpy.data.collections.new('Fit04 - before soft cloth pass');s.collection.children.link(backup);backup.hide_render=True;backup.hide_viewport=True
hood=bpy.data.objects['Fit04 rounded outer hood'];cowl=bpy.data.objects['Fit04 retained continuous diagonal shoulder cowl']
for old in [hood,cowl]:
 o=old.copy();o.data=old.data.copy();o.name=old.name+' prior soft cloth';backup.objects.link(o)
# Shape the hood's free border into a narrow turned hem and low-amplitude flowing folds.
# Fix the straight brow opening with a curved lower edge on the joined front crown.
N=100;R=100
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  u=i/(N-1);edge=min(u,1-u);v=hood.data.vertices[j*N+i];z=v.co.z
  rim=math.exp(-((edge-.024)/.023)**2)
  flow=math.exp(-((edge-.09)/.055)**2)
  # The headpiece and shoulder act as the upper and lower support regions.
  freedom=math.sin(math.pi*t)**1.2
  v.co.y-=.0045*rim*(.3+.7*freedom)
  v.co.y+=.0035*flow*math.sin(t*7+.4)*freedom
  v.co.x+=(-1 if v.co.x<0 else 1)*.0025*math.sin(t*6.5+.3)*flow*freedom
# The added brow patch has 31 rows of 29 new vertices after the original 10,000.
for j in range(31):
 t=j/30
 for k in range(1,30):
  v=hood.data.vertices[10000+j*29+k-1];u=k/30
  arch=math.sin(math.pi*u)**.9
  v.co.z+=.021*arch*t**3
  v.co.y-=.002*arch*t**2
# Sculpt major diagonal folds as a few varying crests and tight valleys.
N=180;R=65
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  a=i/N*2*math.pi;front=max(0,-math.sin(a));side=math.cos(a);bulge=math.sin(math.pi*t)**.7
  rx=.085+.075*bulge+.105*t;ry=.082+.020*bulge+.046*t
  z=1.66-.25*t-.025*front*math.sin(math.pi*t)+.072*side*front*(.3+.7*t)
  ridge=0
  for center,amp,width in [(.22+.055*math.cos(a+.4),.008,.09),(.52+.070*math.cos(a-.3),.011,.085),(.80+.035*math.sin(a*2),.006,.065)]:
   q=(t-center)/width
   ridge+=amp*math.exp(-q*q*.5)
   # A narrow trough beneath a broad fold gives a folded edge, not an inflated tube.
   ridge-=amp*.45*math.exp(-((t-center-.085)/(width*.36))**2*.5)
  support=max(0,1-abs(math.cos(a))*.85)
  ridge*=front*support*math.sin(math.pi*t)**.45
  x=rx*math.cos(a);y=ry*math.sin(a)-.021-ridge
  # Localized tension at one shoulder, avoiding uniform noise over the whole garment.
  shoulder=math.exp(-((a-3.35)/.32)**2)*math.exp(-((t-.38)/.28)**2)
  y+=.0018*math.sin(t*48+a*3)*shoulder
  cowl.data.vertices[j*N+i].co=(x,y,z)
# A soft ivory thread edge follows the outer hood's free edge; no dark/gold trim.
mat=bpy.data.materials['Fit04 opaque soft white veil'].copy();mat.name='Fit04 hood hem ivory thread'
p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.72,.70,.64,1)
coll=bpy.data.collections['V003 - fitting 04 tailored']
for side in [0,99]:
 points=[hood.data.vertices[j*100+side].co.copy() for j in range(12,100)]
 d=bpy.data.curves.new('Soft rolled hood hem','CURVE');d.dimensions='3D';d.bevel_depth=.00065;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for q,co in zip(sp.points,points):q.co=(co.x,co.y-.0006,co.z,1)
 o=bpy.data.objects.new('Fit04 continuous ivory hood hem',d);coll.objects.link(o);d.materials.append(mat)
s['soft_cloth_pass_01']=True
s['sculpt_stage']='Focused hood and shoulder cloth pass, layered hood retained, clean gloves. Primary drapery remains a work in progress.'
# Match prior camera settings for a meaningful before/after review.
cam=s.camera;cam.location=(1.15,-8,2.42);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.43
s.render.resolution_x=1350;s.render.resolution_y=1800;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rot=cam.rotation_euler.copy()
for name,position,target,scale in [('side',(7,-.4,2.4),(0,0,1.045),2.43),('detail',(1.0,-6,2.15),(0,-.08,1.65),1.22)]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-'+name+'.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;cam.data.ortho_scale=2.43;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-front.png'
print('Focused hood and shoulder pass saved for art review.')

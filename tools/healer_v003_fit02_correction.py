"""Correct fit02 after front/profile review: reduce cowl bulk and form broad skirt folds."""
import bpy,math
s=bpy.context.scene;c=bpy.data.collections['V003 - fitting 02']
cowl=bpy.data.objects['Fit02 continuous diagonal shoulder cowl']
# Rebuild the same surface with flatter shoulders and closer contact to the torso.
N=180;R=65
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  a=i/N*math.pi*2;front=max(0,-math.sin(a));side=math.cos(a);bulge=math.sin(math.pi*t)**.7
  rx=.085+.075*bulge+.105*t;ry=.082+.020*bulge+.046*t
  z=1.66-.25*t-.025*front*math.sin(math.pi*t)+.072*side*front*(.3+.7*t)
  fold=(.0045*math.cos(t*math.pi*6+.7*side)+.0015*math.cos(t*math.pi*10-side))*math.sin(math.pi*t)**.6
  cowl.data.vertices[j*N+i].co=((rx+fold*.6)*math.cos(a),(ry+fold)*math.sin(a)-.021,z)
# Waist-to-hem folds: irregular broad fans, deeper far from the attachment.
skirt=bpy.data.objects['Fit02 diagonal waist and skirt drape'];R=150;N=90
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  u=i/(N-1);a=-math.pi*.95+u*math.pi*.93+.55*t
  # A few main valleys and rounded crests, not uniform accordion pleats.
  fold=0
  for pos,amp,width in [(.15,.020,.075),(.39,.027,.10),(.65,.019,.085),(.87,.015,.065)]:
   center=pos+.06*math.sin(t*1.8+pos*4)
   d=(u-center)/width
   fold+=amp*(1-d*d)*math.exp(-.5*d*d)
  fold*=.18+.82*t
  rad=.177+.16*t
  z=1.37-.28*u-t*(1.13-.20*u)
  # Curving the upper edge downward hides its former bib-like horizontal cut.
  z-=.07*math.sin(u*math.pi)*(1-t)**3
  skirt.data.vertices[j*N+i].co=((rad+fold)*math.cos(a),(rad*.73+fold)*math.sin(a)-.025,z+.006*math.sin(u*9)*t**6)
# Keep the veil opaque but reduce its regular curtain-like ridges.
veil=bpy.data.objects['Fit02 opaque suspended face veil']
for v in veil.data.vertices:
 x,y,z=v.co;mask=max(0,1-abs(z-1.77)/.25)
 v.co.y+=.0015*math.sin(x*54+z*4)*mask
# Save neutral modeling views, not a polished presentation that hides seams.
s['fit02_review']='Corrected inflated cowl and flat overskirt. Arm gestures closer to concept; silhouette and garment construction still provisional.'
s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
from mathutils import Vector
cam=s.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();cam.location=(7,-.4,2.4);cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-side.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting02-front.png'
print('Fit02 reviewed corrections saved.')

"""Sculpt a small set of broad converging folds into the existing overskirt."""
import bpy,math
from mathutils import Vector
s=bpy.context.scene
if s.get('waist_fold_pass_01'):raise RuntimeError('Waist fold pass already applied')
o=bpy.data.objects['Fit04 retained diagonal waist and skirt drape']
b=bpy.data.collections['Fit04 - before soft cloth pass'];copy=o.copy();copy.data=o.data.copy();copy.name=o.name+' prior waist folds';b.objects.link(copy)
for v in o.data.vertices:
 x,y,z=v.co
 if y>=-.025:continue
 t=max(0,min(1,(1.17-z)/1.06));front=min(1,max(0,(-y-.025)/.085));endfade=min(1,t/.12)
 displace=0
 for slope,amplitude,width in [(-.46,.017,.034),(-.27,.023,.040),(-.085,.018,.036),(.105,.013,.032)]:
  line=.105+slope*t+.012*math.sin(t*3+slope*4)*t
  w=.006+width*t
  d=(x-line)/w
  # Broad rounded fold with a narrower trough beside it.
  displace+=amplitude*(.16+.84*t)*math.exp(-.5*d*d)
  displace-=amplitude*.40*(.16+.84*t)*math.exp(-.5*((x-line-w*1.1)/(w*.33))**2)
 v.co.y-=displace*front*endfade
s['waist_fold_pass_01']=True;s['soft_cloth_review']='Rounded hood opening and turned hem retained; shoulder fold crests vary; broad waist-origin overskirt fold study retained. Still below concept quality.'
cam=s.camera;cam.location=(1.15,-8,2.42);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.43
s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rot=cam.rotation_euler.copy()
cam.location=(7,-.4,2.4);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-side.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-soft-cloth-front.png'
print('Waist-origin fold study saved and rendered.')

"""Correct the outer hood/inner veil layering without changing the rest of Fit04."""
import bpy,math
from mathutils import Vector
s=bpy.context.scene
if s.get('hood_layering_corrected'):raise RuntimeError('Hood layering correction already applied')
bpy.ops.wm.save_as_mainfile(filepath='/Users/adu/workspace/monarchy-assets/src/healer-before-hood-layering.blend',copy=True)
hood=bpy.data.objects['Fit04 rounded outer hood'];veil=bpy.data.objects['Fit04 opaque shaped face veil - no facial features']
backup=bpy.data.collections.new('Fit04 - prior hood layering');s.collection.children.link(backup);backup.hide_render=True;backup.hide_viewport=True
for old in [hood,veil]:
 o=old.copy();o.data=old.data.copy();o.name=old.name+' before hood overlap';backup.objects.link(o)
# Bring the hood's front edges forward, leaving the rear volume intact.
# Front-edge width narrows the opening so the outer cloth overlaps the veil's sides.
R=100;N=100
assert len(hood.data.vertices)==R*N
for j in range(R):
 t=j/(R-1);crown=min(1,t/.14);crown=crown*crown*(3-2*crown)
 for i in range(N):
  u=i/(N-1);edge=min(u,1-u);overhang=math.exp(-(edge/.175)**2)
  v=hood.data.vertices[j*N+i]
  v.co.y-=(.077+.025*t)*overhang*crown
  # Turn the free edge very slightly back, giving the cloth a soft folded lip.
  v.co.y+=.0045*math.exp(-(edge/.025)**2)*crown
# Recess and narrow the veil; round the hidden top rather than exposing a straight sheet edge.
for v in veil.data.vertices:
 x,y,z=v.co
 v.co.x*=.86;v.co.y+=.017
 top=max(0,min(1,(z-1.90)/.117))
 v.co.z-=.026*top
# Close the front crown with shared boundary vertices to make a continuous brow.
old=hood.data;verts=[v.co.copy() for v in old.vertices];faces=[tuple(p.vertices) for p in old.polygons];rows=[]
for j in range(31):
 left=verts[j*100+99];right=verts[j*100];indices=[j*100+99]
 for k in range(1,30):
  u=k/30;p=left.lerp(right,u);p.y-=.004*(1-(2*u-1)**2);p.z+=.002*(1-(2*u-1)**2);indices.append(len(verts));verts.append(p)
 indices.append(j*100);rows.append(indices)
for j in range(30):
 for k in range(30):faces.append((rows[j][k],rows[j][k+1],rows[j+1][k+1],rows[j+1][k]))
d=bpy.data.meshes.new('Fit04 continuous over-veil hood with closed brow');d.from_pydata(verts,[],faces);d.update()
for m in old.materials:d.materials.append(m)
for p in d.polygons:p.use_smooth=True
hood.data=d

# Front corners now sit ahead of the veil, including in profile.
s['hood_layering_corrected']=True
s['hood_layering_review']='Outer hood front edges overlap and project forward of recessed inner veil; crown veil edge lowered under hood. Other Fit04 components unchanged.'
cam=s.camera;cam.location=(1.15,-8,2.42);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.43
s.render.resolution_x=1350;s.render.resolution_y=1800;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-hood-over-veil-front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rotation=cam.rotation_euler.copy()
for name,position,target,scale in [('side',(7,-.4,2.4),(0,0,1.045),2.43),('detail',(1.0,-6,2.15),(0,-.08,1.76),.92)]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-hood-over-veil-'+name+'.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rotation;cam.data.ortho_scale=2.43;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-hood-over-veil-front.png'
print('Hood-over-veil correction saved; three inspection views rendered.')

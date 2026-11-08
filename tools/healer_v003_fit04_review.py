"""Retain the useful fit04 changes; quarantine failed cloth experiments."""
import bpy,math
from mathutils import Vector,Matrix
s=bpy.context.scene;coll=bpy.data.collections['V003 - fitting 04 tailored'];previous=bpy.data.collections['V003 - fitting 03 gloved']
rejected=bpy.data.collections.new('Fit04 - rejected drapery trials');s.collection.children.link(rejected);rejected.hide_render=True;rejected.hide_viewport=True
for o in list(coll.objects):
 if any(k in o.name for k in ['bias fall','sewn wrap edge','supported shoulder drape trial']):
  rejected.objects.link(o);coll.objects.unlink(o);o.hide_render=False;o.hide_set(False)
# Restore the reviewed fitting shapes, with completely clean materials.
for old in previous.objects:
 if not any(k in old.name for k in ['diagonal shoulder cowl','diagonal waist and skirt drape','hanging sleeve drape']):continue
 o=old.copy();o.data=old.data.copy();o.name=old.name.replace('Fit03','Fit04 retained');coll.objects.link(o);o.data.materials.clear();o.data.materials.append(bpy.data.materials['Fit04 clean warm ivory cloth'])
 # Existing long drapes must clear the new gown instead of intersecting it.
 if 'waist' in o.name:
  for v in o.data.vertices:
   if v.co.y<0:v.co.y-=.014
# Close the top of the new suspended veil under the white headpiece.
veil=bpy.data.objects['Fit04 opaque shaped face veil - no facial features']
for v in veil.data.vertices:
 factor=max(0,min(1,(v.co.z-1.90)/.095));v.co.z+=.022*factor
# Tailored cuff bridges blend the clean glove wrists into the existing sleeve ends.
for raised in [True,False]:
 pos=Vector((-.175,-.265,1.44)) if raised else Vector((.29,-.245,1.17));rot=Matrix.Rotation(math.radians(-8 if raised else 112),3,'X');mirror=Matrix.Diagonal(Vector((-1 if raised else 1,1 if raised else -1,1)))
 vs=[];fs=[];N=64;R=20
 for j in range(R):
  t=j/(R-1);z=-.073+.027*t;rx=.026*(1-t)+.017*t;ry=.024*(1-t)+.010*t
  for i in range(N):
   a=i/N*2*math.pi;p=Vector((rx*math.cos(a),ry*math.sin(a),z));vs.append(pos+rot@mirror@p)
 for j in range(R-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 d=bpy.data.meshes.new('Fit04 tailored cuff bridge');d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new('Fit04 tailored glove cuff '+('raised' if raised else 'open'),d);coll.objects.link(o);d.materials.append(bpy.data.materials['Fit04 clean warm ivory cloth'])
 for p in d.polygons:p.use_smooth=True
 q=o.modifiers.new('Soft cuff rim','SUBSURF');q.levels=1;q=o.modifiers.new('Cuff fabric thickness','SOLIDIFY');q.thickness=.002
s['sculpt_stage']='Fit04 reviewed: clean articulated gloves, covered figure, hood/veil and shallower headpiece retained. New drapery experiments rejected; prior fitting forms restored.'
s['fit04_review']='Did not achieve a step change in cloth quality. Crossing wrap self-intersections and compressed simulated shoulder panel rejected and hidden. Primary garment forms remain unresolved.'
cam=s.camera;cam.location=(1.15,-8,2.42);cam.rotation_euler=(Vector((0,0,1.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.43
s.render.resolution_x=1350;s.render.resolution_y=1800;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-front.png'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.render.render(write_still=True)
loc=cam.location.copy();rotation=cam.rotation_euler.copy()
for name,position,target,scale in [('side',(7,-.4,2.4),(0,0,1.045),2.43),('rear',(1.5,7,2.4),(0,0,1.045),2.43),('detail',(1.0,-6,2.15),(0,-.1,1.49),1.32)]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-'+name+'.png';bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rotation;cam.data.ortho_scale=2.43;s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-front.png'
print('Reviewed fit04 saved; failed drapes quarantined.')

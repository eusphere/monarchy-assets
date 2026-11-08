"""Replace intersecting ribbon construction with a supported front-panel cloth test."""
import bpy,math
from mathutils import Vector
s=bpy.context.scene;coll=bpy.data.collections['V003 - fitting 04 tailored']
for o in coll.objects:
 if any(key in o.name for key in ['bias fall','sewn wrap edge']):o.hide_render=True;o.hide_set(True)
gown=bpy.data.objects['Fit04 softly fitted covered gown']
support=bpy.data.collections.new('Fit04 cloth fitting collision only');s.collection.children.link(support);support.objects.link(gown)
gown.modifiers.new('Drape fitting collision','COLLISION');gown.collision.thickness_outer=.004
# Front drape is cut with modest ease, and supported only at the shoulder ends.
vs=[];fs=[];R=28;N=75
for j in range(R):
 t=j/(R-1)
 for i in range(N):
  u=i/(N-1);x=.43*(u-.5);z=1.615-.045*u-.245*t
  shape=math.sqrt(max(.015,1-(x/.225)**2))
  y=-.035-.15*shape-.004*math.sin(t*math.pi*4+u*3)
  vs.append((x,y,z))
for j in range(R-1):
 for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
d=bpy.data.meshes.new('Fit04 shoulder panel rest surface');d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new('Fit04 supported shoulder drape trial',d);coll.objects.link(o);d.materials.append(bpy.data.materials['Fit04 clean warm ivory cloth'])
for p in d.polygons:p.use_smooth=True
vg=o.vertex_groups.new(name='Shoulder seam attachments')
for j in range(4):
 for i in list(range(5))+list(range(N-5,N)):vg.add([j*N+i],1-j*.18,'REPLACE')
cl=o.modifiers.new('Supported cloth fitting','CLOTH');cl.settings.quality=6;cl.settings.mass=.20;cl.settings.vertex_group_mass=vg.name;cl.settings.tension_stiffness=35;cl.settings.compression_stiffness=35;cl.settings.shear_stiffness=20;cl.settings.bending_stiffness=1.0
cl.collision_settings.use_collision=True;cl.collision_settings.collection=support;cl.collision_settings.distance_min=.004;cl.collision_settings.use_self_collision=True;cl.collision_settings.self_distance_min=.003
cl.point_cache.frame_start=1;cl.point_cache.frame_end=30
# Freeze viewport inspection on the lightweight panel during the fitting.
for f in range(1,31):s.frame_set(f)
fit=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));o.data=fit;o.modifiers.remove(cl)
for p in fit.polygons:p.use_smooth=True
q=o.modifiers.new('Soft cloth surface','SUBSURF');q.levels=2;q=o.modifiers.new('Physical fabric thickness','SOLIDIFY');q.thickness=.003
s.frame_set(1)
s.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/v003-fitting04-drape-trial.png';bpy.ops.render.render(write_still=True)
print('Shoulder drape trial rendered; not saved as accepted result yet.')

"""Add a slim revision of Vesper; preserve and hide the earlier studies."""
import bpy, math
from mathutils import Vector
name='C2 - Veiled Vesper'
if bpy.data.collections.get(name): raise RuntimeError('C2 already exists; refusing to duplicate')
# Reuse the blockout mesh helpers without running the original lineup builder.
p='/Users/adu/workspace/monarchy-assets/tools/healer_silhouettes.py'
s=open(p).read();s=s[s.index('def material'):s.index('for index,(name,offset)')]
exec(compile(s,p,'exec'))
for c in bpy.context.scene.collection.children:
    if c.name.startswith(('A -','B -','C -')): c.hide_render=True;c.hide_viewport=True
coll=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(coll);offset=0
white=material('C2 warm white silk',(.79,.76,.67))
trim=material('C2 antique gold',(.25,.16,.065),.65)
cloth('C2 slender pleated gown',[(.025,.32,.24,.015),(.12,.31,.23,0),(.5,.255,.20,0),(.9,.21,.155,0),(1.14,.155,.13,0),(1.36,.205,.15,0),(1.57,.235,.15,0),(1.64,.16,.12,0)],white,14,.017)
cloth('C2 enclosing hood',[(1.42,.23,.16,.055),(1.65,.22,.18,.035),(1.9,.17,.16,.025),(2.02,.10,.115,.035),(2.065,.001,.001,.04)],white,12,.008)
# Featureless opaque textile face covering, gently bowed and pleated.
vs=[];fs=[];n=24;rows=20
for j in range(rows):
    t=j/(rows-1);z=1.91-.52*t;w=.125+.035*t
    for i in range(n):
        u=i/(n-1)*2-1
        y=-.168-.035*(1-u*u)+.006*math.cos(u*math.pi*6)+.025*t
        vs.append((u*w,y,z+.008*math.sin(u*5)*t))
for j in range(rows-1):
    for i in range(n-1):
        a=j*n+i;fs.append((a,a+1,a+1+n,a+n))
ob=mesh('C2 opaque white face veil',vs,fs,white);ob.modifiers.new('Veil thickness','SOLIDIFY').thickness=.004
# Narrow side falls replace the bulbous shoulder panels.
for side in [-1,1]:
    ribbon('C2 long outer veil',[(side*.105,.035,2.025),(side*.195,.07,1.83),(side*.245,.11,1.53),(side*.26,.13,.95),(side*.32,.15,.09)],[.055,.075,.09,.095,.11],white)
    ribbon('C2 narrow hanging sleeve',[(side*.215,-.005,1.58),(side*.28,-.035,1.42),(side*.32,-.10,1.16),(side*.28,-.07,.81)],[.07,.075,.085,.10],white)
    # Restrained crescent crest follows the hood, rather than spanning shoulders.
crown('C2 slender crescent diadem',[(-.28,2.12),(-.20,1.99),(-.10,1.97),(.10,1.97),(.20,1.99),(.28,2.12),(.19,2.06),(.09,2.035),(-.09,2.035),(-.19,2.06)],trim,y=-.035)
ellipsoid('C2 central diadem ornament',(0,-.093,2.02),(.025,.018,.035),trim)
# A single diagonal drape gives shape without adding width.
ribbon('C2 diagonal torso drape',[(-.17,-.17,1.58),(-.09,-.19,1.44),(.05,-.18,1.24),(.12,-.18,1.08),(.04,-.23,.73),(-.11,-.27,.28)],[.075,.085,.095,.09,.105,.13],white)
# Close, asymmetrical healing gestures. Hands remain blockout forms.
for side,z in [(-1,1.30),(1,1.11)]:
    ribbon('C2 bent sleeve',[(side*.23,-.01,1.49),(side*.29,-.12,1.29),(side*.20,-.25,z)],[.065,.08,.07],white)
    hand=ellipsoid('C2 unarmed hand',(side*.15,-.30,z+.025),(.042,.075,.035),ivory);hand.rotation_euler.y=side*.5
scene=bpy.context.scene;cam=scene.camera
cam.location=(3,-9,3.1);cam.rotation_euler=(Vector((0,0,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.7
scene.render.resolution_x=1000;scene.render.resolution_y=1200
scene.render.image_settings.file_format='PNG';scene.render.filepath='/Users/adu/workspace/monarchy-assets/ideas/healer/previews/vesper-v002.png'
# Lower key-light power retains readable folds in the white fabric.
for ob in scene.objects:
    if ob.type=='LIGHT': ob.data.energy*=.65
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.render.render(write_still=True)
print('Saved C2 and preview')

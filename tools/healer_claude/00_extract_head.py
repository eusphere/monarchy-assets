"""One-off: cut the head and neck out of Blender Studio's Human Base Meshes bundle.

  blender -b --disable-autoexec --factory-startup --python 00_extract_head.py -- <human_base_meshes_bundle.blend>

Source: Human Base Meshes bundle v1.4.1 (blender.org asset bundles; fetched from the
mirrors.dotsrc.org copy), object `GEO-body_female_realistic`. The bundle's README states
all its assets are public domain under CC0. Only the head and neck are kept, at the
bundle's own scale and position, in src/healer-head-base.blend, so the build does not
need the 49 MB bundle."""
import os
import sys

import bmesh
import bpy

bundle = sys.argv[sys.argv.index('--') + 1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(bundle) as (src, dst):
    dst.objects = ['GEO-body_female_realistic']
body = dst.objects[0]
sc = bpy.context.scene
sc.collection.objects.link(body)
for m in body.modifiers:
    if m.type == 'MULTIRES':
        m.levels = 2                         # enough to carry the lips, nose and ears
dg = bpy.context.evaluated_depsgraph_get()
ev = body.evaluated_get(dg)
me = bpy.data.meshes.new_from_object(ev)
bm = bmesh.new()
bm.from_mesh(me)
top = max(v.co.z for v in bm.verts)
CUT = top - 0.268                            # the root of the neck, above the slope of the shoulders
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < CUT or abs(v.co.x) > 0.11], context='VERTS')
out = bpy.data.meshes.new('Head base')
bm.to_mesh(out)
bm.free()
out.polygons.foreach_set('use_smooth', [True] * len(out.polygons))
ob = bpy.data.objects.new('Head base', out)
ob['source'] = 'Blender Studio Human Base Meshes bundle v1.4.1, GEO-body_female_realistic, CC0'
ob['top_z'] = top
sc.collection.objects.link(ob)
bpy.data.objects.remove(body)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
    for d in list(block):
        if d.users == 0:
            block.remove(d)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'src', 'healer-head-base.blend'))
print('head base:', len(out.vertices), 'verts', len(out.polygons), 'faces')

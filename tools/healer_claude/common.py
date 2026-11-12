"""Shared helpers for the healer-claude build stages.

Run each stage headless, in order:
    Blender -b --python tools/healer_claude/01_base.py
    Blender -b src/healer-claude.blend --python tools/healer_claude/02_skirt.py
    ...
Scene convention: metres, floor at z=0, the figure faces -Y.
"""
import math
import os

import bmesh
import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLEND = os.path.join(ROOT, 'src', 'healer-claude.blend')
SOURCE = os.path.join(ROOT, 'src', 'healer.blend')
RENDERS = os.path.join(ROOT, 'ideas', 'healer', 'renders', 'claude')


def collection(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def remove(name):
    o = bpy.data.objects.get(name)
    if o:
        me = o.data
        bpy.data.objects.remove(o)
        if me and me.users == 0 and isinstance(me, bpy.types.Mesh):
            bpy.data.meshes.remove(me)


def new_object(name, verts, faces, coll, uvs=None, smooth=True):
    remove(name)
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if uvs is not None:
        layer = me.uv_layers.new(name='UVMap')
        loop_vert = np.empty(len(me.loops), dtype=np.int64)
        me.loops.foreach_get('vertex_index', loop_vert)
        layer.data.foreach_set('uv', np.asarray(uvs, dtype=np.float64)[loop_vert].ravel())
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    ob = bpy.data.objects.new(name, me)
    collection(coll).objects.link(ob)
    return ob


def face_out(ob):
    """Make normals consistent and outward. The cloth solver pushes along collider normals,
    so an inside-out collider drags cloth into itself."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def grid_faces(rows, cols, closed):
    """Quads for a rows x cols vertex grid; `closed` wraps the columns."""
    faces = []
    span = cols if closed else cols - 1
    for r in range(rows - 1):
        for c in range(span):
            a = r * cols + c
            b = r * cols + (c + 1) % cols
            faces.append((a, b, b + cols, a + cols))
    return faces


def coords(ob):
    co = np.empty(3 * len(ob.data.vertices))
    ob.data.vertices.foreach_get('co', co)
    return co.reshape(-1, 3)


def set_coords(ob, co):
    ob.data.vertices.foreach_set('co', np.asarray(co, dtype=np.float64).ravel())
    ob.data.update()


def activate(ob):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def add_collision(ob, thickness=0.004, friction=8.0):
    m = ob.modifiers.get('Collision') or ob.modifiers.new('Collision', 'COLLISION')
    ob.collision.thickness_outer = thickness
    ob.collision.thickness_inner = 0.01
    ob.collision.cloth_friction = friction
    return m


def collider_proxy(source_name, ratio, thickness=0.004):
    """A decimated, render-hidden stand-in so cloth does not collide with dense meshes."""
    name = 'Collider - ' + source_name
    remove(name)
    src = bpy.data.objects[source_name]
    ob = bpy.data.objects.new(name, src.data.copy())
    collection('Sim').objects.link(ob)
    ob.matrix_world = src.matrix_world.copy()
    dec = ob.modifiers.new('Decimate', 'DECIMATE')
    dec.ratio = ratio
    activate(ob)
    bpy.ops.object.modifier_apply(modifier=dec.name)
    ob.hide_render = True
    ob.display_type = 'WIRE'
    add_collision(ob, thickness)
    return ob


def collide_before_subsurf(ob, thickness=0.004):
    """Collide with the unsubdivided cage of a finished garment."""
    add_collision(ob, thickness)
    i = [m.type for m in ob.modifiers].index('COLLISION')
    ob.modifiers.move(i, 0)


def simulate(ob, frames, on_frame=None, max_frame_seconds=45):
    """Step the scene so the cloth on `ob` solves, then freeze the result."""
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = frames
    for m in ob.modifiers:
        if m.type == 'CLOTH':
            m.point_cache.frame_start = 1
            m.point_cache.frame_end = frames
    import time
    start = last = time.time()
    for f in range(1, frames + 1):
        if on_frame:
            on_frame(f)
        sc.frame_set(f)
        bpy.context.view_layer.update()
        now = time.time()
        took, last = now - last, now
        if f % 10 == 0:
            print('  frame', f, '%.0fs elapsed, %.1fs this frame' % (now - start, took), flush=True)
        # A frame this slow means the solver is thrashing; keep what we have.
        if took > max_frame_seconds:
            print('  stopping early at frame', f, 'after a %.0fs frame' % took, flush=True)
            break
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    co = np.empty(3 * len(ev.data.vertices))
    ev.data.vertices.foreach_get('co', co)
    for m in list(ob.modifiers):
        if m.type == 'CLOTH':
            ob.modifiers.remove(m)
    set_coords(ob, co.reshape(-1, 3))
    sc.frame_set(1)


def render(name, angle=0.0, dist=7.2, target_z=1.12, lens=85, res=(700, 1370), samples=48):
    sc = bpy.context.scene
    cam = bpy.data.objects['Hero camera']
    if abs(angle) > 100:
        lens, dist = lens * 4.4 / dist, 4.4   # stay in front of the backdrop wall
    a = math.radians(angle)
    cam.location = (math.sin(a) * dist, -math.cos(a) * dist, target_z)
    cam.rotation_euler = (math.radians(90), 0, a)
    cam.data.lens = lens
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.eevee.taa_render_samples = samples
    os.makedirs(RENDERS, exist_ok=True)
    sc.render.filepath = os.path.join(RENDERS, name + '.png')
    bpy.ops.render.render(write_still=True)


def save():
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

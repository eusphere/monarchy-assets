"""Stage 6: materials and reflections.

* `TeamAccent` - worn metal in the team colour. One RGB node ("Team colour")
  carries the hue the client supplies; everything else (patina in the
  recesses, uneven polish, hammer marks, hairline scratches) is layered on
  top of it, so any team colour gets the same depth and wear.
* `Voile` / `Voile sheer` - warm parchment cloth with a fine vertical grain;
  the sheer one lets the layers underneath show through face-on.
* World - near black to the camera, but a soft studio to reflections, so the
  metal has something to mirror."""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401


class Graph:
    def __init__(self, tree):
        self.t = tree
        self.x = 0

    def node(self, kind, label=None, **props):
        n = self.t.nodes.new(kind)
        n.location = (self.x, -220 * (len(self.t.nodes) % 6))
        self.x += 60
        if label:
            n.label = n.name = label
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.t.links.new(a, b)

    def val(self, v):
        if isinstance(v, (int, float)):
            n = self.node('ShaderNodeValue')
            n.outputs[0].default_value = v
            return n.outputs[0]
        return v

    def math(self, op, a, b=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def mix(self, fac, a, b, kind='MIX'):
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=kind)
        for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            elif isinstance(v, tuple):
                sock.default_value = v
            else:
                self.link(v, sock)
        return n.outputs[2]

    def ramp(self, fac, lo, hi):
        n = self.node('ShaderNodeMapRange', clamp=True, interpolation_type='SMOOTHSTEP')
        self.link(fac, n.inputs[0])
        n.inputs[1].default_value = lo
        n.inputs[2].default_value = hi
        return n.outputs[0]

    def noise(self, vec, scale, detail=4.0, rough=0.55, stretch=None):
        if stretch:
            m = self.node('ShaderNodeMapping')
            m.inputs['Scale'].default_value = stretch
            self.link(vec, m.inputs['Vector'])
            vec = m.outputs[0]
        n = self.node('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        self.link(vec, n.inputs['Vector'])
        return n.outputs['Fac']


def fresh(mat):
    mat.use_nodes = True
    t = mat.node_tree
    t.nodes.clear()
    g = Graph(t)
    out = g.node('ShaderNodeOutputMaterial')
    bsdf = g.node('ShaderNodeBsdfPrincipled')
    return g, out, bsdf


# ------------------------------------------------------------------ worn team metal
acc = bpy.data.materials['TeamAccent']
acc['colorRole'] = 'teamAccent'
g, out, bsdf = fresh(acc)
g.link(bsdf.outputs[0], out.inputs['Surface'])
team = g.node('ShaderNodeRGB', 'Team colour')
team.outputs[0].default_value = (0.80, 0.45, 0.11, 1)          # default: deep gold
tc = g.node('ShaderNodeTexCoord')
obj = tc.outputs['Object']

# Recesses: ambient occlusion finds the creases between links and plaques.
ao = g.node('ShaderNodeAmbientOcclusion', samples=16)
ao.inputs['Distance'].default_value = 0.018
cavity = g.ramp(ao.outputs['AO'], 0.97, 0.55)                   # 1 deep in a recess
# Uneven handling: broad patches that have been rubbed bright or left dull.
patch = g.ramp(g.noise(obj, 22, 5, 0.6), 0.38, 0.68)
fine = g.noise(obj, 260, 3, 0.7)
# Tarnish gathers in recesses and, thinly, in the dull patches.
grime = g.math('MAXIMUM', cavity, g.math('MULTIPLY', g.math('SUBTRACT', 1.0, patch), 0.55))
grime = g.math('MULTIPLY', grime, g.math('ADD', 0.75, g.math('MULTIPLY', fine, 0.5)), clamp=True)

deep = g.mix(1.0, team.outputs[0], (0.22, 0.13, 0.08, 1), 'MULTIPLY')     # the hue, browned and darkened
bright = g.mix(0.06, team.outputs[0], (1.0, 0.93, 0.80, 1), 'MIX')        # polished high points run paler
base = g.mix(patch, team.outputs[0], bright)
base = g.mix(grime, base, deep)
g.link(base, bsdf.inputs['Base Color'])
g.link(g.math('SUBTRACT', 1.0, g.math('MULTIPLY', grime, 0.45)), bsdf.inputs['Metallic'])
rough = g.math('ADD', 0.24, g.math('MULTIPLY', g.math('SUBTRACT', 1.0, patch), 0.22))
rough = g.math('ADD', rough, g.math('MULTIPLY', grime, 0.38))
rough = g.math('ADD', rough, g.math('MULTIPLY', g.math('SUBTRACT', fine, 0.5), 0.10), clamp=True)
g.link(rough, bsdf.inputs['Roughness'])

# Surface: soft hammer facets, then hairline scratches running mostly one way.
vor = g.node('ShaderNodeTexVoronoi', feature='SMOOTH_F1')
vor.inputs['Scale'].default_value = 85
vor.inputs['Smoothness'].default_value = 0.7
g.link(obj, vor.inputs['Vector'])
b1 = g.node('ShaderNodeBump')
b1.inputs['Strength'].default_value = 0.22
b1.inputs['Distance'].default_value = 0.004
g.link(vor.outputs['Distance'], b1.inputs['Height'])
scratch = g.ramp(g.noise(obj, 90, 2, 0.8, stretch=(1.0, 18.0, 9.0)), 0.62, 0.70)
b2 = g.node('ShaderNodeBump')
b2.inputs['Strength'].default_value = 0.12
b2.inputs['Distance'].default_value = 0.001
g.link(scratch, b2.inputs['Height'])
g.link(b1.outputs[0], b2.inputs['Normal'])
g.link(b2.outputs[0], bsdf.inputs['Normal'])
bsdf.inputs['Coat Weight'].default_value = 0.0
bsdf.inputs['Specular IOR Level'].default_value = 0.5

# ------------------------------------------------------------------ voile


def voile(name, sheer):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    g, out, bsdf = fresh(mat)
    tc = g.node('ShaderNodeTexCoord')
    obj = tc.outputs['Object']
    # Fine vertical grain, with a slower slub so it is not mechanical.
    grain = g.noise(obj, 1.0, 2, 0.5, stretch=(520.0, 520.0, 14.0))
    slub = g.noise(obj, 1.0, 3, 0.6, stretch=(60.0, 60.0, 3.0))
    # A mid-tone parchment, not white: white cloth burns out and hides its own folds.
    tone = g.mix(g.math('MULTIPLY', slub, 0.55), (0.58, 0.47, 0.33, 1), (0.42, 0.33, 0.23, 1))
    tone = g.mix(g.math('MULTIPLY', grain, 0.25), tone, (0.70, 0.60, 0.46, 1))
    # Depth: the insides of folds and the places where cloth lies on cloth go darker and warmer.
    occ = g.node('ShaderNodeAmbientOcclusion', samples=8)
    occ.inputs['Distance'].default_value = 0.07
    shade = g.ramp(occ.outputs['AO'], 0.30, 0.95)
    tone = g.mix(shade, g.mix(1.0, tone, (0.34, 0.24, 0.17, 1), 'MULTIPLY'), tone)
    g.link(tone, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Sheen Weight'].default_value = 0.6
    bsdf.inputs['Sheen Roughness'].default_value = 0.45
    bsdf.inputs['Sheen Tint'].default_value = (1.0, 0.94, 0.84, 1)
    bump = g.node('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.38
    bump.inputs['Distance'].default_value = 0.0006
    g.link(g.math('ADD', grain, g.math('MULTIPLY', slub, 0.6)), bump.inputs['Height'])
    g.link(bump.outputs[0], bsdf.inputs['Normal'])
    if sheer:
        # Gauze: see-through face-on, solid where it turns away or folds back on itself.
        lw = g.node('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.35
        opacity = g.math('ADD', 0.50, g.math('MULTIPLY', lw.outputs['Facing'], 0.50), clamp=True)
        opacity = g.math('ADD', opacity, g.math('MULTIPLY', g.math('SUBTRACT', grain, 0.5), 0.25), clamp=True)
        tr = g.node('ShaderNodeBsdfTransparent')
        mx = g.node('ShaderNodeMixShader')
        g.link(opacity, mx.inputs[0])
        g.link(tr.outputs[0], mx.inputs[1])
        g.link(bsdf.outputs[0], mx.inputs[2])
        g.link(mx.outputs[0], out.inputs['Surface'])
        mat.surface_render_method = 'DITHERED'
        mat.use_backface_culling = False
    else:
        g.link(bsdf.outputs[0], out.inputs['Surface'])
    return mat


voile('Voile', False)
sheer = voile('Voile sheer', True)
veil = bpy.data.objects['Head veil']
veil.data.materials.clear()
veil.data.materials.append(sheer)
lining = bpy.data.materials['Body lining ivory']
lining.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.72, 0.63, 0.50, 1)

# ------------------------------------------------------------------ world and studio
sc = bpy.context.scene
w = sc.world
w.use_nodes = True
w.node_tree.nodes.clear()
g = Graph(w.node_tree)
wout = g.node('ShaderNodeOutputWorld')
bg_cam = g.node('ShaderNodeBackground')
bg_cam.inputs['Color'].default_value = (0.030, 0.018, 0.012, 1)
bg_ref = g.node('ShaderNodeBackground')
tc = g.node('ShaderNodeTexCoord')
sep = g.node('ShaderNodeSeparateXYZ')
g.link(tc.outputs['Generated'], sep.inputs[0])
x, y, z = sep.outputs
# A broad overhead soft box, a tall strip to the camera's left, a cooler one to the right.
over = g.ramp(z, 0.45, 0.95)
left = g.math('MULTIPLY', g.ramp(g.math('MULTIPLY', x, -1.0), 0.55, 0.85), g.ramp(g.math('ABSOLUTE', z), 0.55, 0.15))
right = g.math('MULTIPLY', g.ramp(x, 0.70, 0.92), g.ramp(g.math('ABSOLUTE', z), 0.45, 0.10))
col = g.mix(over, (0.035, 0.028, 0.024, 1), (1.0, 0.93, 0.84, 1))
col = g.mix(left, col, (1.0, 0.90, 0.78, 1), 'ADD')
col = g.mix(g.math('MULTIPLY', right, 0.5), col, (0.75, 0.84, 1.0, 1), 'ADD')
g.link(col, bg_ref.inputs['Color'])
bg_ref.inputs['Strength'].default_value = 0.22
lp = g.node('ShaderNodeLightPath')
mx = g.node('ShaderNodeMixShader')
g.link(lp.outputs['Is Camera Ray'], mx.inputs[0])
g.link(bg_ref.outputs[0], mx.inputs[1])
g.link(bg_cam.outputs[0], mx.inputs[2])
g.link(mx.outputs[0], wout.inputs['Surface'])
sc.eevee.use_raytracing = True
sc.eevee.ray_tracing_options.resolution_scale = '1'
sc.eevee.use_gtao = True if hasattr(sc.eevee, 'use_gtao') else None
bpy.data.materials['Studio backdrop'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.060, 0.032, 0.020, 1)
# One smaller, harder key raking across the figure from her right; very little fill. Depth in
# cloth comes from shadow, and a big soft light with a strong fill erases it.
from mathutils import Vector


def relight(name, loc, target, energy, size, color):
    o = bpy.data.objects[name]
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    o.data.energy, o.data.size, o.data.color = energy, size, color


relight('Key', (-3.9, -2.9, 4.3), (0, 0, 1.25), 2100, 1.7, (1.0, 0.93, 0.84))
relight('Fill', (3.6, -3.4, 1.4), (0, 0, 1.0), 38, 5.0, (0.86, 0.90, 1.0))
relight('Rim', (2.4, 3.4, 4.0), (0, 0, 1.5), 950, 2.0, (1.0, 0.90, 0.78))
if hasattr(sc.eevee, 'fast_gi_method'):                  # Eevee's screen-space occlusion, for the previews
    sc.eevee.fast_gi_method = 'GLOBAL_ILLUMINATION'
    sc.eevee.fast_gi_distance = 0.35
for o in bpy.data.objects:
    if o.type == 'LIGHT' and hasattr(o.data, 'use_shadow_jitter'):
        o.data.use_shadow_jitter = True

save()
render('stage6-front', 0)
render('stage6-three-quarter', 28)
render('stage6-rear', 180)
render('stage6-portrait', 18, dist=2.6, target_z=1.95, lens=85, res=(900, 1125), samples=64)
render('stage6-jewelry', -20, dist=1.5, target_z=1.84, lens=85, res=(1000, 800), samples=64)
print('stage 6 done')

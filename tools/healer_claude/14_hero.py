"""Stage 14: hero stills, path traced (does not change the model).

The stage renders use Eevee because they are quick. These use Cycles, which
traces real shadow and bounce light, so folds have depth and the sheer veil
layers properly. Slower: a few minutes for the set."""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

sc = bpy.context.scene
rig = bpy.data.objects['Healer Rig']
rig.data.pose_position = 'REST'                    # the blessing gesture, as in the concept
sc.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:                             # fall back to the CPU quietly
    print('GPU not available:', e)
SAMPLES = int(os.environ.get('HEALER_HERO_SAMPLES', '160'))
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8
sc.cycles.transparent_max_bounces = 24             # many layers of gauze
sc.cycles.diffuse_bounces = 3
sc.view_settings.exposure = float(os.environ.get('HEALER_HERO_EXPOSURE', '0.0'))


def hero(name, angle, **kw):
    real = bpy.ops.render.render
    render(name, angle, samples=SAMPLES, **kw)


WANT = os.environ.get('HEALER_HERO', 'front,three-quarter,rear,portrait').split(',')
VIEWS = {'front': (0, {}), 'three-quarter': (28, {}), 'rear': (180, {}), 'side': (90, {}),
         'portrait': (16, dict(dist=2.6, target_z=1.92, lens=85, res=(900, 1125)))}
for v in WANT:
    a, kw = VIEWS[v]
    hero('hero-' + v, a, **kw)
    print('hero', v, flush=True)
print('stage 14 done')

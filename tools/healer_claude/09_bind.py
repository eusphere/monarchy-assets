"""Stage 9: bind the garments to the rig and render animation test frames.

The body form gets automatic weights from the deforming body bones. Garments
take theirs from it where they lie on the body, and from the rig's cloth
helpers elsewhere: `Skirt` and `Hem.L/R` for the skirt (the hem bones stay on
the ground), `SleeveFall.L/R` for the veil hanging off the arms. Weights are
then smoothed across each garment so the regions blend."""
import os
import sys

import bpy
import numpy as np
from mathutils.kdtree import KDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
rig.data.pose_position = 'REST'
sc = bpy.context.scene
HELPERS = ('Skirt', 'Hem.R', 'Hem.L', 'SleeveFall.R', 'SleeveFall.L', 'Chain.Sag', 'ChainAnchor.R', 'ChainAnchor.L')
bones = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in rig.data.bones}


def sstep(a, b, x):
    t = np.clip((np.asarray(x, dtype=float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def clear_skin(ob):
    for m in list(ob.modifiers):
        if m.type == 'ARMATURE':
            ob.modifiers.remove(m)
    for g in list(ob.vertex_groups):
        ob.vertex_groups.remove(g)


def add_armature(ob):
    m = ob.modifiers.new('Healer skin', 'ARMATURE')
    m.object = rig
    while ob.modifiers[0] != m:
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
    ob.parent = rig


def write_weights(ob, weights):
    """weights: {bone: array per vertex}. Normalised, small values dropped."""
    names = list(weights)
    W = np.stack([np.clip(weights[n], 0, None) for n in names], 1)
    W[W < 0.01] = 0
    tot = W.sum(1)
    assert (tot > 0).all(), ob.name + ' has unweighted vertices'
    W /= tot[:, None]
    for j, n in enumerate(names):
        idx = np.where(W[:, j] > 0)[0]
        if len(idx) == 0:
            continue
        g = ob.vertex_groups.new(name=n)
        for i in idx:
            g.add([int(i)], float(W[i, j]), 'REPLACE')


def smooth(ob, weights, rounds):
    e = np.empty(2 * len(ob.data.edges), dtype=np.int64)
    ob.data.edges.foreach_get('vertices', e)
    e = e.reshape(-1, 2)
    n = len(ob.data.vertices)
    deg = np.bincount(e.ravel(), minlength=n).astype(float)
    out = {}
    for name, w in weights.items():
        w = w.astype(float).copy()
        for _ in range(rounds):
            acc = np.zeros(n)
            np.add.at(acc, e[:, 0], w[e[:, 1]])
            np.add.at(acc, e[:, 1], w[e[:, 0]])
            w = 0.5 * w + 0.5 * acc / np.maximum(deg, 1)
        out[name] = w
    return out


# ------------------------------------------------------------------ body
body = bpy.data.objects['Body form']
clear_skin(body)
for n in HELPERS:
    rig.data.bones[n].use_deform = False
for b in rig.data.bones:                       # fingers belong to the gloves, not the body form
    if '.0' in b.name:
        b.use_deform = False
was = (body.hide_viewport, rig.hide_viewport)
body.hide_viewport = rig.hide_viewport = False
body.hide_set(False)
rig.hide_set(False)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
for b in rig.data.bones:
    if b.name != 'Root':
        b.use_deform = True
body.hide_viewport, rig.hide_viewport = was
nb = len(body.data.vertices)
BW = {g.name: np.zeros(nb) for g in body.vertex_groups}
for v in body.data.vertices:
    for ge in v.groups:
        BW[body.vertex_groups[ge.group].name][v.index] = ge.weight
tot = sum(BW.values())
print('body auto weights: groups', len(BW), 'unweighted verts', int((tot < 1e-4).sum()), flush=True)
if (tot < 1e-4).any():
    # Bone heat left gaps (it can on overlapping shells): fill them from the nearest bone.
    bc = coords(body)
    names = [n for n in bones if n not in HELPERS and '.0' not in n and n != 'Root']
    for i in np.where(tot < 1e-4)[0]:
        best, bd = None, 1e9
        for n in names:
            h, t = bones[n]
            ab = t - h
            u = np.clip(np.dot(bc[i] - h, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
            d = np.linalg.norm(bc[i] - (h + ab * u))
            if d < bd:
                best, bd = n, d
        BW.setdefault(best, np.zeros(nb))[i] = 1.0
    clear_skin(body)
    write_weights(body, BW)
    add_armature(body)
bco = coords(body)
tree = KDTree(nb)
for i, p in enumerate(bco):
    tree.insert(p, i)
tree.balance()


def from_body(co, k=4):
    """Body weights carried to arbitrary points, with each point's distance to the body."""
    out = {n: np.zeros(len(co)) for n in BW}
    dist = np.zeros(len(co))
    for i, p in enumerate(co):
        near = tree.find_n(p, k)
        dist[i] = near[0][2]
        ws = np.array([1.0 / max(d, 1e-4) ** 2 for _, _, d in near])
        ws /= ws.sum()
        for (_, j, _), w in zip(near, ws):
            for n in BW:
                if BW[n][j] > 0:
                    out[n][i] += w * BW[n][j]
    return out, dist


def bind(name, weights, rounds=0):
    ob = bpy.data.objects[name]
    clear_skin(ob)
    if rounds:
        weights = smooth(ob, weights, rounds)
    write_weights(ob, weights)
    add_armature(ob)
    print('bound', name, len(ob.vertex_groups), 'groups', flush=True)


# ------------------------------------------------------------------ close garments
for name in ('Fitted bodice', 'Shoulder wrap', 'Neck cowl'):
    w, _ = from_body(coords(bpy.data.objects[name]))
    bind(name, w, rounds=4)

# ------------------------------------------------------------------ head wrap
hw = coords(bpy.data.objects['Head wrap'])
nz0, nz1 = bones['Neck'][0][2], bones['Neck'][1][2]
h = sstep(nz0 + 0.02, nz1 + 0.03, hw[:, 2])
c = 1 - sstep(nz0 - 0.03, nz0 + 0.03, hw[:, 2])
bind('Head wrap', {'Head': h, 'Chest': c, 'Neck': np.clip(1 - h - c, 0, 1)})

# ------------------------------------------------------------------ skirt
sk = coords(bpy.data.objects['Underdress skirt'])
z = sk[:, 2]
pel = sstep(0.95, 1.22, z)
hem = 1 - sstep(0.10, 0.42, z)
mid = np.clip(1 - pel - hem, 0, 1)
left = sstep(-0.06, 0.06, sk[:, 0] - 0.02)
# The front of the skirt rides on the legs, so a step shows as a knee pressing the cloth forward.
legs, _ = from_body(sk, k=6)
LEG = ('Thigh.L', 'Shin.L', 'Thigh.R', 'Shin.R')
leg_tot = sum(legs.get(n, 0) for n in LEG)
front = sstep(0.04, -0.07, sk[:, 1])
ride = 0.70 * front * mid * (leg_tot > 1e-6)
W = {'Pelvis': pel, 'Skirt': mid - ride, 'Hem.L': hem * left, 'Hem.R': hem * (1 - left)}
for n in LEG:
    W[n] = ride * legs.get(n, 0) / np.maximum(leg_tot, 1e-6)
bind('Underdress skirt', W, rounds=10)

# ------------------------------------------------------------------ veil
vo = bpy.data.objects['Head veil']
vc = coords(vo)
z = vc[:, 2]
# The veil hangs down her back, clear of the arms, so it follows the spine by height alone.
head = sstep(nz1 - 0.04, nz1 + 0.05, z)
rest = 1 - head
W = {'Head': head,
     'Chest': rest * sstep(1.50, 1.65, z),
     'Spine': rest * (sstep(1.30, 1.45, z) - sstep(1.50, 1.65, z)),
     'Pelvis': rest * (sstep(1.00, 1.20, z) - sstep(1.30, 1.45, z)),
     'Skirt': rest * (1 - sstep(1.00, 1.20, z))}
bind('Head veil', W, rounds=10)

# ------------------------------------------------------------------ chain
# Each link stays rigid and takes one blend of wrist and sag, graded along the chain, so the
# line eases from the hands into the hanging middle instead of breaking where the weights change.
import bmesh
ch = bpy.data.objects['Healer - cuff to cuff plaque chain']
cc = coords(ch)
bm = bmesh.new()
bm.from_mesh(ch.data)
bm.verts.ensure_lookup_table()
seen = np.zeros(len(bm.verts), bool)
isls = []
for v in bm.verts:
    if seen[v.index]:
        continue
    stack, isl = [v], []
    seen[v.index] = True
    while stack:
        a = stack.pop()
        isl.append(a.index)
        for e in a.link_edges:
            b = e.other_vert(a)
            if not seen[b.index]:
                seen[b.index] = True
                stack.append(b)
    isls.append(np.array(isl))
bm.free()
cent = np.array([cc[i].mean(axis=0) for i in isls])
wr = bones['ChainAnchor.R'][0]
phi = np.arctan2(-cent[:, 0], -cent[:, 1]) % (2 * np.pi)
phi0 = np.arctan2(-wr[0], -wr[1]) % (2 * np.pi)
order = np.argsort((phi - phi0 + 0.3) % (2 * np.pi))
wR, wL, wS = np.zeros(len(cc)), np.zeros(len(cc)), np.zeros(len(cc))
for rank, oi in enumerate(order):
    u = rank / max(len(order) - 1, 1)
    r = float(1 - sstep(0.0, 0.42, u))
    l = float(sstep(0.58, 1.0, u))
    wR[isls[oi]], wL[isls[oi]], wS[isls[oi]] = r, l, max(1 - r - l, 0)
bind(ch.name, {'ChainAnchor.R': wR, 'ChainAnchor.L': wL, 'Chain.Sag': wS})

# ------------------------------------------------------------------ test frames
rig.data.pose_position = 'POSE'
save()
if not rig.animation_data:
    rig.animation_data_create()
SHOTS = {'Healer | Idle': (1, 37), 'Healer | Heal': (1, 17, 33, 49), 'Healer | Walk': (1, 9, 17, 25)}
for action, frames in SHOTS.items():
    rig.animation_data.action = bpy.data.actions[action]
    tag = action.split('| ')[1].lower()
    for f in frames:
        sc.frame_set(f)
        render('anim/anim-%s-f%02d' % (tag, f), 22, res=(520, 1020), samples=24)
        if tag != 'idle' and f == frames[1]:
            render('anim/anim-%s-f%02d-side' % (tag, f), 90, res=(520, 1020), samples=24)
            render('anim/anim-%s-f%02d-rear' % (tag, f), 160, res=(520, 1020), samples=24)
rig.animation_data.action = bpy.data.actions['Healer | Idle']
sc.frame_set(1)
save()
print('stage 9 done')

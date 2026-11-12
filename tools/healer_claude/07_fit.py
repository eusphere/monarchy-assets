"""Stage 7: fitted underlayer and seated jewelry.

* `Fitted bodice` - a close ivory layer over the torso and arms (the concept's
  long fitted sleeves), so no bare body form shows between the wraps.
* Necklace - every plaque and link is laid onto the surface it should rest on
  (cowl, bodice, shoulders) instead of floating as a wide ring.
* Cuff chain - re-hung from the wrists round behind her, outside the veil, slightly longer than before."""
import os
import sys

import bmesh
import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F401

rig = bpy.data.objects['Healer Rig']
dg = bpy.context.evaluated_depsgraph_get()


def eval_coords(ob):
    ev = ob.evaluated_get(dg)
    co = np.empty(3 * len(ev.data.vertices))
    ev.data.vertices.foreach_get('co', co)
    return co.reshape(-1, 3)


def islands(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    seen = np.zeros(len(bm.verts), bool)
    out = []
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
        out.append(np.array(isl))
    bm.free()
    return out


def frame(axis, hint):
    a = axis / np.linalg.norm(axis)
    n = hint - a * np.dot(hint, a)
    n /= max(np.linalg.norm(n), 1e-9)
    return np.stack([a, n, np.cross(a, n)], 1)


# ------------------------------------------------------------------ fitted bodice and sleeves
remove('Fitted bodice')
body = bpy.data.objects['Body form']
bod = bpy.data.objects.new('Fitted bodice', body.data.copy())
collection('Garments').objects.link(bod)
bod.parent = rig
bm = bmesh.new()
bm.from_mesh(bod.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < 1.26], context='VERTS')
bm.normal_update()
for v in bm.verts:
    v.co += v.normal * 0.0045
bm.to_mesh(bod.data)
bm.free()
bod.data.materials.clear()
bod.data.materials.append(bpy.data.materials['Voile'])
for m in list(bod.modifiers):
    bod.modifiers.remove(m)
sub = bod.modifiers.new('Smooth', 'SUBSURF')
sub.levels = sub.render_levels = 2
# Soft creases, as a close sleeve gathers along the arm.
tex = bpy.data.textures.get('Sleeve creases') or bpy.data.textures.new('Sleeve creases', 'CLOUDS')
tex.noise_scale = 0.035
tex.noise_depth = 2
dis = bod.modifiers.new('Creases', 'DISPLACE')
dis.texture = tex
dis.strength = 0.006
dis.mid_level = 0.35
body.hide_render = True

# ------------------------------------------------------------------ resting surface
names = ['Fitted bodice', 'Neck cowl', 'Shoulder wrap', 'Head wrap']
pts = np.vstack([eval_coords(bpy.data.objects[n]) for n in names])
pts = pts[(pts[:, 2] > 1.50) & (pts[:, 2] < 1.95)]
GT = 72
gth = 2 * np.pi * np.arange(GT) / GT
zs = np.arange(1.52, 1.94, 0.015)
ang = np.arctan2(pts[:, 1], pts[:, 0]) % (2 * np.pi)
rad = np.hypot(pts[:, 0], pts[:, 1])
# Arms out at the sides are not part of the collar's resting surface.
keep = rad < 0.22
surf = np.full((len(zs), GT), np.nan)
for i, z in enumerate(zs):
    band = keep & (np.abs(pts[:, 2] - z) < 0.012)
    for j in range(GT):
        d = np.abs((ang - gth[j] + np.pi) % (2 * np.pi) - np.pi)
        sel = band & (d < 2 * np.pi / GT)
        if sel.any():
            surf[i, j] = rad[sel].max()
for i in range(len(zs)):
    ok = ~np.isnan(surf[i])
    surf[i] = np.interp(np.arange(GT), np.where(ok)[0], surf[i][ok], period=GT) if ok.sum() > 3 else np.nan
for i in range(len(zs)):
    if np.isnan(surf[i]).any():
        surf[i] = surf[i - 1] if i else 0.06


def surface(theta, z, off=0.0):
    zi = np.clip((z - zs[0]) / (zs[1] - zs[0]), 0, len(zs) - 1.001)
    ti = (theta % (2 * np.pi)) / (2 * np.pi) * GT
    i0, j0 = int(zi), int(ti) % GT
    fz, ft = zi - i0, ti - int(ti)
    j1 = (j0 + 1) % GT
    r = ((surf[i0, j0] * (1 - ft) + surf[i0, j1] * ft) * (1 - fz)
         + (surf[i0 + 1, j0] * (1 - ft) + surf[i0 + 1, j1] * ft) * fz) + off
    return np.array([r * np.cos(theta), r * np.sin(theta), z])


# ------------------------------------------------------------------ plaque collar
# The old necklace was a wide rigid ring made for other garments. This one is built on the
# surface it rests on: a slim band along the collar line, and tapered, faceted plaques
# hanging from it across the front, each laid flat on the cloth beneath.
old = bpy.data.objects.get('Healer - flat linked plaque necklace')
if old:
    old.hide_render = old.hide_viewport = True
remove('Plaque collar')
# Smooth the resting surface so the pieces do not follow every small fold.
k = np.exp(-0.5 * (np.arange(-4, 5) / 1.6) ** 2)
k /= k.sum()
sm = np.stack([np.convolve(np.pad(r, 4, mode='wrap'), k, 'valid') for r in surf], 0)
sm = np.stack([np.convolve(np.pad(sm[:, j], 4, mode='edge'), k, 'valid') for j in range(GT)], 1)
surf = np.maximum(sm, surf - 0.004)


def collar_z(theta):
    # A heavy collar sags: it sits on the shoulders and hangs well down onto the chest in front.
    return 1.840 - 0.078 * max(-np.sin(theta), 0.0) ** 1.6


def laid(theta, z_top, length, off):
    """Top point, unit 'down the surface' axis and outward normal for a piece of given length."""
    T = surface(theta, z_top, off)
    B = T
    for dz in np.linspace(0.002, length, 30):
        B = surface(theta, z_top - dz, off)
        if np.linalg.norm(B - T) >= length:
            break
    # Weight pulls a plaque straight down wherever the body falls away beneath it.
    V = T + np.array([0.0, 0.0, -length])
    if np.hypot(V[0], V[1]) >= np.hypot(*surface(theta, V[2], off)[:2]):
        B = V
    axis = (B - T) / max(np.linalg.norm(B - T), 1e-9)
    side = np.cross(axis, np.array([np.cos(theta), np.sin(theta), 0.0]))
    side /= np.linalg.norm(side)
    normal = np.cross(side, axis)
    return T, axis, side, normal


cv, cf = [], []
# Band: a flat ribbon all the way round.
NB = 96
for i in range(NB):
    th = 2 * np.pi * i / NB
    zt = collar_z(th)
    cv += [tuple(surface(th, zt + 0.0075, 0.0035)), tuple(surface(th, zt - 0.0075, 0.0045))]
for i in range(NB):
    a0, b0 = 2 * i, 2 * i + 1
    a1, b1 = 2 * ((i + 1) % NB), 2 * ((i + 1) % NB) + 1
    cf.append((a0, a1, b1, b0))
# Plaques across the front, longest at the breastbone.
NP = 13
for i in range(NP):
    u = (i - (NP - 1) / 2) / ((NP - 1) / 2)                 # -1 .. 1
    th = np.radians(-90 + 78 * u)
    L = 0.104 * (1 - 0.48 * abs(u) ** 1.4)
    W = 0.0195 * (1 - 0.15 * abs(u))
    T, ax, sd, nm = laid(th, collar_z(th) - 0.009, L, 0.0040)
    H = 0.0055                                              # centre ridge
    outline = [(-0.42 * W, 0.0), (0.42 * W, 0.0), (0.5 * W, 0.14 * L), (0.40 * W, 0.74 * L),
               (0.0, L), (-0.40 * W, 0.74 * L), (-0.5 * W, 0.14 * L)]
    ridge = [(0.0, 0.10 * L), (0.0, 0.76 * L)]
    base = len(cv)
    for (pu, pv) in outline:
        cv.append(tuple(T + sd * pu + ax * pv))
    for (pu, pv) in ridge:
        cv.append(tuple(T + sd * pu + ax * pv + nm * H))
    o = [base + j for j in range(7)]
    r0, r1 = base + 7, base + 8
    cf += [(o[0], o[1], r0), (o[1], o[2], r0), (o[2], o[3], r1, r0), (o[3], o[4], r1),
           (o[4], o[5], r1), (o[5], o[6], r0, r1), (o[6], o[0], r0)]
collar = new_object('Plaque collar', cv, cf, 'Jewelry', smooth=False)
face_out(collar)
collar.data.materials.append(bpy.data.materials['TeamAccent'])
collar.parent = rig
vg = collar.vertex_groups.new(name='Chest')
vg.add(list(range(len(cv))), 1.0, 'REPLACE')
arm = collar.modifiers.new('Healer skin', 'ARMATURE')
arm.object = rig
sol = collar.modifiers.new('Thickness', 'SOLIDIFY')
sol.thickness = 0.0055
sol.offset = 1
bev = collar.modifiers.new('Edge', 'BEVEL')
bev.width = 0.0010
bev.segments = 2
bev.limit_method = 'ANGLE'

# ------------------------------------------------------------------ cuff chain
chain = bpy.data.objects['Healer - cuff to cuff plaque chain']
cc = coords(chain).copy()
isls = islands(chain)
cent = np.array([cc[i].mean(axis=0) for i in isls])
phi = np.arctan2(-cent[:, 0], -cent[:, 1]) % (2 * np.pi)      # 0 at the front, growing via the figure's right
# The old chain ran from the right wrist round the back to the left wrist.
wr = coords(bpy.data.objects['Fit04 tailored glove cuff raised']).mean(axis=0)
wl = coords(bpy.data.objects['Fit04 tailored glove cuff open']).mean(axis=0)
phi0 = np.arctan2(-wr[0], -wr[1]) % (2 * np.pi)
order = np.argsort((phi - phi0 + 0.3) % (2 * np.pi))
cent_o = cent[order]
s_old = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(cent_o, axis=0), axis=1))])
# New line: from each wrist out round the outside of the veil and behind her, hanging low
# across the back. It is a little longer than the chain was, so the links are stretched to suit.
TARGET = s_old[-1] * 1.14
# A heavy chain does not stand off the cloth: away from the wrists it lies against the veil,
# so its line is taken from the veil's own surface.
vc = eval_coords(bpy.data.objects['Head veil'])
va = np.arctan2(vc[:, 1], vc[:, 0]) % (2 * np.pi)
vr = np.hypot(vc[:, 0], vc[:, 1])
VT = 72
vth = 2 * np.pi * np.arange(VT) / VT
vz = np.arange(0.50, 1.75, 0.05)
vs = np.full((len(vz), VT), np.nan)
for i, z in enumerate(vz):
    band = np.abs(vc[:, 2] - z) < 0.04
    for j in range(VT):
        d = np.abs((va - vth[j] + np.pi) % (2 * np.pi) - np.pi)
        sel = band & (d < 2 * np.pi / VT)
        if sel.any():
            vs[i, j] = vr[sel].max()
for i in range(len(vz)):
    ok = ~np.isnan(vs[i])
    vs[i] = np.interp(np.arange(VT), np.where(ok)[0], vs[i][ok], period=VT) if ok.sum() > 3 else 0.25
kk = np.array([1, 2, 3, 2, 1]) / 9
vs = np.stack([np.convolve(np.pad(r, 2, mode='wrap'), kk, 'valid') for r in vs], 0)


def veil_radius(theta, z):
    i = int(np.clip(round((z - vz[0]) / 0.05), 0, len(vz) - 1))
    tj = (theta % (2 * np.pi)) / (2 * np.pi) * VT
    j0 = int(tj) % VT
    f = tj - int(tj)
    return vs[i, j0] * (1 - f) + vs[i, (j0 + 1) % VT] * f


th_r = np.arctan2(wr[1], wr[0])
th_l = np.arctan2(wl[1], wl[0])
sweep = (th_r - th_l) % (2 * np.pi)                       # the long way round, behind her
t = np.linspace(0, 1, 500)
th = th_r - sweep * t
r_ends = np.hypot(wr[0], wr[1]) * (1 - t) + np.hypot(wl[0], wl[1]) * t
ease = np.clip(np.minimum(t, 1 - t) / 0.10, 0, 1)
ease = ease * ease * (3 - 2 * ease)


def hang(sag):
    # Weight shows in the line: it drops almost straight from the wrists and lies low and flat behind.
    shape = (np.cosh(3.4) - np.cosh(3.4 * (2 * t - 1))) / (np.cosh(3.4) - 1)
    z = wr[2] * (1 - t) + wl[2] * t - sag * shape
    r_cloth = np.array([veil_radius(a, zz) for a, zz in zip(th, z)]) + 0.016
    r = r_ends * (1 - ease) + r_cloth * ease
    return np.column_stack([r * np.cos(th), r * np.sin(th), z])


lo, hi = 0.1, 1.3
for _ in range(40):
    mid = (lo + hi) / 2
    c = hang(mid)
    if np.linalg.norm(np.diff(c, axis=0), axis=1).sum() < TARGET:
        lo = mid
    else:
        hi = mid
curve = hang((lo + hi) / 2)
# Take out the small steps the surface lookup leaves in the line.
for _ in range(6):
    curve[1:-1] = 0.25 * curve[:-2] + 0.5 * curve[1:-1] + 0.25 * curve[2:]
print('chain sag %.2f lowest z %.2f' % ((lo + hi) / 2, curve[:, 2].min()), flush=True)
s_new = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))])
total = s_new[-1]
scale = total / s_old[-1]
drop = []
for k, oi in enumerate(order):
    isl = isls[oi]
    s = s_old[k] * scale
    if s > total + 1e-6:
        drop += list(isl)
        continue
    pos = np.array([np.interp(s, s_new, curve[:, i]) for i in range(3)])
    ahead = np.array([np.interp(min(s + 0.01, total), s_new, curve[:, i]) for i in range(3)])
    behind = np.array([np.interp(max(s - 0.01, 0), s_new, curve[:, i]) for i in range(3)])
    k0, k1 = max(k - 1, 0), min(k + 1, len(order) - 1)
    old_tan = cent_o[k1] - cent_o[k0]
    c = cent_o[k]
    old_out = np.array([c[0], c[1], 0.0])
    Fs = frame(old_tan, old_out)
    Ft = frame(ahead - behind, np.array([0.0, -1.0, 0.0]))
    local = (cc[isl] - c) @ Fs
    local[:, 0] *= scale                                   # longer links along the chain
    local[:, 1:] *= 1.38                                   # and heavier in section
    cc[isl] = local @ Ft.T + pos
set_coords(chain, cc)
if drop:
    bm = bmesh.new()
    bm.from_mesh(chain.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[int(i)] for i in drop], context='VERTS')
    bm.to_mesh(chain.data)
    bm.free()
print('chain islands kept', len(order) - sum(1 for k in range(len(order)) if s_old[k] > total),
      'of', len(order), 'old length %.2f new %.2f' % (s_old[-1], total), flush=True)

save()
render('stage7-front', 0)
render('stage7-three-quarter', 28)
render('stage7-side', 90)
render('stage7-rear', 180)
render('stage7-rear-quarter', 140)
render('stage7-portrait', 18, dist=2.6, target_z=1.92, lens=85, res=(900, 1125), samples=64)
render('stage7-jewelry', -20, dist=1.5, target_z=1.80, lens=85, res=(1000, 800), samples=64)
print('stage 7 done')

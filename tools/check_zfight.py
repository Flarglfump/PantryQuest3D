#!/usr/bin/env python3
"""Finds surfaces that would flicker against each other (z-fighting): pairs of triangles
in the same plane, facing the same way, that overlap. Looks at an area's level geometry
(models/areas/<area>/*.obj) and its plain cube entities. Standard library only.

    python3 tools/check_zfight.py [area ...]      (no names: every area)
"""
import glob
import math
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
EPS_D = 0.004          # metres: planes closer than this fight at a distance
EPS_N = 0.999          # normals this parallel count as the same direction
DETAIL = False
LOOSE = False          # (--loose: let alike-textured pairs pass; lit per corner, they still flicker)
MIN_AREA = 0.02        # square metres of overlap worth reporting


UVS = {}               # triangle -> its three texture coordinates (OBJ files only)


def load_obj(path):
    verts, uvs, tris = [], [], []
    for line in open(path):
        if line.startswith('v '):
            verts.append(tuple(float(x) for x in line.split()[1:4]))
        elif line.startswith('vt '):
            uvs.append(tuple(float(x) for x in line.split()[1:3]))
        elif line.startswith('f '):
            toks = [p.split('/') for p in line.split()[1:]]
            fix = lambda i, n: i - 1 if i > 0 else n + i
            idx = [fix(int(t[0]), len(verts)) for t in toks]
            tix = [fix(int(t[1]), len(uvs)) if len(t) > 1 and t[1] else None for t in toks]
            for k in range(1, len(idx) - 1):
                t = (verts[idx[0]], verts[idx[k]], verts[idx[k + 1]])
                tris.append(t)
                if None not in (tix[0], tix[k], tix[k + 1]):
                    UVS[t] = (uvs[tix[0]], uvs[tix[k]], uvs[tix[k + 1]])
    return tris


def uv_at(t, p):
    """The texture coordinate at point p (in t's plane), or None."""
    if t not in UVS:
        return None
    a, b, c = t
    v0, v1, v2 = sub(b, a), sub(c, a), sub(p, a)
    d00, d01, d11, d20, d21 = dot(v0, v0), dot(v0, v1), dot(v1, v1), dot(v2, v0), dot(v2, v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return None
    w1 = (d11 * d20 - d01 * d21) / den
    w2 = (d00 * d21 - d01 * d20) / den
    w0 = 1 - w1 - w2
    u = UVS[t]
    return (u[0][0] * w0 + u[1][0] * w1 + u[2][0] * w2, u[0][1] * w0 + u[1][1] * w1 + u[2][1] * w2)


def euler(rx, ry, rz):
    """R = Ry * Rx * Rz (degrees), as a function on points."""
    cx, sx = math.cos(math.radians(rx)), math.sin(math.radians(rx))
    cy, sy = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    cz, sz = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def f(p):
        x, y, z = p
        x, y = x * cz - y * sz, x * sz + y * cz
        y, z = y * cx - z * sx, y * sx + z * cx
        x, z = x * cy + z * sy, -x * sy + z * cy
        return (x, y, z)
    return f


def cube_tris(pos, rot, scale):
    r = euler(*rot)
    out = []
    corners = lambda sx, sy, sz: [(sx * a, sy * b, sz * c) for a, b, c in []]
    faces = [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))]
    for n, u, v in faces:
        pts = []
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = tuple(0.5 * (n[i] + a * u[i] + b * v[i]) * scale[i] for i in range(3))
            p = r(p)
            pts.append(tuple(p[i] + pos[i] for i in range(3)))
        out.append((pts[0], pts[1], pts[2]))
        out.append((pts[0], pts[2], pts[3]))
    return out


def scene_cubes(path):
    """[(name, tris)] for cube Mesh entities with no parent."""
    out = []
    for block in open(path).read().split('\nentity\n')[1:]:
        if 'shape = cube' not in block or '  Mesh\n' not in block or '  Parent\n' in block:
            continue
        name = re.search(r'text = "([^"]*)"', block)
        pos = re.search(r'Transform3D\n    position = (\S+) (\S+) (\S+)\n    rotation = (\S+) (\S+) (\S+)\n    scale = (\S+) (\S+) (\S+)', block)
        if not pos:
            continue
        v = [float(x) for x in pos.groups()]
        out.append((name.group(1) if name else '?', cube_tris(v[0:3], v[3:6], v[6:9])))
    return out


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def plane(t):
    n = cross(sub(t[1], t[0]), sub(t[2], t[0]))
    l = math.sqrt(dot(n, n))
    if l < 1e-9:
        return None
    n = (n[0] / l, n[1] / l, n[2] / l)
    return n, dot(n, t[0]), l / 2


def clip(poly, a, b):
    """The part of convex poly on the left of a->b (2D)."""
    out = []
    side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        sp, sq = side(p), side(q)
        if sp >= 0:
            out.append(p)
        if (sp >= 0) != (sq >= 0):
            t = sp / (sp - sq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def area2(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2


def overlap(t1, t2, n):
    """Area where two coplanar triangles overlap."""
    ax = max(range(3), key=lambda i: abs(n[i]))          # drop the axis the plane faces most
    keep = [i for i in range(3) if i != ax]
    to2 = lambda p: (p[keep[0]], p[keep[1]])
    a = [to2(p) for p in t1]
    b = [to2(p) for p in t2]
    ccw = lambda P: (P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[2][0] - P[0][0]) * (P[1][1] - P[0][1]) > 0
    if not ccw(a): a = a[::-1]
    if not ccw(b): b = b[::-1]
    poly = a
    for i in range(3):
        poly = clip(poly, b[i], b[(i + 1) % 3])
        if len(poly) < 3:
            return 0, None
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    # back to 3D: on t1's plane
    d = dot(n, t1[0])
    c = [0, 0, 0]
    c[keep[0]], c[keep[1]] = cx, cy
    c[ax] = (d - n[keep[0]] * cx - n[keep[1]] * cy) / n[ax]
    return area2(poly) / max(abs(n[ax]), 1e-6), tuple(c)


def material(part):
    """bark_-1_0.obj -> bark; Bed#3 -> Bed#3 (a cube is its own)."""
    return re.sub(r'_-?\d+_-?\d+\.obj$', '', part)


def check(area):
    parts = []
    sc = os.path.join(ROOT, 'areas', area + '.scene')
    used = sorted(set(re.findall(r'file = "(models/areas/[^"]+\.obj)"', open(sc).read()))) if os.path.exists(sc) else []
    for f in used:                     # (only the chunks the scene uses: not old files left behind)
        parts.append((os.path.basename(f), load_obj(os.path.join(ROOT, f))))
    if os.path.exists(sc):
        for k, (name, tris) in enumerate(scene_cubes(sc)):
            parts.append(('%s#%d' % (name, k), tris))
    buckets = {}
    for pi, (pname, tris) in enumerate(parts):
        both = pname.startswith('water_') or pname.startswith('canopy_')
        # (drawn from both sides: its back fights too, with anything facing the other way there)
        for t in tris + ([(t[0], t[2], t[1]) for t in tris] if both else []):
            pl = plane(t)
            if not pl:
                continue
            n, d, _ = pl
            if n[1] < -0.9:
                continue                 # (undersides: out of sight below the floors)
            key = (round(n[0], 1), round(n[1], 1), round(n[2], 1), round(d / 0.05))
            buckets.setdefault(key, []).append((pi, t, n, d))
    found = {}
    shown = set()
    for key, items in buckets.items():
        if len(items) < 2:
            continue
        # neighbours too: a plane near a bucket edge
        for i in range(len(items)):
            pi, t1, n1, d1 = items[i]
            for j in range(i + 1, len(items)):
                pj, t2, n2, d2 = items[j]
                if dot(n1, n2) < EPS_N or abs(d1 - d2) > EPS_D:
                    continue
                # quick bounds test
                if any(max(p[k] for p in t1) < min(p[k] for p in t2) - 1e-4 or max(p[k] for p in t2) < min(p[k] for p in t1) - 1e-4 for k in range(3)):
                    continue
                if set(t1) == set(t2) and material(parts[pi][0]) == material(parts[pj][0]):
                    continue          # the same triangle twice (drawn the same both times: no flicker)
                a, c3 = overlap(t1, t2, n1)
                if a > 1e-4 and abs(dot(n2, c3) - d2) > EPS_D:
                    continue          # (nearly parallel, but apart where they overlap)
                if a > 1e-4 and LOOSE and material(parts[pi][0]) == material(parts[pj][0]):
                    u1, u2 = uv_at(t1, c3), uv_at(t2, c3)
                    if u1 and u2 and all(abs((u1[k] - u2[k]) - round(u1[k] - u2[k])) < 0.01 for k in range(2)):
                        continue      # the same texture, the same way round: they look alike (no flicker)
                if a > 1e-4:
                    k2 = tuple(sorted((parts[pi][0], parts[pj][0])))
                    c = tuple(round(sum(p[k] for p in t1) / 3, 1) for k in range(3))
                    tot, at = found.get(k2, (0, c))
                    found[k2] = (tot + a, at)
                    if DETAIL and k2 not in shown:
                        shown.add(k2)
                        bb = lambda t: tuple(tuple(round(f(p[k] for p in t), 2) for k in range(3)) for f in (min, max))
                        print('   %s: n %s  %s %s | %s %s' % (area, tuple(round(x, 2) for x in n1), parts[pi][0], bb(t1), parts[pj][0], bb(t2)))
    return [(k, v) for k, v in found.items() if v[0] >= MIN_AREA]


def main(areas):
    global LOOSE, DETAIL
    if '--detail' in areas:
        DETAIL = True
        areas = [x for x in areas if x != '--detail']
    if '--loose' in areas:
        LOOSE = True
        areas = [x for x in areas if x != '--loose']
    if not areas:
        areas = sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(ROOT, 'areas', '*.scene')))
    total = 0
    for area in areas:
        res = check(area)
        for (a, b), (amount, at) in sorted(res, key=lambda r: -r[1][0]):
            print('%s: %s and %s overlap in one plane (%.2f m2, near %s)' % (area, a, b, amount, at))
        total += len(res)
    print('%d fighting pair(s)' % total)
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

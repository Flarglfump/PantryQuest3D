#!/usr/bin/env python3
"""Draws Pantry Quest 3D's textures and HUD icons (PNG) from code.

    python3 tools/make_art.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from kit import write_png, vnoise, hash2, mix  # noqa: E402


def tex(name, size, fn, alpha=False):
    write_png(os.path.join('art', name + '.png'), size, size, fn, alpha)


def fbm(x, y, scale, seed, wrap_px):
    v, amp, tot, s = 0.0, 1.0, 0.0, scale
    for o in range(3):
        v += vnoise(x, y, s, seed + o, wrap=max(1, int(wrap_px / s))) * amp
        tot += amp
        amp *= 0.5
        s /= 2
    return v / tot


def grass(x, y):
    n = fbm(x, y, 16, 1, 32)
    tuft = hash2(x, y, 3) > 0.93
    base = mix((70, 128, 52), (104, 166, 70), n)
    return mix(base, (150, 200, 90), 0.5) if tuft else base


def dirt(x, y):
    n = fbm(x, y, 8, 2, 32)
    pebble = hash2(x // 2, y // 2, 4) > 0.95
    base = mix((128, 96, 62), (160, 124, 84), n)
    return mix(base, (190, 170, 140), 0.6) if pebble else base


def bark(x, y):
    n = int(16 * math.sin(x * 1.1 + 3 * math.sin(y * 0.3)) + 10 * hash2(x, y, 5))
    return (104 + n, 72 + n, 46 + n // 2)


def planks(x, y):
    row = y // 8
    off = (row * 11) % 32
    seam = (y % 8 == 0) or ((x + off) % 32 == 0)
    n = fbm(x * 3, y, 16, 6 + row, 96) * 30
    c = (150 + n, 104 + n * 0.8, 62 + n * 0.5)
    return mix(c, (70, 46, 26), 0.7) if seam else c


def thatch(x, y):
    n = hash2(x, y // 3, 7)
    stripe = 20 * math.sin(x * 0.9 + n * 4)
    c = (190 + stripe, 160 + stripe, 80 + stripe * 0.5)
    return mix(c, (110, 84, 40), 0.5) if y % 8 < 1 else c


def leaves(x, y):
    n = fbm(x, y, 6, 8, 32)
    spot = hash2(x // 2, y // 2, 9)
    c = mix((44, 104, 46), (86, 156, 64), n)
    return mix(c, (30, 70, 34), 0.6) if spot < 0.15 else c


def hedge(x, y):
    n = fbm(x, y, 4, 10, 32)
    return mix((40, 92, 40), (72, 140, 58), n)


def stone(x, y):
    n = fbm(x, y, 8, 11, 32)
    crack = abs(vnoise(x, y, 6, 12, wrap=5) - 0.5) < 0.03
    c = mix((116, 116, 120), (160, 158, 160), n)
    return mix(c, (70, 70, 74), 0.6) if crack else c


def water(x, y):
    w = math.sin((x + 2 * math.sin(y * 0.4)) * 0.4) + math.sin(y * 0.3 + x * 0.1)
    return (60 + w * 10, 120 + w * 14, 170 + w * 12, 200)


def crock(x, y):          # glazed clay: a cream glaze with a blue band
    band = 10 <= y % 32 <= 13
    n = fbm(x, y, 8, 13, 32) * 20
    return (60 + n, 90 + n, 150 + n) if band else (210 + n, 196 + n, 160 + n)


def dough(x, y):
    n = fbm(x, y, 8, 14, 32)
    hole = vnoise(x, y, 4, 15, wrap=8) > 0.78
    c = mix((226, 206, 160), (244, 230, 192), n)
    return mix(c, (190, 160, 110), 0.6) if hole else c


def crust(x, y):
    n = fbm(x, y, 6, 16, 32)
    score = (x + y) % 16 == 0
    c = mix((160, 100, 40), (200, 140, 66), n)
    return mix(c, (110, 60, 24), 0.6) if score else c


def mould(x, y):
    n = fbm(x, y, 4, 17, 32)
    spot = vnoise(x, y, 3, 18, wrap=11) > 0.7
    c = mix((96, 120, 92), (150, 170, 130), n)
    return mix(c, (220, 230, 200), 0.6) if spot else c


def web(x, y):            # mould web: see-through strands
    s1 = abs(((x + y) % 8) - 4) < 1
    s2 = abs(((x - y) % 8) - 4) < 1
    ring = abs(math.hypot(x - 16, y - 16) % 6 - 3) < 0.8
    on = s1 or s2 or ring
    return (230, 236, 220, 230) if on else (200, 210, 190, 40)


def clay(x, y):
    n = fbm(x, y, 8, 19, 32) * 24
    band = y % 16 in (5, 6)
    return (120 + n, 70 + n * 0.5, 50) if band else (180 + n, 104 + n * 0.6, 66 + n * 0.3)


def sack(x, y):
    weave = ((x // 2) + (y // 2)) % 2
    n = hash2(x, y, 20) * 20
    return (176 + n - weave * 16, 150 + n - weave * 14, 100 + n - weave * 10)


def chest(x, y):
    band = x % 16 < 2 or y % 16 < 2
    return (200, 170, 60) if band else planks(x, y)


def rot(x, y):            # the dungeon's spoiled floor
    n = fbm(x, y, 8, 21, 32)
    return mix((70, 66, 50), (110, 104, 74), n)


def cobble(x, y):          # town cobbles: rounded stones in warm grey
    cx, cy = (x + (y // 8 % 2) * 4) % 8, y % 8
    edge = cx == 0 or cy == 0
    n = hash2((x + (y // 8 % 2) * 4) // 8, y // 8, 23)
    base = mix((150, 138, 120), (190, 176, 150), n)
    return mix(base, (100, 92, 80), 0.6) if edge else mix(base, (210, 200, 180), fbm(x, y, 4, 24, 32) * 0.25)


def crack(x, y):           # a cracked wall: stone with dark cracks running across it
    c = stone(x, y)
    k = abs(y - 16 - 7 * math.sin(x * 0.35)) < 1.1 or abs(x - 10 - 5 * math.sin(y * 0.4)) < 1.0 and y > 10
    return mix(c, (30, 26, 24), 0.85) if k else c


def lavacheese(x, y):      # bubbling molten cheese
    n = fbm(x, y, 8, 25, 32)
    b = vnoise(x, y, 4, 26, wrap=8) > 0.75
    c = mix((240, 150, 30), (255, 210, 80), n)
    return mix(c, (255, 250, 200), 0.6) if b else c


def flesh(x, y):           # the inside of a giant fish: pink, wet, veined
    n = fbm(x, y, 8, 31, 32)
    v = abs(vnoise(x, y, 6, 32, wrap=5) - 0.5) < 0.04
    c = mix((200, 90, 100), (240, 140, 140), n)
    return mix(c, (150, 40, 70), 0.6) if v else c


def fizzrock(x, y):        # pale blue water-worn stone with bubbles of light
    n = fbm(x, y, 8, 33, 32)
    b = hash2(x // 2, y // 2, 34) > 0.97
    c = mix((110, 150, 180), (170, 205, 225), n)
    return (230, 245, 255) if b else c


def sand(x, y):
    n = fbm(x, y, 4, 35, 32)
    return mix((200, 180, 130), (232, 214, 168), n)


def ice(x, y):              # pale blue ice with white cracks
    n = fbm(x, y, 8, 37, 32)
    c = mix((170, 210, 235), (225, 245, 255), n)
    if abs(vnoise(x, y, 5, 38, wrap=6) - 0.5) < 0.03:
        return (250, 255, 255)
    return c


def painting(x, y):        # a gloomy landscape in a gilt frame
    if x < 3 or y < 3 or x > 28 or y > 28:
        return (200, 160, 60) if (x + y) % 3 else (150, 110, 40)
    sky = mix((60, 70, 90), (120, 110, 130), y / 32)
    hill = 18 + 4 * math.sin(x * 0.3)
    if y > hill:
        return mix((50, 70, 40), (30, 40, 30), (y - hill) / 10)
    return sky


def flowers(x, y):
    g = grass(x, y)
    h = hash2(x // 2, y // 2, 22)
    if h > 0.975:
        return (240, 230, 120)
    if h > 0.955:
        return (230, 120, 160)
    return g


# ---- HUD icons: a 16 x 16 sheet, frames left to right ----------------------------------------
ICONS = ['heart4', 'heart3', 'heart2', 'heart1', 'heart0', 'bean', 'pea', 'key', 'spoon', 'potlid',
         'shooter', 'ember', 'map', 'compass', 'bosskey', 'pie', 'slice', 'fairy', 'jar', 'whistle', 'bomb', 'bracelet', 'ember2', 'letter', 'boss',
         'jar1', 'jar2', 'jar_fish', 'boomerang', 'fizzbubble', 'letter_fizzy', 'ember3', 'lash', 'bow', 'med_umami', 'med_bitter', 'hammer', 'apron', 'med_spice', 'boots', 'snorkel', 'med_salt', 'jar_fire', 'longlash', 'lens', 'hover', 'med_sour']


def icon_pixel(name, x, y):
    cx, cy = x - 7.5, y - 7.5
    if name.startswith('heart'):
        q = int(name[-1])
        hx, hy = cx / 7, -cy / 7
        inside = (hx * hx + (hy - abs(hx) ** 0.66) ** 2 * 1.4) < 0.8
        if not inside:
            return (0, 0, 0, 0)
        edge = (hx * hx + (hy - abs(hx) ** 0.66) ** 2 * 1.4) > 0.6
        ang = (math.degrees(math.atan2(cx, -cy)) + 360) % 360       # clockwise from the top
        full = ang < q * 90
        if edge:
            return (60, 10, 20, 255)
        return (230, 40, 60, 255) if full else (70, 40, 46, 200)
    if name == 'bean':
        d = (cx / 4.5) ** 2 + (cy / 6.5) ** 2
        if d > 1:
            return (0, 0, 0, 0)
        return (120, 230, 110, 255) if cx + cy < -3 else (40, 170, 60, 255)
    if name == 'pea':
        d = math.hypot(cx, cy)
        return (0, 0, 0, 0) if d > 5 else ((150, 230, 90, 255) if cx + cy < -2 else (70, 160, 40, 255))
    if name == 'key':
        if math.hypot(cx, cy + 4) < 3.2 and math.hypot(cx, cy + 4) > 1.4:
            return (230, 200, 80, 255)
        if abs(cx) < 1.1 and -1 < cy < 7:
            return (230, 200, 80, 255)
        if 0 < cx < 3.5 and cy in (3.5, 5.5):
            return (230, 200, 80, 255)
        return (0, 0, 0, 0)
    if name == 'spoon':
        if (cx - 3) ** 2 / 9 + (cy + 3) ** 2 / 9 < 1:
            return (200, 150, 90, 255)
        if abs(cx + cy) < 1.3 and cx < 2 and cy < 5 and cx > -6:
            return (170, 120, 70, 255)
        return (0, 0, 0, 0)
    if name == 'potlid':
        d = math.hypot(cx, cy)
        if d > 7:
            return (0, 0, 0, 0)
        if d < 1.8:
            return (90, 90, 96, 255)
        return (170, 170, 176, 255) if d < 6 else (110, 110, 116, 255)
    if name == 'shooter':
        if abs(cx) < 1 and 0 < cy < 7:
            return (150, 100, 50, 255)
        if abs(abs(cx) - 4) < 1 and -7 < cy < 1:
            return (150, 100, 50, 255)
        if -1 < cy < 1 and abs(cx) < 5:
            return (150, 100, 50, 255)
        if -6 < cy < -4 and abs(cx) < 4:
            return (220, 190, 150, 255)
        return (0, 0, 0, 0)
    if name == 'ember':
        d = abs(cx) * 1.3 + abs(cy + 1) * 0.9
        if d > 7:
            return (0, 0, 0, 0)
        return (255, 240, 160, 255) if d < 3 else (250, 140, 40, 255)
    if name == 'map':
        if abs(cx) < 6 and abs(cy) < 5:
            return (120, 160, 90, 255) if (int(x) // 3 + int(y) // 4) % 2 else (220, 200, 150, 255)
        return (0, 0, 0, 0)
    if name == 'compass':
        d = math.hypot(cx, cy)
        if d > 6.5:
            return (0, 0, 0, 0)
        if abs(cx) < 1.2 and cy < 0:
            return (220, 40, 40, 255)
        return (200, 160, 60, 255) if d > 5 else (240, 236, 220, 255)
    if name == 'bosskey':
        k = icon_pixel('key', x, y)
        return (220, 90, 60, 255) if k[3] else k
    if name in ('pie', 'slice'):
        d = math.hypot(cx, cy)
        ang = (math.degrees(math.atan2(cx, -cy)) + 360) % 360
        if d > 7 or (name == 'slice' and ang > 90):
            return (0, 0, 0, 0)
        return (200, 140, 60, 255) if d > 5.5 else (220, 50, 80, 255)
    if name == 'fairy':
        d = math.hypot(cx, cy)
        return (0, 0, 0, 0) if d > 5 else (255, 200, 240, 255 if d < 3 else 140)
    if name == 'jar':
        if abs(cx) < 4 and -3 < cy < 7 or abs(cx) < 2 and -7 < cy <= -3:
            return (190, 220, 240, 200)
        return (0, 0, 0, 0)
    if name == 'whistle':
        d = math.hypot(cx, cy + 1)
        if d < 5.5 or (-1 < cx < 1 and cy < -4 and cy > -7):
            return (160, 170, 200, 255) if d < 4.5 else (90, 100, 130, 255)
        return (0, 0, 0, 0)
    if name == 'bomb':
        d = math.hypot(cx, cy + 1)
        if d < 5.5:
            return (255, 244, 210, 255) if cx + cy < 0 else (230, 200, 150, 255)
        if abs(cx - 1) < 1 and -7 < cy < -5:
            return (120, 80, 40, 255)
        return (0, 0, 0, 0)
    if name == 'bracelet':
        d = math.hypot(cx, cy)
        return (230, 120, 170, 255) if 3.5 < d < 6 else (0, 0, 0, 0)
    if name == 'ember2':
        e = icon_pixel('ember', x, y)
        return (255, 90, 60, 255) if e[3] and e[1] < 200 else e
    if name in ('jar1', 'jar2'):
        return icon_pixel('jar', x, y)
    if name == 'jar_fish':
        j = icon_pixel('jar', x, y)
        if j[3] and (cx / 3) ** 2 + ((cy - 2) / 1.6) ** 2 < 1:
            return (240, 140, 50, 255)
        return j
    if name == 'boomerang':
        if abs(cx) < 1.3 and -1 < cy < 7:
            return (170, 120, 70, 255)
        if abs(cx) < 4 and -7 < cy < -1:
            return (220, 210, 190, 255) if abs(cx) < 3 else (150, 150, 150, 255)
        return (0, 0, 0, 0)
    if name == 'fizzbubble':
        d = math.hypot(cx, cy)
        if d > 6.5:
            return (0, 0, 0, 0)
        if math.hypot(cx + 2, cy + 2) < 1.5:
            return (255, 255, 255, 255)
        return (120, 200, 250, 200) if d < 5.5 else (60, 130, 220, 255)
    if name == 'letter_fizzy':
        l = icon_pixel('letter', x, y)
        return (60, 140, 230, 255) if l[3] and l[0] == 200 else l
    if name == 'ember3':
        e = icon_pixel('ember', x, y)
        return (90, 170, 255, 255) if e[3] and e[1] < 200 else e
    if name == 'lash':
        d = math.hypot(cx, cy)
        if 3 < d < 5.5 and not (cx > 0 and cy > 0):
            return (200, 40, 60, 255)
        if abs(cx - cy) < 1.2 and cx > 0 and cy > 0 and cx < 7:
            return (200, 40, 60, 255)
        return (0, 0, 0, 0)
    if name == 'bow':
        if abs(math.hypot(cx + 4, cy) - 8) < 1.1 and cx > -1:
            return (170, 110, 60, 255)
        if abs(cx - 2.5) < 0.5 and abs(cy) < 6.5:
            return (240, 240, 230, 255)
        return (0, 0, 0, 0)
    if name == 'lens':
        d = math.hypot(cx, cy + 1)
        if d < 5.5:
            return (200, 140, 220, 220) if d < 4 else (140, 80, 160, 255)
        if abs(cx) < 1 and -7 < cy < -5:
            return (90, 170, 60, 255)
        return (0, 0, 0, 0)
    if name == 'hover':
        b = icon_pixel('boots', x, y)
        return (250, 245, 230, 255) if b[3] else b
    if name == 'med_sour':
        d = math.hypot(cx, cy)
        if d > 6:
            return (0, 0, 0, 0)
        return (170, 90, 200, 255) if d < 4.5 else (180, 150, 60, 255)
    if name == 'boots':
        if (-6 < cy < 5 and -3 < cx < 1) or (2 < cy < 6 and -3 < cx < 5):
            return (90, 90, 100, 255) if cy < 5 else (60, 60, 70, 255)
        return (0, 0, 0, 0)
    if name == 'snorkel':
        a = icon_pixel('apron', x, y)
        return (60, 130, 220, 255) if a[3] and (x + y) % 4 else ((40, 90, 180, 255) if a[3] else a)
    if name == 'med_salt':
        d = math.hypot(cx, cy)
        if d > 6:
            return (0, 0, 0, 0)
        return (90, 160, 240, 255) if d < 4.5 else (180, 150, 60, 255)
    if name == 'jar_fire':
        j = icon_pixel('jar', x, y)
        if j[3] and abs(cx) < 2.5 and -1 < cy < 5:
            return (90, 160, 255, 255)
        return j
    if name == 'longlash':
        l = icon_pixel('lash', x, y)
        return (230, 120, 40, 255) if l[3] else l
    if name == 'hammer':
        if abs(cx) < 1 and -2 < cy < 7:
            return (150, 100, 60, 255)
        if abs(cx) < 5 and -7 < cy < -2:
            return (190, 190, 200, 255)
        return (0, 0, 0, 0)
    if name == 'apron':
        if abs(cx) < 5 - max(0, -cy - 2) * 0.8 and -7 < cy < 7:
            return (220, 120, 60, 255) if (x + y) % 4 else (180, 80, 40, 255)
        return (0, 0, 0, 0)
    if name == 'med_spice':
        d = math.hypot(cx, cy)
        if d > 6:
            return (0, 0, 0, 0)
        return (230, 90, 50, 255) if d < 4.5 else (180, 150, 60, 255)
    if name in ('med_umami', 'med_bitter'):
        d = math.hypot(cx, cy)
        if d > 6:
            return (0, 0, 0, 0)
        c = (240, 200, 80, 255) if name == 'med_umami' else (90, 190, 80, 255)
        return c if d < 4.5 else (180, 150, 60, 255)
    if name == 'letter':
        if abs(cx) < 6 and abs(cy) < 4:
            return (200, 60, 60, 255) if abs(cx) < 1.5 and abs(cy) < 1.5 else (240, 230, 200, 255)
        return (0, 0, 0, 0)
    return (255, 0, 255, 255)


def main():
    for name, fn, size in [('grass', grass, 32), ('dirt', dirt, 32), ('bark', bark, 16), ('planks', planks, 32),
                           ('thatch', thatch, 32), ('leaves', leaves, 32), ('hedge', hedge, 32), ('stone', stone, 32),
                           ('crock', crock, 32), ('dough', dough, 32), ('crust', crust, 32), ('mould', mould, 32),
                           ('clay', clay, 16), ('sack', sack, 16), ('chest', chest, 32), ('rot', rot, 32),
                           ('flowers', flowers, 32), ('cobble', cobble, 32), ('crack', crack, 32), ('lavacheese', lavacheese, 32),
                           ('flesh', flesh, 32), ('fizzrock', fizzrock, 32), ('sand', sand, 32), ('painting', painting, 32), ('ice', ice, 32)]:
        tex(name, size, fn)
    tex('water', 32, water, alpha=True)
    tex('web', 32, web, alpha=True)
    for name in ICONS:          # one picture each: draw_image("art/icons/<name>.png", centre)
        write_png(os.path.join('art', 'icons', name + '.png'), 16, 16, lambda x, y, n=name: icon_pixel(n, x, y), alpha=True)
    print('art written')


if __name__ == '__main__':
    main()

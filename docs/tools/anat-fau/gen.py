# 第 03 章「立體解剖：台積電 COUPE-GC 光引擎的耦光結構」的 SVG 產生器（等角分解圖，2026-10-08 版）。
# 跑法：PYTHONUTF8=1 python gen.py → new.svg、new-pins.html、preview.html（可用無頭 Chrome 截圖看）；改完再跑 apply.py 套進 CPO.html。
# 場景座標：x 往右下、y 往左下、z 往上；數字都是場景單位，SCALE 控制整體縮放。
import math, os, re, colorsys

HERE = os.path.dirname(os.path.abspath(__file__))
C = math.cos(math.radians(30)); S = 0.5
SCALE = 1.12
VW, VH = 900, 700
INK = '#1c1f26'

def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
def rgb2hex(r, g, b): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v*255))) for v in (r, g, b))
def shade(h, f):
    r, g, b = hex2rgb(h); hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return rgb2hex(*colorsys.hls_to_rgb(hh, max(0, min(1, l*f)), s))

OX, OY = 0.0, 0.0
def P(x, y, z): return (OX + C*(x - y)*SCALE, OY + S*(x + y)*SCALE - z*SCALE)
def fmt(pts): return ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts)
def poly(pts, fill, stroke=INK, sw=1.2, extra=''):
    return f'<polygon points="{fmt(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'

def box(x, y, z, dx, dy, dz, col, sw=1.2):
    t = [P(x, y, z+dz), P(x+dx, y, z+dz), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    l = [P(x, y+dy, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    r = [P(x+dx, y, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x+dx, y, z+dz)]
    return poly(l, shade(col, .80), sw=sw) + poly(r, shade(col, .90), sw=sw) + poly(t, col, sw=sw)

def frame(x, y, z, dx, dy, dz, ix, iy, idx, idy, col, sw=1.2):
    """有方形開口的框：外框 x..x+dx / y..y+dy，內孔 ix..ix+idx / iy..iy+idy"""
    out = ''
    wx = [P(ix, iy, z), P(ix, iy+idy, z), P(ix, iy+idy, z+dz), P(ix, iy, z+dz)]
    wy = [P(ix, iy, z), P(ix+idx, iy, z), P(ix+idx, iy, z+dz), P(ix, iy, z+dz)]
    out += poly(wx, shade(col, .68), sw=sw) + poly(wy, shade(col, .58), sw=sw)
    l = [P(x, y+dy, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    r = [P(x+dx, y, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x+dx, y, z+dz)]
    out += poly(l, shade(col, .80), sw=sw) + poly(r, shade(col, .90), sw=sw)
    t_out = [P(x, y, z+dz), P(x+dx, y, z+dz), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    t_in = [P(ix, iy, z+dz), P(ix+idx, iy, z+dz), P(ix+idx, iy+idy, z+dz), P(ix, iy+idy, z+dz)]
    out += (f'<path d="M{fmt(t_out)}Z M{fmt(t_in)}Z" fill="{col}" fill-rule="evenodd" '
            f'stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    return out

def bevel_box(x, y0, z, dx, yfb, dz, col, mirror='#f7ecd2'):
    """前端切 45° 的方塊：底面前緣在 y=yfb，頂面前緣在 y=yfb-dz；斜面＝反射面"""
    yft = yfb - dz
    t = [P(x, y0, z+dz), P(x+dx, y0, z+dz), P(x+dx, yft, z+dz), P(x, yft, z+dz)]
    r = [P(x+dx, y0, z), P(x+dx, yfb, z), P(x+dx, yft, z+dz), P(x+dx, y0, z+dz)]
    m = [P(x, yft, z+dz), P(x+dx, yft, z+dz), P(x+dx, yfb, z), P(x, yfb, z)]
    return poly(r, shade(col, .90)) + poly(t, col) + poly(m, mirror, '#a96812', 1.3)

def ell(cx, cy, z, r, fill, stroke=INK, sw=1, extra=''):
    px, py = P(cx, cy, z)
    return (f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{1.2247*r*SCALE:.1f}" ry="{0.7071*r*SCALE:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def line3(a, b, stroke, sw, extra=''):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def label(x, y, z, s, size=12.5, fill='#5a6273', anchor='start', weight='600', dx=0, dy=0):
    px, py = P(x, y, z)
    return f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'

# ---------- 場景 ----------
SDX, SDY = 256, 196          # 晶片堆疊 footprint
GX, GY = 200, 158            # 光柵／微透鏡位置
Z_SUB = (0, 12); Z_PIC = (20, 46); Z_EIC = (90, 110); Z_CAR = (154, 180)
Z_REC = (180, 196)           # Receptacle 坐在 Si Carrier 上
Z_CPL = (228, 236)           # Carrier 定位載板
Z_PMLA = (250, 255)
Z_FA = (268, 296); Z_LID = (296, 322)
FIB_Z = Z_FA[1]
FX = [GX + (i-2.5)*13 for i in range(6)]
FA_X0, FA_DX = GX-43, 86
FA_Y0 = 14                   # FAU 後端
STRIP = 48                   # 後段露出的 V 溝長度
CP_X0, CP_DX = GX-56, 112
CP_Y0, CP_DY = 2, 178
RC_X0, RC_DX = CP_X0-10, CP_DX+20
RC_Y0, RC_DY = CP_Y0-10, CP_DY+20
BALLS = [(CP_X0+9, CP_Y0+9), (CP_X0+CP_DX-9, CP_Y0+9), (GX, CP_Y0+CP_DY-9)]

def build():
    g, lab = [], []
    # 封裝基板
    g.append(box(-16, -16, Z_SUB[0], SDX+32, SDY+32, Z_SUB[1]-Z_SUB[0], '#efeaf6'))
    # 凸塊
    for i in range(6): g.append(ell(22+i*38, SDY-5, 16, 4, '#e9c96e', '#a96812', 1))
    for i in range(4): g.append(ell(SDX-5, 20+i*38, 16, 4, '#e9c96e', '#a96812', 1))
    # PIC ＋ 光柵（綠線）在銅色反射層上 ＋ 波導
    g.append(box(0, 0, Z_PIC[0], SDX, SDY, Z_PIC[1]-Z_PIC[0], '#cfe2f4'))
    zt = Z_PIC[1]
    g.append(poly([P(GX-22, GY-15, zt), P(GX+22, GY-15, zt), P(GX+22, GY+15, zt), P(GX-22, GY+15, zt)], '#d9905a', '#9a5a2a', 1))
    for k in range(5):
        yy = GY-10+k*5
        g.append(line3((GX-17, yy, zt+.1), (GX+17, yy, zt+.1), '#0c7a53', 2.2))
    a, b = P(GX-22, GY, zt+.1), P(30, GY, zt+.1)
    g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#0b5871" stroke-width="2" stroke-dasharray="6 4" fill="none"/>')
    a, b = P(30, GY, zt+.1), P(40, GY-7, zt+.1)
    g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#0b5871" stroke-width="1.6" fill="none"/>')
    a, b = P(30, GY, zt+.1), P(40, GY+7, zt+.1)
    g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#0b5871" stroke-width="1.6" fill="none"/>')
    # EIC（有開口）
    g.append(frame(0, 0, Z_EIC[0], SDX, SDY, Z_EIC[1]-Z_EIC[0], GX-28, GY-20, 56, 40, '#d6ecd6'))
    # Si Carrier ＋ 矽微透鏡
    g.append(box(0, 0, Z_CAR[0], SDX, SDY, Z_CAR[1]-Z_CAR[0], '#e6e7ec'))
    zc = Z_CAR[1]
    for fx in FX:
        g.append(ell(fx, GY, zc, 6.5, '#f3e3b4', '#a96812', 1))
        g.append(ell(fx, GY, zc, 3.2, '#fff6dc', '#a96812', .7))
    # Receptacle 插座框 ＋ 三個定位孔
    g.append(frame(RC_X0, RC_Y0, Z_REC[0], RC_DX, RC_DY, Z_REC[1]-Z_REC[0], CP_X0+14, CP_Y0+14, CP_DX-28, CP_DY-28, '#c9ced8'))
    for bx, by in BALLS: g.append(ell(bx, by, Z_REC[1], 3.6, '#5b6170', '#2d3340', .8))
    # 定位珠（掛在載板下方）＋ Carrier 載板（有開口）＋ 珠頂
    for bx, by in BALLS: g.append(ell(bx, by, Z_CPL[0]-5, 5.2, 'url(#ball)', '#8a6a1c', .9))
    g.append(frame(CP_X0, CP_Y0, Z_CPL[0], CP_DX, CP_DY, Z_CPL[1]-Z_CPL[0], FA_X0-4, GY-26, FA_DX+8, 52, '#e3d9c2'))
    for bx, by in BALLS: g.append(ell(bx, by, Z_CPL[1], 3.2, '#e9c96e', '#8a6a1c', .8))
    # PMLA 薄片 ＋ 4 顆小透鏡
    g.append(box(FA_X0, GY-20, Z_PMLA[0], FA_DX, 40, Z_PMLA[1]-Z_PMLA[0], '#dff2f6'))
    for fx in FX: g.append(ell(fx, GY, Z_PMLA[1], 4.5, '#e9c96e', '#a96812', .9))
    # FA 基板（前端 45°）；光纖躺在基板頂、後段露出 V 溝
    g.append(box(FA_X0, FA_Y0, Z_FA[0], FA_DX, (GY+14)-FA_Y0, Z_FA[1]-Z_FA[0], '#eef4f7'))
    yf = GY+14
    for fx in FX:
        a, b, c = P(fx-4, yf, Z_FA[1]), P(fx, yf, Z_FA[1]-7), P(fx+4, yf, Z_FA[1])
        g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{c[0]:.1f} {c[1]:.1f}" fill="none" stroke="#3f3f4c" stroke-width="1"/>')
        px, py = P(fx, yf, Z_FA[1]-3.2)
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.6*SCALE:.1f}" fill="#dceaf1" stroke="#7fa5b8" stroke-width="1"/>')
    for fx in FX:
        for dxx in (-3.6, 3.6):
            g.append(line3((fx+dxx, FA_Y0, Z_FA[1]+.1), (fx+dxx, FA_Y0+STRIP, Z_FA[1]+.1), '#8b94a3', .9))
    for fx in FX:
        a, b = (fx, FA_Y0+STRIP+2, FIB_Z+1), (fx, -128, FIB_Z+1)
        g.append(line3(a, b, '#7fa5b8', 7.5*SCALE, 'stroke-linecap="round"'))
        g.append(line3(a, b, '#dceaf1', 2.4*SCALE, 'stroke-linecap="round"'))
    # 上蓋（玻璃，從露出段之後開始；前端同一個 45° 面）
    g.append(bevel_box(FA_X0, FA_Y0+STRIP, Z_LID[0], FA_DX, GY, Z_LID[1]-Z_LID[0], '#e8f1f4'))
    # 反射面上標一條鏡線（光纖高度）
    g.append(line3((FA_X0, GY, Z_LID[0]+.5), (FA_X0+FA_DX, GY, Z_LID[0]+.5), '#a96812', 1.6, 'stroke-dasharray="3 2"'))
    # 光路：沿第 3 根光纖 → 反射面 → 垂直往下 → 光柵
    bx = FX[2]
    pts = [(bx, -90, FIB_Z+1), (bx, GY, FIB_Z+1), (bx, GY, Z_PIC[1])]
    d = 'M' + ' L'.join(f'{P(*p)[0]:.1f} {P(*p)[1]:.1f}' for p in pts)
    g.append(f'<path id="ca_beam" d="{d}" fill="none" stroke="#0e6e8c" stroke-width="2.4" stroke-dasharray="7 4"/>')
    a1, a2 = P(bx+7, GY+7, Z_PIC[1]-6), P(bx+7, GY+7, Z_PIC[1]+12)
    g.append(f'<path d="M{a1[0]:.1f} {a1[1]:.1f} L{a2[0]:.1f} {a2[1]:.1f}" stroke="#b3362c" stroke-width="1.6" marker-end="url(#arr)"/>')
    g.append('<circle r="3.8" fill="#b3362c"><animateMotion dur="4s" repeatCount="indefinite"><mpath href="#ca_beam"/></animateMotion></circle>')
    # 標籤：右側一排＋引線（螢幕座標固定 x）
    TX = 650
    def lead(pt, s, sy, size=12.5, fill='#5a6273', weight='600'):
        px, py = P(*pt)
        return (f'<path d="M{TX-8:.0f} {sy-4:.0f} L{px:.1f} {py:.1f}" stroke="#9aa3b2" stroke-width="1" fill="none"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#9aa3b2"/>'
                f'<text x="{TX}" y="{sy}" font-size="{size}" fill="{fill}" font-weight="{weight}">{s}</text>')
    lab.append(lead((FA_X0+FA_DX, FA_Y0+STRIP+34, Z_LID[0]+12), 'FAU（FA＋反射面＋PMLA）', 250, 13, INK, '800'))
    lab.append(lead((FA_X0+FA_DX, GY-6, Z_PMLA[1]), 'PMLA 平面微透鏡陣列', 296))
    lab.append(lead((CP_X0+CP_DX, CP_Y0+40, Z_CPL[1]), 'Carrier 定位載板（3 珠 3 孔）', 330))
    lab.append(lead((RC_X0+RC_DX, RC_Y0+30, Z_REC[1]), 'Receptacle 插座（固定在晶片上）', 364))
    lab.append(lead((SDX, 30, Z_CAR[0]+13), 'Si Carrier 矽載板（頂面有微透鏡）', 430))
    lab.append(lead((SDX, 30, Z_EIC[0]+10), 'EIC 電晶片（留開口讓光過）', 510))
    lab.append(lead((SDX, 30, Z_PIC[0]+13), 'PIC 矽光子晶片（光柵在上、銅反射層在下）', 590))
    lab.append(label(-16, SDY+16, Z_SUB[0]+6, '封裝基板', anchor='end', dx=-8, dy=4))
    lab.append(label(-5, GY-8, Z_PIC[1], '光往晶片內的波導走', anchor='end', dx=-6, dy=2, size=12.5))
    return ''.join(g), ''.join(lab)

def main():
    global OX, OY
    body, labels = build()
    xs, ys = [], []
    for m in re.finditer(r'(-?\d+\.\d)[, ](-?\d+\.\d)', body):
        xs.append(float(m.group(1))); ys.append(float(m.group(2)))
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    OX = (VW - (maxx-minx))/2 - minx - 95
    OY = (VH - (maxy-miny))/2 - miny + 22
    body, labels = build()
    defs = ('<defs><radialGradient id="ball" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#fff6dc"/>'
            '<stop offset="1" stop-color="#c9a24a"/></radialGradient>'
            '<marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">'
            '<path d="M0 0 L6 3 L0 6 Z" fill="#b3362c"/></marker></defs>')
    title = ('<text x="26" y="34" font-size="15.5" letter-spacing="2" fill="#8b94a3" font-weight="700">台積電 COUPE-GC 光引擎與 FAU 的耦光結構</text>'
             f'<text x="{VW-26}" y="34" text-anchor="end" font-size="15" fill="#8b94a3">等角分解示意：零件照實際順序、不照比例</text>')
    svg = (f'<svg viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" font-family="\'Noto Sans TC\',\'Microsoft JhengHei\',sans-serif">\n'
           f'  <rect x="0" y="0" width="{VW}" height="{VH}" fill="#ffffff"/>\n  {defs}\n  {title}\n  {body}\n  {labels}\n</svg>')
    pins = [
        (1, 'FAU', (FA_X0+FA_DX/2, FA_Y0+STRIP+30, Z_LID[1])),
        (2, '光纖', (FX[1], -70, FIB_Z)),
        (3, '反射面', (FA_X0+FA_DX/2, GY+2, Z_LID[0]+4)),
        (4, 'V 溝', (FX[0]-8, FA_Y0+4, Z_FA[1])),
        (5, 'PMLA', (FA_X0+6, GY+12, Z_PMLA[1])),
        (6, 'Carrier', (CP_X0+CP_DX-9, CP_Y0+CP_DY-16, Z_CPL[1])),
        (7, 'Receptacle', (RC_X0+RC_DX-8, RC_Y0+60, Z_REC[1])),
        (8, '微透鏡', (GX+34, GY-14, Z_CAR[1])),
        (9, '堆疊', (SDX-26, SDY-22, Z_EIC[1])),
    ]
    pin_html = []
    for n, name, p in pins:
        px, py = P(*p)
        pin_html.append(f'<span class="pin" data-a="{n}" style="left:{px/VW*100:.0f}%;top:{py/VH*100:.0f}%">{n}</span>')
    with open(os.path.join(HERE, 'new.svg'), 'w', encoding='utf-8') as f: f.write(svg)
    with open(os.path.join(HERE, 'new-pins.html'), 'w', encoding='utf-8') as f: f.write('\n'.join(pin_html))
    css = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}.img-in{position:relative;width:900px}.img-in>svg{display:block;width:100%;height:auto}'
           '.pin{position:absolute;width:28px;height:28px;margin:-14px 0 0 -14px;border-radius:50%;background:#b3362c;color:#fff;border:2px solid #fff;font-size:13px;font-weight:800;display:flex;align-items:center;justify-content:center}')
    with open(os.path.join(HERE, 'preview.html'), 'w', encoding='utf-8') as f:
        f.write(css + '</style><div class="img-in">' + svg + '\n' + '\n'.join(pin_html) + '</div>')
    print('bbox', round(minx), round(maxx), round(miny), round(maxy), 'offset', round(OX), round(OY))

main()

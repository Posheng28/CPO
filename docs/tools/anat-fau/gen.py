# 第 03 章「立體解剖：台積電 COUPE-GC 光引擎的耦光結構」的 SVG 產生器（等角分解圖，2026-10-09 版）。
# 跑法：PYTHONUTF8=1 python gen.py → new-flat.svg（平面分解圖）、new-real.svg（擬真渲染）、new-pins.html、preview-flat.html、preview-real.html
#       改完再跑 apply.py 套進 CPO.html（兩張圖都放進去，頁面上有切換鈕）。
# 場景座標：x 往右下、y 往左下、z 往上；數字都是場景單位，SCALE 控制整體縮放。兩種風格共用同一套幾何，紅點位置相同。
import math, os, re, colorsys

HERE = os.path.dirname(os.path.abspath(__file__))
C = math.cos(math.radians(30)); S = 0.5
SCALE = 1.12
VW, VH = 900, 700
INK = '#1c1f26'
MODE = 'flat'          # 'flat' | 'real'
PFX = 'f'              # id 前綴，兩張圖同時放在一頁時 id 不能撞

def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
def rgb2hex(r, g, b): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v*255))) for v in (r, g, b))
def shade(h, f):
    r, g, b = hex2rgb(h); hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return rgb2hex(*colorsys.hls_to_rgb(hh, max(0, min(1, l*f)), s))

OX, OY = 0.0, 0.0
def P(x, y, z): return (OX + C*(x - y)*SCALE, OY + S*(x + y)*SCALE - z*SCALE)
def fmt(pts): return ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts)

# ---------- 材質 ----------
# flat：單色＋黑描邊；real：漸層＋淡描邊＋高光。base_flat / base_real 分開給，kind 決定漸層長相
MAT = {
    'sub':   dict(flat='#efeaf6', real='#2f6b45', kind='matte'),    # 封裝基板（擬真：綠色載板）
    'pic':   dict(flat='#cfe2f4', real='#4a5f7a', kind='silicon'),
    'eic':   dict(flat='#d6ecd6', real='#3a4556', kind='silicon'),
    'car':   dict(flat='#e6e7ec', real='#c3c9d3', kind='silicon'),
    'rec':   dict(flat='#c9ced8', real='#9aa3ad', kind='metal'),
    'cpl':   dict(flat='#e3d9c2', real='#3b3e45', kind='matte'),    # 定位載板（擬真：黑色陶瓷）
    'pmla':  dict(flat='#dff2f6', real='#cfeaf6', kind='glass'),
    'fa':    dict(flat='#eef4f7', real='#e4f1f9', kind='glass'),
    'lid':   dict(flat='#e8f1f4', real='#dcebf5', kind='glass'),
    'mt':    dict(flat='#efe9dc', real='#ece6d8', kind='matte'),    # MT 插芯
    'boot':  dict(flat='#6b6f78', real='#3a3f47', kind='matte'),
    'rib':   dict(flat='#e9d27a', real='#e2c24a', kind='matte'),    # 光纖帶
}
FLAT_F = {'t': 1.0, 'l': .80, 'r': .90, 'w': .62}

def grad_defs():
    """real 模式：每種材質三個面各一個漸層"""
    out = []
    for name, m in MAT.items():
        b = m['real']; k = m['kind']
        if k == 'metal':
            stops = {'t': [(0, 1.35), (.35, .95), (.5, 1.25), (.75, .9), (1, 1.1)],
                     'l': [(0, .8), (.5, .55), (1, .7)], 'r': [(0, 1.0), (.5, .75), (1, .9)], 'w': [(0, .6), (1, .4)]}
        elif k == 'glass':
            stops = {'t': [(0, 1.18), (.5, 1.02), (1, .92)], 'l': [(0, .95), (1, .78)], 'r': [(0, 1.05), (1, .85)], 'w': [(0, .8), (1, .6)]}
        elif k == 'silicon':
            stops = {'t': [(0, 1.3), (.45, 1.05), (1, .9)], 'l': [(0, .78), (1, .52)], 'r': [(0, 1.0), (1, .68)], 'w': [(0, .62), (1, .42)]}
        else:
            stops = {'t': [(0, 1.2), (1, .92)], 'l': [(0, .75), (1, .55)], 'r': [(0, .95), (1, .7)], 'w': [(0, .6), (1, .42)]}
        for face, st in stops.items():
            x2, y2 = ('1', '1') if face == 't' else ('0', '1')
            s = ''.join(f'<stop offset="{o}" stop-color="{shade(b, f)}"/>' for o, f in st)
            out.append(f'<linearGradient id="{PFX}g_{name}_{face}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>')
    return ''.join(out)

def face(pts, mat, which, sw=None):
    m = MAT[mat]
    if MODE == 'flat':
        return f'<polygon points="{fmt(pts)}" fill="{shade(m["flat"], FLAT_F[which])}" stroke="{INK}" stroke-width="{sw or 1.2}" stroke-linejoin="round"/>'
    op = ' fill-opacity="0.82"' if m['kind'] == 'glass' else ''
    return (f'<polygon points="{fmt(pts)}" fill="url(#{PFX}g_{mat}_{which})"{op} stroke="{shade(m["real"], .45)}" '
            f'stroke-width="{sw or .7}" stroke-linejoin="round"/>')

def edge_hi(a, b, strength=.55):
    """real 模式：沿一條邊畫白色高光"""
    if MODE == 'flat': return ''
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ffffff" stroke-opacity="{strength}" stroke-width="1.1"/>'

def shadow(x, y, z, dx, dy, op=.42, blur='blur8', inset=0):
    """real 模式：把 footprint 投到 z 高度的平面，當作下方零件上的陰影"""
    if MODE == 'flat': return ''
    pts = [P(x+inset, y+inset, z), P(x+dx-inset, y+inset, z), P(x+dx-inset, y+dy-inset, z), P(x+inset, y+dy-inset, z)]
    return f'<polygon points="{fmt(pts)}" fill="#000" fill-opacity="{op}" filter="url(#{PFX}{blur})"/>'

def box(x, y, z, dx, dy, dz, mat, sw=None, hi=True):
    t = [P(x, y, z+dz), P(x+dx, y, z+dz), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    l = [P(x, y+dy, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    r = [P(x+dx, y, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x+dx, y, z+dz)]
    out = face(l, mat, 'l', sw) + face(r, mat, 'r', sw) + face(t, mat, 't', sw)
    if hi:
        out += edge_hi((x, y+dy, z+dz), (x+dx, y+dy, z+dz)) + edge_hi((x+dx, y, z+dz), (x+dx, y+dy, z+dz), .4)
    return out

def frame(x, y, z, dx, dy, dz, ix, iy, idx, idy, mat, sw=None):
    """有方形開口的框：外框 x..x+dx / y..y+dy，內孔 ix..ix+idx / iy..iy+idy"""
    out = ''
    wx = [P(ix, iy, z), P(ix, iy+idy, z), P(ix, iy+idy, z+dz), P(ix, iy, z+dz)]
    wy = [P(ix, iy, z), P(ix+idx, iy, z), P(ix+idx, iy, z+dz), P(ix, iy, z+dz)]
    out += face(wx, mat, 'w', sw) + face(wy, mat, 'w', sw)
    l = [P(x, y+dy, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    r = [P(x+dx, y, z), P(x+dx, y+dy, z), P(x+dx, y+dy, z+dz), P(x+dx, y, z+dz)]
    out += face(l, mat, 'l', sw) + face(r, mat, 'r', sw)
    t_out = [P(x, y, z+dz), P(x+dx, y, z+dz), P(x+dx, y+dy, z+dz), P(x, y+dy, z+dz)]
    t_in = [P(ix, iy, z+dz), P(ix+idx, iy, z+dz), P(ix+idx, iy+idy, z+dz), P(ix, iy+idy, z+dz)]
    m = MAT[mat]
    if MODE == 'flat':
        fill, stroke, w = m['flat'], INK, (sw or 1.2)
    else:
        fill, stroke, w = f'url(#{PFX}g_{mat}_t)', shade(m['real'], .45), (sw or .7)
    out += (f'<path d="M{fmt(t_out)}Z M{fmt(t_in)}Z" fill="{fill}" fill-rule="evenodd" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')
    out += edge_hi((x, y+dy, z+dz), (x+dx, y+dy, z+dz)) + edge_hi((x+dx, y, z+dz), (x+dx, y+dy, z+dz), .4)
    return out

def bevel_box(x, y0, z, dx, yfb, dz, mat):
    """前端切 45° 的方塊：底面前緣在 y=yfb，頂面前緣在 y=yfb-dz；斜面＝反射面"""
    yft = yfb - dz
    t = [P(x, y0, z+dz), P(x+dx, y0, z+dz), P(x+dx, yft, z+dz), P(x, yft, z+dz)]
    r = [P(x+dx, y0, z), P(x+dx, yfb, z), P(x+dx, yft, z+dz), P(x+dx, y0, z+dz)]
    m = [P(x, yft, z+dz), P(x+dx, yft, z+dz), P(x+dx, yfb, z), P(x, yfb, z)]
    if MODE == 'flat':
        mirror = f'<polygon points="{fmt(m)}" fill="#f7ecd2" stroke="#a96812" stroke-width="1.3" stroke-linejoin="round"/>'
    else:
        mirror = f'<polygon points="{fmt(m)}" fill="url(#{PFX}g_mirror)" stroke="#8a6a1c" stroke-width=".7" stroke-linejoin="round"/>'
    return face(r, mat, 'r') + face(t, mat, 't') + mirror + edge_hi((x, yft, z+dz), (x+dx, yft, z+dz), .7)

def ell(cx, cy, z, r, fill, stroke=INK, sw=1, extra=''):
    px, py = P(cx, cy, z)
    return (f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{1.2247*r*SCALE:.1f}" ry="{0.7071*r*SCALE:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def line3(a, b, stroke, sw, extra=''):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def label(x, y, z, s, size=12.5, fill=None, anchor='start', weight='600', dx=0, dy=0):
    fill = fill or ('#5a6273' if MODE == 'flat' else '#d7dde8')
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
# MT 接頭：光纖尾端的插芯＋護套＋光纖帶（往 -y 伸出畫面）
MT_Y0, MT_DY = -122, 30      # 插芯 y -122..-92
MT_X0, MT_DX = FA_X0-2, FA_DX+4
MT_Z0, MT_DZ = FIB_Z-9, 18
BOOT_Y0, BOOT_DY = -150, 28
RIB_Y0, RIB_DY = -215, 66

def build():
    g, lab = [], []
    dark = MODE == 'real'
    # 背景
    if dark:
        g.append(f'<rect x="0" y="0" width="{VW}" height="{VH}" fill="url(#{PFX}bg)"/>')
        g.append(f'<rect x="0" y="0" width="{VW}" height="{VH}" fill="url(#{PFX}grid)"/>')
        cx, cy = P(SDX/2, SDY/2, 120)
        g.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="360" ry="250" fill="url(#{PFX}glow)"/>')
    else:
        g.append(f'<rect x="0" y="0" width="{VW}" height="{VH}" fill="#ffffff"/>')
    # 封裝基板（擬真：加幾條淡金色走線）
    g.append(shadow(-16, -16, 0.2, SDX+32, SDY+32, .5, 'blur12', -10))
    g.append(box(-16, -16, Z_SUB[0], SDX+32, SDY+32, Z_SUB[1]-Z_SUB[0], 'sub'))
    if dark:
        for k in range(5):
            yy = -8 + k*44
            g.append(line3((-10, yy, Z_SUB[1]+.2), (SDX+10, yy, Z_SUB[1]+.2), '#c9a24a', .8, 'stroke-opacity=".35"'))
        for k in range(6):
            xx = -8 + k*52
            g.append(line3((xx, -10, Z_SUB[1]+.2), (xx, SDY+10, Z_SUB[1]+.2), '#c9a24a', .8, 'stroke-opacity=".35"'))
    # 凸塊
    bump_fill = f'url(#{PFX}gold)' if dark else '#e9c96e'
    for i in range(6): g.append(ell(22+i*38, SDY-5, 16, 4, bump_fill, '#a96812', .8))
    for i in range(4): g.append(ell(SDX-5, 20+i*38, 16, 4, bump_fill, '#a96812', .8))
    # PIC ＋ 光柵（綠線）在銅色反射層上 ＋ 波導
    g.append(shadow(0, 0, Z_PIC[0]+.2, SDX, SDY, .35, 'blur8', 6))
    g.append(box(0, 0, Z_PIC[0], SDX, SDY, Z_PIC[1]-Z_PIC[0], 'pic'))
    zt = Z_PIC[1]
    cu = f'url(#{PFX}copper)' if dark else '#d9905a'
    g.append(f'<polygon points="{fmt([P(GX-22, GY-15, zt), P(GX+22, GY-15, zt), P(GX+22, GY+15, zt), P(GX-22, GY+15, zt)])}" fill="{cu}" stroke="#9a5a2a" stroke-width="1"/>')
    gc_col = '#3ddc97' if dark else '#0c7a53'
    for k in range(5):
        yy = GY-10+k*5
        g.append(line3((GX-17, yy, zt+.1), (GX+17, yy, zt+.1), gc_col, 2.2))
    wg = '#7fd3ff' if dark else '#0b5871'
    a, b = P(GX-22, GY, zt+.1), P(30, GY, zt+.1)
    g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{wg}" stroke-width="2" stroke-dasharray="6 4" fill="none"/>')
    for dy_ in (-7, 7):
        a, b = P(30, GY, zt+.1), P(40, GY+dy_, zt+.1)
        g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{wg}" stroke-width="1.6" fill="none"/>')
    # EIC（有開口）
    g.append(shadow(0, 0, Z_PIC[1]+.2, SDX, SDY, .38, 'blur12', 10))
    g.append(frame(0, 0, Z_EIC[0], SDX, SDY, Z_EIC[1]-Z_EIC[0], GX-28, GY-20, 56, 40, 'eic'))
    # Si Carrier ＋ 矽微透鏡
    g.append(shadow(0, 0, Z_EIC[1]+.2, SDX, SDY, .38, 'blur12', 10))
    g.append(box(0, 0, Z_CAR[0], SDX, SDY, Z_CAR[1]-Z_CAR[0], 'car'))
    zc = Z_CAR[1]
    for fx in FX:
        g.append(ell(fx, GY, zc, 6.5, f'url(#{PFX}lens)' if dark else '#f3e3b4', '#a96812', .9))
        g.append(ell(fx, GY, zc, 3.2, '#fff6dc', '#a96812', .6))
    # Receptacle 插座框 ＋ 三個定位孔
    g.append(shadow(RC_X0, RC_Y0, Z_CAR[1]+.2, RC_DX, RC_DY, .35, 'blur8', 2))
    g.append(frame(RC_X0, RC_Y0, Z_REC[0], RC_DX, RC_DY, Z_REC[1]-Z_REC[0], CP_X0+14, CP_Y0+14, CP_DX-28, CP_DY-28, 'rec'))
    for bx, by in BALLS: g.append(ell(bx, by, Z_REC[1], 3.6, '#2d3340' if dark else '#5b6170', '#1b2029', .8))
    # 定位珠（掛在載板下方）＋ Carrier 載板（有開口）＋ 珠頂
    g.append(shadow(CP_X0, CP_Y0, Z_REC[1]+.2, CP_DX, CP_DY, .4, 'blur8', 6))
    for bx, by in BALLS: g.append(ell(bx, by, Z_CPL[0]-5, 5.2, f'url(#{PFX}ball)', '#8a6a1c', .8))
    g.append(frame(CP_X0, CP_Y0, Z_CPL[0], CP_DX, CP_DY, Z_CPL[1]-Z_CPL[0], FA_X0-4, GY-26, FA_DX+8, 52, 'cpl'))
    for bx, by in BALLS: g.append(ell(bx, by, Z_CPL[1], 3.2, f'url(#{PFX}ball)', '#8a6a1c', .7))
    # PMLA 薄片 ＋ 6 顆小透鏡
    g.append(shadow(FA_X0, GY-20, Z_CPL[1]+.2, FA_DX, 40, .35, 'blur6', 2))
    g.append(box(FA_X0, GY-20, Z_PMLA[0], FA_DX, 40, Z_PMLA[1]-Z_PMLA[0], 'pmla'))
    for fx in FX: g.append(ell(fx, GY, Z_PMLA[1], 4.5, f'url(#{PFX}lens)' if dark else '#e9c96e', '#a96812', .8))
    # FA 基板；前端面畫 V 溝剖面與光纖圓
    g.append(shadow(FA_X0, FA_Y0, Z_PMLA[1]+.2, FA_DX, (GY+14)-FA_Y0, .38, 'blur8', 4))
    g.append(box(FA_X0, FA_Y0, Z_FA[0], FA_DX, (GY+14)-FA_Y0, Z_FA[1]-Z_FA[0], 'fa'))
    yf = GY+14
    for fx in FX:
        a, b, c = P(fx-4, yf, Z_FA[1]), P(fx, yf, Z_FA[1]-7), P(fx+4, yf, Z_FA[1])
        g.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{c[0]:.1f} {c[1]:.1f}" fill="none" stroke="#3f3f4c" stroke-width="1"/>')
        px, py = P(fx, yf, Z_FA[1]-3.2)
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.6*SCALE:.1f}" fill="#dceaf1" stroke="#7fa5b8" stroke-width="1"/>')
    for fx in FX:
        for dxx in (-3.6, 3.6):
            g.append(line3((fx+dxx, FA_Y0, Z_FA[1]+.1), (fx+dxx, FA_Y0+STRIP, Z_FA[1]+.1), '#8b94a3', .9))
    # 光纖：從基板露出段躺到 MT 插芯前緣
    for fx in FX:
        a, b = (fx, FA_Y0+STRIP+2, FIB_Z+1), (fx, MT_Y0+MT_DY-2, FIB_Z+1)
        if dark:
            g.append(line3(a, b, '#24394d', 9*SCALE, 'stroke-linecap="round"'))
            g.append(line3(a, b, '#6f98b0', 6.2*SCALE, 'stroke-linecap="round"'))
            g.append(line3(a, b, '#e3f3fb', 1.8*SCALE, 'stroke-linecap="round" stroke-opacity=".9"'))
        else:
            g.append(line3(a, b, '#7fa5b8', 7.5*SCALE, 'stroke-linecap="round"'))
            g.append(line3(a, b, '#dceaf1', 2.4*SCALE, 'stroke-linecap="round"'))
    # 上蓋（玻璃，從露出段之後開始；前端同一個 45° 面）＋ 鏡線
    g.append(bevel_box(FA_X0, FA_Y0+STRIP, Z_LID[0], FA_DX, GY, Z_LID[1]-Z_LID[0], 'lid'))
    g.append(line3((FA_X0, GY, Z_LID[0]+.5), (FA_X0+FA_DX, GY, Z_LID[0]+.5), '#a96812', 1.6, 'stroke-dasharray="3 2"'))
    # MT 接頭：插芯 → 護套 → 光纖帶
    g.append(box(MT_X0, MT_Y0, MT_Z0, MT_DX, MT_DY, MT_DZ, 'mt'))
    g.append(box(MT_X0+10, BOOT_Y0, MT_Z0+3, MT_DX-20, BOOT_DY, MT_DZ-6, 'boot'))
    g.append(box(MT_X0+16, RIB_Y0, FIB_Z-2, MT_DX-32, RIB_DY, 4, 'rib', hi=False))
    # 光路：沿第 3 根光纖 → 反射面 → 垂直往下 → 光柵
    bx = FX[2]
    pts = [(bx, MT_Y0+MT_DY, FIB_Z+1), (bx, GY, FIB_Z+1), (bx, GY, Z_PIC[1])]
    d = 'M' + ' L'.join(f'{P(*p)[0]:.1f} {P(*p)[1]:.1f}' for p in pts)
    beam = '#4fd1ff' if dark else '#0e6e8c'
    if dark:
        g.append(f'<path d="{d}" fill="none" stroke="{beam}" stroke-width="7" stroke-opacity=".28" filter="url(#{PFX}blur4)"/>')
    g.append(f'<path id="{PFX}ca_beam" d="{d}" fill="none" stroke="{beam}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    a1, a2 = P(bx+7, GY+7, Z_PIC[1]-6), P(bx+7, GY+7, Z_PIC[1]+12)
    g.append(f'<path d="M{a1[0]:.1f} {a1[1]:.1f} L{a2[0]:.1f} {a2[1]:.1f}" stroke="#ff6b5c" stroke-width="1.6" marker-end="url(#{PFX}arr)"/>')
    dot = '#ff6b5c' if dark else '#b3362c'
    g.append(f'<circle r="3.8" fill="{dot}"><animateMotion dur="4s" repeatCount="indefinite"><mpath href="#{PFX}ca_beam"/></animateMotion></circle>')
    # 標籤：右側一排＋引線（螢幕座標固定 x）
    TX = 650
    tcol = '#5a6273' if not dark else '#d7dde8'
    lcol = '#9aa3b2' if not dark else '#8d98aa'
    def lead(pt, s, sy, size=12.5, fill=None, weight='600'):
        px, py = P(*pt)
        return (f'<path d="M{TX-8:.0f} {sy-4:.0f} L{px:.1f} {py:.1f}" stroke="{lcol}" stroke-width="1" fill="none"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="{lcol}"/>'
                f'<text x="{TX}" y="{sy}" font-size="{size}" fill="{fill or tcol}" font-weight="{weight}">{s}</text>')
    lab.append(lead((MT_X0+MT_DX, MT_Y0+8, MT_Z0+MT_DZ/2), 'MT 接頭（多芯一次插）', 212))
    lab.append(lead((FA_X0+FA_DX, FA_Y0+STRIP+34, Z_LID[0]+12), 'FAU（FA＋反射面＋PMLA）', 250, 13, (INK if not dark else '#ffffff'), '800'))
    lab.append(lead((FA_X0+FA_DX, GY-6, Z_PMLA[1]), 'PMLA 平面微透鏡陣列', 296))
    lab.append(lead((CP_X0+CP_DX, CP_Y0+40, Z_CPL[1]), 'Carrier 定位載板（3 珠 3 孔）', 330))
    lab.append(lead((RC_X0+RC_DX, RC_Y0+30, Z_REC[1]), 'Receptacle 插座（固定在晶片上）', 364))
    lab.append(lead((SDX, 30, Z_CAR[0]+13), 'Si Carrier 矽載板（頂面有微透鏡）', 430))
    lab.append(lead((SDX, 30, Z_EIC[0]+10), 'EIC 電晶片（留開口讓光過）', 510))
    lab.append(lead((SDX, 30, Z_PIC[0]+13), 'PIC 矽光子晶片（光柵在上、銅反射層在下）', 590))
    lab.append(label(-16, SDY+16, Z_SUB[0]+6, '封裝基板', anchor='end', dx=-8, dy=4))
    lab.append(label(-5, GY-8, Z_PIC[1], '光往晶片內的波導走', anchor='end', dx=-6, dy=2, size=12.5))
    return ''.join(g), ''.join(lab)

def defs():
    d = [f'<radialGradient id="{PFX}ball" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#fff6dc"/><stop offset="1" stop-color="#c9a24a"/></radialGradient>',
         f'<marker id="{PFX}arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#ff6b5c"/></marker>']
    if MODE == 'real':
        d.append(grad_defs())
        d.append(f'<linearGradient id="{PFX}bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c1322"/><stop offset=".55" stop-color="#121d31"/><stop offset="1" stop-color="#0a1a1f"/></linearGradient>')
        d.append(f'<pattern id="{PFX}grid" width="46" height="46" patternUnits="userSpaceOnUse"><path d="M46 0 H0 V46" fill="none" stroke="#7fb6ff" stroke-opacity=".07" stroke-width="1"/></pattern>')
        d.append(f'<radialGradient id="{PFX}glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#2d7bd1" stop-opacity=".35"/><stop offset="1" stop-color="#2d7bd1" stop-opacity="0"/></radialGradient>')
        d.append(f'<linearGradient id="{PFX}mirror" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7ecd2"/><stop offset=".45" stop-color="#ffffff"/><stop offset=".6" stop-color="#e9c96e"/><stop offset="1" stop-color="#a97a2a"/></linearGradient>')
        d.append(f'<linearGradient id="{PFX}copper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f0b27a"/><stop offset=".5" stop-color="#c9793f"/><stop offset="1" stop-color="#8c4f24"/></linearGradient>')
        d.append(f'<radialGradient id="{PFX}gold" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#fff3c4"/><stop offset="1" stop-color="#b8892a"/></radialGradient>')
        d.append(f'<radialGradient id="{PFX}lens" cx="40%" cy="35%" r="65%"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#f3e3b4"/><stop offset="1" stop-color="#c9a24a"/></radialGradient>')
        for n, sd in (('blur4', 4), ('blur6', 6), ('blur8', 8), ('blur12', 12)):
            d.append(f'<filter id="{PFX}{n}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return '<defs>' + ''.join(d) + '</defs>'

PINS = [
    (1, 'FAU', (FA_X0+FA_DX/2, FA_Y0+STRIP+30, Z_LID[1])),
    (2, '光纖', (FX[1], -62, FIB_Z)),
    (3, '反射面', (FA_X0+FA_DX/2, GY+2, Z_LID[0]+4)),
    (4, 'V 溝', (FX[0]-8, FA_Y0+4, Z_FA[1])),
    (5, 'PMLA', (FA_X0+6, GY+12, Z_PMLA[1])),
    (6, 'Carrier', (CP_X0+CP_DX-9, CP_Y0+CP_DY-16, Z_CPL[1])),
    (7, 'Receptacle', (RC_X0+RC_DX-8, RC_Y0+60, Z_REC[1])),
    (8, '微透鏡', (GX+34, GY-14, Z_CAR[1])),
    (9, '堆疊', (SDX-26, SDY-22, Z_EIC[1])),
    (10, 'MT', (MT_X0+MT_DX/2+6, MT_Y0+10, MT_Z0+MT_DZ)),
]

def render(mode, fit=True):
    """fit=True 時用這個模式的幾何算置中偏移；兩種風格要共用同一個偏移（紅點才會一樣），所以只在 flat 算一次"""
    global MODE, PFX, OX, OY
    MODE, PFX = mode, ('f' if mode == 'flat' else 'r')
    minx = maxx = miny = maxy = 0
    if fit:
        OX = OY = 0.0
        body, labels = build()
        xs, ys = [], []
        for m in re.finditer(r'(-?\d+\.\d)[, ](-?\d+\.\d)', body):
            xs.append(float(m.group(1))); ys.append(float(m.group(2)))
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        OX = (VW - (maxx-minx))/2 - minx - 42   # 光纖帶會伸出右上角，左邊要留給兩個標籤
        OY = (VH - (maxy-miny))/2 - miny + 22
    body, labels = build()
    dark = mode == 'real'
    tcol = '#8b94a3' if not dark else '#9aa6ba'
    title = (f'<text x="26" y="34" font-size="15.5" letter-spacing="2" fill="{tcol}" font-weight="700">台積電 COUPE-GC 光引擎與 FAU 的耦光結構</text>'
             f'<text x="{VW-26}" y="{VH-22}" text-anchor="end" font-size="15" fill="{tcol}">等角分解示意：零件照實際順序、不照比例</text>')
    svg = (f'<svg viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" font-family="\'Noto Sans TC\',\'Microsoft JhengHei\',sans-serif">\n'
           f'  {defs()}\n  {body}\n  {title}\n  {labels}\n</svg>')
    pin_html = []
    for n, name, p in PINS:
        px, py = P(*p)
        pin_html.append(f'<span class="pin" data-a="{n}" style="left:{px/VW*100:.0f}%;top:{py/VH*100:.0f}%">{n}</span>')
    print(mode, 'bbox', round(minx), round(maxx), round(miny), round(maxy), 'offset', round(OX), round(OY))
    return svg, pin_html

def main():
    out = {}
    for mode in ('flat', 'real'):
        svg, pins = render(mode, fit=(mode == 'flat'))
        out[mode] = (svg, pins)
        with open(os.path.join(HERE, f'new-{mode}.svg'), 'w', encoding='utf-8') as f: f.write(svg)
    assert out['flat'][1] == out['real'][1], 'pins differ between styles'
    with open(os.path.join(HERE, 'new-pins.html'), 'w', encoding='utf-8') as f: f.write('\n'.join(out['flat'][1]))
    css = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}.img-in{position:relative;width:900px}.img-in>svg{display:block;width:100%;height:auto}'
           '.pin{position:absolute;width:28px;height:28px;margin:-14px 0 0 -14px;border-radius:50%;background:#b3362c;color:#fff;border:2px solid #fff;font-size:13px;font-weight:800;display:flex;align-items:center;justify-content:center}')
    for mode in ('flat', 'real'):
        with open(os.path.join(HERE, f'preview-{mode}.html'), 'w', encoding='utf-8') as f:
            f.write(css + '</style><div class="img-in">' + out[mode][0] + '\n' + '\n'.join(out[mode][1]) + '</div>')

main()

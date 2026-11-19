# 第 06 章「NPO 模組的四種做法」那張 2x2 示意圖
# python gen.py          只輸出 npo4.svg
# python gen.py --apply  再把圖塞進 CPO.html 的 npo4-start ~ npo4-end 之間, 並複製成 index.html
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
W, H = 900, 600
PW, PH = 390, 226
INK, TEAL, RED, PURPLE, GREY, MUT = '#1c1f26', '#0e6e8c', '#b3362c', '#7a5cb8', '#8b94a3', '#5d6675'
LASER, DKRED = '#c9483d', '#8f2a22'


def t(x, y, s, size=11, fill=INK, anchor='', bold=False):
    a = f' text-anchor="{anchor}"' if anchor else ''
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}"{a} font-size="{size}"{b} fill="{fill}">{s}</text>'


def dot(path, fill, dur, r=2.6):
    return (f'<circle r="{r}" fill="{fill}"><animateMotion dur="{dur}s" '
            f'repeatCount="indefinite" path="{path}"/></circle>')


def panel(px, py, no, title, tag, ext_laser, sep_pd):
    o = [f'<!-- {no} {title} -->']
    o.append(f'<rect x="{px}" y="{py}" width="{PW}" height="{PH}" fill="#fcfbf8" stroke="#d3ccbc" stroke-width="1"/>')
    o.append(f'<circle cx="{px+22}" cy="{py+24}" r="11" fill="{INK}"/>')
    o.append(t(px+22, py+28, no, 11.5, '#ffffff', 'middle', True))
    o.append(t(px+40, py+29, title, 13.5, INK, '', True))
    o.append(t(px+378, py+29, tag, 11.5, MUT, 'end'))

    # 模組基板
    o.append(t(px+22, py+56, '光引擎模組的基板', 11, GREY))
    o.append(f'<rect x="{px+22}" y="{py+62}" width="196" height="118" rx="3" fill="#efece3" stroke="#9d9483" stroke-width="1.2"/>')

    # 電晶片
    for yy, name in ((84, 'Driver'), (130, 'TIA')):
        o.append(f'<rect x="{px+34}" y="{py+yy}" width="48" height="30" rx="2" fill="{INK}"/>')
        o.append(t(px+58, py+yy+19, name, 11, '#ffffff', 'middle', True))

    # 矽光晶片
    o.append(f'<rect x="{px+98}" y="{py+88}" width="86" height="76" rx="2" fill="{TEAL}"/>')
    o.append(t(px+141, py+110, '矽光晶片', 12, '#ffffff', 'middle', True))
    o.append(t(px+141, py+125, '調變器、波導', 10.5, '#cfe6ee', 'middle'))
    # 電的連線用灰色, 免得跟雷射的紅色搞混
    o.append(f'<line x1="{px+82}" y1="{py+99}" x2="{px+98}" y2="{py+99}" stroke="{MUT}" stroke-width="2"/>')

    # 光偵測器: 做進矽光晶片, 或另外貼一顆
    if sep_pd:
        o.append(f'<line x1="{px+82}" y1="{py+145}" x2="{px+90}" y2="{py+145}" stroke="{MUT}" stroke-width="2"/>')
        o.append(f'<rect x="{px+90}" y="{py+133}" width="34" height="24" rx="2" fill="{PURPLE}" stroke="#ffffff" stroke-width="1.5"/>')
        o.append(t(px+107, py+149, 'PD', 11, '#ffffff', 'middle', True))
    else:
        o.append(f'<rect x="{px+104}" y="{py+134}" width="44" height="22" rx="2" fill="#ffffff"/>')
        o.append(t(px+126, py+149, '鍺 PD', 11, TEAL, 'middle', True))
        o.append(f'<line x1="{px+82}" y1="{py+145}" x2="{px+104}" y2="{py+145}" stroke="{MUT}" stroke-width="2"/>')

    # FAU 與訊號光纖
    o.append(t(px+194, py+90, 'FAU', 10.5, TEAL, 'middle'))
    o.append(f'<rect x="{px+184}" y="{py+96}" width="20" height="44" fill="#dff0f5" stroke="{TEAL}" stroke-width="1.2"/>')
    o.append(t(px+262, py+102, '訊號光纖（收、發）', 11, TEAL, 'middle'))
    o.append(t(px+322, py+56, '機箱面板', 10.5, GREY, 'middle'))
    o.append(f'<line x1="{px+322}" y1="{py+62}" x2="{px+322}" y2="{py+196}" stroke="#d3ccbc" stroke-width="1.2" stroke-dasharray="4 3"/>')
    for yy in (110, 126):
        o.append(f'<line x1="{px+204}" y1="{py+yy}" x2="{px+318}" y2="{py+yy}" stroke="{TEAL}" stroke-width="1.6"/>')
        o.append(f'<circle cx="{px+322}" cy="{py+yy}" r="4" fill="#ffffff" stroke="{TEAL}" stroke-width="1.6"/>')
    o.append(dot(f'M{px+204},{py+110} L{px+318},{py+110}', TEAL, 2))
    o.append(dot(f'M{px+318},{py+126} L{px+204},{py+126}', TEAL, 2))

    # 雷射: 外置 ELSFP, 或貼在模組裡
    if ext_laser:
        pmf = f'M{px+300},{py+167} L{px+230},{py+167} L{px+214},{py+152} L{px+184},{py+152}'
        o.append(f'<path d="{pmf}" fill="none" stroke="{LASER}" stroke-width="1.8"/>')
        o.append(f'<rect x="{px+300}" y="{py+150}" width="74" height="34" rx="3" fill="#fbeeec" stroke="{RED}" stroke-width="1.3"/>')
        o.append(t(px+337, py+165, 'ELSFP', 11.5, DKRED, 'middle', True))
        o.append(t(px+337, py+178, '雷射模組', 10.5, DKRED, 'middle'))
        o.append(t(px+267, py+161, '保偏光纖', 11, DKRED, 'middle'))
        o.append(dot(pmf, LASER, 2.2, 2.8))
        foot = '接出的光纖：訊號＋光源　　雷射壞了：換面板上的 ELSFP'
    else:
        o.append(f'<rect x="{px+112}" y="{py+68}" width="58" height="18" rx="2" fill="{RED}"/>')
        o.append(t(px+141, py+81, '雷射晶片', 10.5, '#ffffff', 'middle', True))
        o.append(dot(f'M{px+141},{py+84} L{px+141},{py+100}', '#ffd9a8', 1.2, 2.4))
        o.append(f'<rect x="{px+300}" y="{py+150}" width="74" height="34" rx="3" fill="none" stroke="#d3ccbc" stroke-width="1.2" stroke-dasharray="4 3"/>')
        o.append(t(px+337, py+171, '不用外置雷射', 10.5, GREY, 'middle'))
        foot = '接出的光纖：只有訊號　　雷射壞了：換整顆模組'
    o.append(t(px+22, py+214, foot, 11.5, MUT))
    return '\n'.join(o)


def build():
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="NPO 光引擎模組的四種做法" '
         'font-family="\'Noto Sans TC\',\'Microsoft JhengHei\',sans-serif">']
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
    o.append(f'<text x="450" y="30" text-anchor="middle" font-family="Georgia,\'PMingLiU\',serif" '
             f'font-size="16" font-weight="bold" fill="{INK}">NPO 光引擎模組的四種做法</text>')
    o.append(t(450, 50, '兩個選擇：雷射放模組外面或裡面；光偵測器（PD）做進矽光晶片或另外貼一顆。模組都插在 ASIC 旁的插座上',
               11.5, GREY, 'middle'))
    o.append(t(295, 78, 'PD 做進矽光晶片（鍺 PD）', 13, TEAL, 'middle', True))
    o.append(t(695, 78, 'PD 另外貼一顆（三五族）', 13, '#5e46a0', 'middle', True))

    for cy, a, b, c, d in ((203, '雷射', '外置', '插在面板的', 'ELSFP'),
                           (443, '雷射', '內建', '晶片貼在', '模組裡')):
        o.append(t(50, cy-13, a, 14, RED, 'middle', True))
        o.append(t(50, cy+6, b, 14, RED, 'middle', True))
        o.append(t(50, cy+27, c, 11, GREY, 'middle'))
        o.append(t(50, cy+42, d, 11, GREY, 'middle'))

    o.append(panel(100, 90, '1', '外置雷射＋整合 PD', '例：阿里雲 3.2T 矽光版', True, False))
    o.append(panel(500, 90, '2', '外置雷射＋獨立 PD', '高速、長距離設計', True, True))
    o.append(panel(100, 330, '3', '內建雷射＋整合 PD', '模組較大，雷射的熱在模組裡', False, False))
    o.append(panel(500, 330, '4', '內建雷射＋獨立 PD', '晶片最多，較少見', False, True))

    # 圖例
    x = 100
    for col, name in ((TEAL, '光：矽光晶片、訊號光纖'), (INK, '電晶片'), (RED, '雷射（外置時經保偏光纖送光）'), (PURPLE, '獨立 PD')):
        o.append(f'<rect x="{x}" y="571" width="12" height="12" fill="{col}"/>')
        o.append(t(x+18, 582, name, 11.5, MUT))
        x += 18 + int(len(name) * 11.5) + 26
    o.append(t(890, 582, '示意圖，非實際比例與擺放位置', 11, GREY, 'end'))
    o.append('</svg>')
    return '\n'.join(o)


svg = build()
(HERE / 'npo4.svg').write_text(svg, encoding='utf-8', newline='\n')
print('npo4.svg', len(svg))

if '--apply' in sys.argv:
    page = ROOT / 'CPO.html'
    with open(page, encoding='utf-8', newline='') as f:
        s = f.read()
    a, b = '<!-- npo4-start -->', '<!-- npo4-end -->'
    if s.count(a) != 1 or s.count(b) != 1:
        sys.exit('CPO.html 找不到 npo4 標記')
    i, j = s.index(a) + len(a), s.index(b)
    s = s[:i] + '\r\n' + svg.replace('\n', '\r\n') + '\r\n' + s[j:]
    with open(page, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    shutil.copyfile(page, ROOT / 'index.html')
    print('已套進 CPO.html 並複製成 index.html')

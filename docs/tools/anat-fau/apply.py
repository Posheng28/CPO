# 把 gen.py 產的 new-real.svg ＋ new-pins.html ＋ 說明列換進 CPO.html 的 #anatB 區塊，
# 並把 glassbridge.svg 插在第 03 章「Edge vs Grating」小圖後面；同步 index.html（保留 CRLF）。可重跑。
# 用法：先跑 gen.py，再 PYTHONUTF8=1 python apply.py；說明列文字就在下面的 legend 清單裡改。
import io, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, 'CPO.html')):
    ROOT = os.path.dirname(ROOT)
src = io.open(os.path.join(ROOT, 'CPO.html'), encoding='utf-8', newline='').read()
assert '\r\n' in src, 'expect CRLF'

def rd(name): return io.open(os.path.join(HERE, name), encoding='utf-8').read().strip()
svg = rd('new-real.svg')
pins = rd('new-pins.html').split('\n')
gb = rd('glassbridge.svg')

legend = [
    ('FAU 光纖陣列單元', '把多根光纖排整齊、固定、對準晶片的整個模組。大立光的做法：自己做 FA（光纖＋V 溝基板），買進 PMLA 微透鏡陣列與反射稜鏡，組成 FAU；客戶要求連底下的定位載板一起裝好再交貨。上詮、波若威、合聖做的也是這一塊'),
    ('光纖束', '單模光纖，芯只有 9 µm，間距 127 或 250 µm；對位誤差超過幾微米光就漏掉。2027 年量產是單排，多排（二維）要到 2028 年'),
    ('45° 反射面', '光沿著躺平的光纖進來，在這裡轉 90° 往下打進晶片。台積電的專利是把鏡面直接做在 FAU 裡；大立光這一代用外購的稜鏡'),
    ('V 溝基板', '玻璃或矽上蝕刻的 V 型溝，光纖躺進去就定位，上面再蓋一片玻璃、灌膠固化。V 溝外購、供應商多；大立光靠自製的主動對位設備把 V 溝的誤差吸收掉'),
    ('PMLA 平面微透鏡陣列', 'FAU 這一側的透鏡，把晶片送上來約 70 µm 寬的準直光束聚回光纖 9 µm 的模場。大立光外購，客戶認證的是半導體石英玻璃版本；合聖改用超穎透鏡做同一層'),
    ('Carrier 定位載板', '帶 3 顆定位珠、3 個定位孔的板子。FAU 先精準貼在載板上，載板再插進插座，珠對孔一放就準。這是大立光法說的說法；客戶要求連這塊一起做好，載板本身外購'),
    ('Receptacle 插座', '固定在光引擎表面的座子，讓 FAU 可以插上、拔下、換新。Senko、康寧的可拆方案都是把座子黏在晶片上；台積電 COUPE 3.0 的可拆光學插座預計 2027 年第一季'),
    ('Si 微透鏡', '刻在矽載板頂面、正對光柵的矽透鏡，晶片這一側的透鏡。把光束放大，對位容差從 ±0.5 µm 放寬到 ±10 µm、損耗 0.3 到 0.5 dB。這是台積電做在晶圓上的，不是 FAU 廠做的'),
    ('COUPE 晶片堆疊', '由下往上：封裝基板、PIC 矽光子晶片（表面有光柵耦合器 GC，正下方一層銅反射鏡把往下漏的光彈回來）、EIC 電晶片用 SoIC 疊上去（光柵正上方留開口）、Si 矽載板蓋在最上面。光從上面垂直進出，這就是 GC 光柵耦合；EC 邊緣耦合則從晶片側面進光'),
    ('MT 接頭', 'FAU 尾端的光纖收成一條光纖帶，末端是 MT 插芯，多芯一次插上機內光纖、再走到前面板。上詮的 FAU 就是 MT 接頭、FA、透鏡三段；嘉基、Senko 做這類小型高密度接頭'),
]
assert len(legend) == 10 and len(pins) == 10

lines = []
lines.append('  <div class="anat rv" id="anatB">')
lines.append('    <div class="img-side"><div class="img-in">')
for l in svg.split('\n'):
    lines.append('      ' + l.strip() if l.strip() else '')
for p in pins:
    lines.append('      ' + p.strip())
lines.append('    </div></div>')
lines.append('    <div class="leg">')
lines.append('      <div class="lg-h">點零件看說明</div>')
for i, (t, d) in enumerate(legend, 1):
    lines.append(f'      <div class="lg" data-a="{i}"><span class="n">{i}</span><div><div class="t">{t}</div><div class="d">{d}</div></div></div>')
lines.append('    </div>')
lines.append('  </div>')
new_block = '\r\n'.join(lines)

start = src.index('  <div class="anat rv" id="anatB">')
end_marker = '  <div class="callout rv pts"><span class="cl-k">對位方式決定量產成本</span>'
end = src.index(end_marker, start)
out = src[:start] + new_block + '\r\n\r\n' + src[end:]

# 導語（把舊版本都換成現在這句）
old_ledes = ['這就是上面那張圖的 3D 版——<b>FAU 怎麼騎在光引擎上、光在哪裡轉彎</b>。點紅點看每個零件。',
             '這是上面那張圖的立體分解版：<b>FAU 怎麼接到光引擎上、光在哪裡轉彎、零件由下往上的順序</b>。點紅點看每個零件；上方可切換平面分解圖與擬真渲染兩種畫法。']
new_lede = '這是上面那張圖的立體分解版：<b>FAU 怎麼接到光引擎上、光在哪裡轉彎、零件由下往上的順序</b>。點紅點看每個零件。'
for ol in old_ledes:
    if out.count(ol) == 1: out = out.replace(ol, new_lede)
assert out.count(new_lede) == 1, 'lede missing'

# Glass Bridge 小圖：插在「Edge vs Grating」svgbox 之後（用註解當標記，可重跑）
GB_S, GB_E = '  <!-- gb-start -->', '  <!-- gb-end -->'
gb_block = GB_S + '\r\n  <div class="svgbox rv">\r\n' + '\r\n'.join('  ' + l if l.strip() else '' for l in gb.split('\n')) + '\r\n  </div>\r\n' + GB_E
if GB_S in out:
    a = out.index(GB_S); b = out.index(GB_E) + len(GB_E)
    out = out[:a] + gb_block + out[b:]
else:
    anchor = out.index('aria-label="Edge vs Grating 耦光對比"')
    close = out.index('  </svg>\r\n  </div>\r\n', anchor) + len('  </svg>\r\n  </div>\r\n')
    out = out[:close] + '\r\n' + gb_block + '\r\n' + out[close:]

io.open(os.path.join(ROOT, 'CPO.html'), 'w', encoding='utf-8', newline='').write(out)
shutil.copyfile(os.path.join(ROOT, 'CPO.html'), os.path.join(ROOT, 'index.html'))
print('block lines', new_block.count('\r\n') + 1, '| total lines', out.count('\r\n'), '| crlf-only:', '\n' not in out.replace('\r\n', ''))

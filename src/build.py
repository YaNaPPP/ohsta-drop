import base64, io
from PIL import Image
def uri(path, fmt=None, q=88):
    if fmt=='webp':
        b=io.BytesIO(); Image.open(path).save(b,'WEBP',quality=q,method=6); data=b.getvalue(); m='image/webp'
    else:
        data=open(path,'rb').read(); m='image/jpeg' if path.endswith('.jpg') else 'image/png'
    return 'data:%s;base64,%s'%(m,base64.b64encode(data).decode())
s=open('template.html').read()
rep={'__GUY__':uri('guy.png','webp'),'__DRIP__':uri('drip.png'),'__GLOW__':uri('glow.png'),'__ELL__':uri('blob.png'),
'__RING__':uri('ring.png'),'__LSPRAY__':uri('logo-spray.png'),'__LSPRAYTOP__':uri('logo-spray-top.png'),
'__CLEAN__':uri('build/clean.jpg'),'__PAINTED__':uri('photo.png','webp',92),'__MAP__':uri('build/map.png'),
'__STROKES__':open('build/strokes.json').read(),'__MSTROKES__':open('mob/strokes.json').read(),
'__MCLEAN__':uri('mob/clean.jpg'),'__MPAINTED__':uri('mob/photo.png','webp',90),'__MMAP__':uri('mob/map.png'),'__MGUY__':uri('mob/guy.png','webp'),'__WALLMASK__':uri('wallmask.png'),'__VOUT__':open('outline/vid.json').read(),'__MOUT__':open('outline/mob.json').read(),
'__F_MON__':'data:font/woff2;base64,'+base64.b64encode(open('../fonts/mon-black.woff2','rb').read()).decode(),
'__F_BOOK__':'data:font/woff2;base64,'+base64.b64encode(open('../fonts/nm-book.woff2','rb').read()).decode(),
'__F_BOLD__':'data:font/woff2;base64,'+base64.b64encode(open('../fonts/nm-bold.woff2','rb').read()).decode()}
for k,v in sorted(rep.items(), key=lambda kv:-len(kv[0])): s=s.replace(k,v)

# ---- the rest of the landing page: 10 pieces of Drop 010, each breaking one rule of the dress code ----
import hashlib, html as H
PIECES = [
 ('01', 'Tagged Blazer',            'Keep it clean.',        'Grey wool, sprayed by hand on the street. No two tags are alike.',   '390', 'Grey blazer sprayed with blue graffiti lettering', '50% 30%'),
 ('02', 'Laced Spine Blazer',       'Never turn your back.', 'The back is cut open and laced shut with red cord, collar to hem.', '460', 'Black blazer seen from the back, laced up the spine with red cord', '50% 40%'),
 ('03', 'Exposed Seam Jacket',      'Hide the seams.',       'Split down the spine and sewn back together with loose white thread.', '420', 'Pinstripe jacket from the back with a raw white-thread seam down the spine', '50% 30%'),
 ('04', 'Raw Edge Two-Piece',       'Finish what you start.','Every hem left raw, every layer showing. Unfinished on purpose.',   '540', 'Cream suit jacket with raw, frayed edges and layered sleeves', '50% 30%'),
 ('05', 'Post-it Coat',             'Say nothing.',          'Forty handwritten notes stitched onto the back. Read before you hug.', '480', 'Grey coat from the back covered in pink handwritten sticky notes', '50% 35%'),
 ('06', 'Bleeding Bead Blazer',     'No decoration.',        'Red glass beads run down the lapels like fresh paint.',             '520', 'Close-up of a grey blazer lapel with red glass beads running down', '50% 40%'),
 ('07', 'Cross-Stitch Herringbone', 'Stay in line.',         'Red wool cross-stitched straight across the chest in a grid.',       '410', 'Grey herringbone blazer with a red cross-stitched grid on the chest', '50% 30%'),
 ('08', 'Hooked Trousers',          'Sharp crease only.',    'Side seams split open and held together with silver hooks.',        '290', 'Black trousers with split side seams closed by silver hooks', '50% 40%'),
 ('09', 'Tied-Back Jacket',         'Buttons only.',         'The back is split and tied shut three times. Sleeves gathered by hand.', '450', 'Black jacket from the back, split and tied with three black ribbons', '50% 30%'),
 ('10', 'Net Harness Shirt',        'Tie required.',         'A crisp white shirt, locked in a cage of knotted leather.',          '260', 'White shirt worn under a knotted black leather net harness', '50% 35%'),
]
cards = []
for i, (n, name, rule, viol, price, alt, pos) in enumerate(PIECES):
    e = H.escape
    cards.append(f"""        <article class="card{' low' if i % 2 else ''}" data-i="{n}" data-name="{e(name)}">
          <p class="rule"><span class="rn">Rule {n}</span><span class="rt">{e(rule)}<svg class="rstrike" aria-hidden="true"><path/></svg></span></p>
          <a class="ph" href="#drop" data-go="#drop" data-piece="{n}" data-cursor="Reserve" aria-label="Reserve the {e(name)}"><img src="assets/img/piece-{n}.webp" alt="{e(alt)}" style="object-position:{pos}" loading="{'eager' if i < 3 else 'lazy'}" decoding="async"></a>
          <div class="cinfo">
            <h3><span class="cn">{n}</span>{e(name)}</h3>
            <p class="viol">{e(viol)}</p>
            <p class="meta"><span>30 pieces</span><span>€ {price}</span><a class="res" href="#drop" data-go="#drop" data-piece="{n}">Reserve →</a></p>
          </div>
        </article>""")
opts = "\n".join(f'            <option value="{n}">{n} — {H.escape(name)}</option>' for n, name, *_ in PIECES)
land = open('landing.html').read().replace('__CARDS__', "\n".join(cards)).replace('__OPTIONS__', opts)
def v(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()[:8]
css = f'<link rel="stylesheet" href="assets/landing.css?v={v("../assets/landing.css")}">\n'
js = "".join(f'<script src="assets/{p}?v={v("../assets/" + p)}"></script>\n' for p in ['vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', 'landing.js'])
s = s.replace('</style>\n', '</style>\n' + css, 1).replace('<!--LANDING-->', land).replace('<!--LANDING-SCRIPTS-->', js)
open('../index.html', 'w').write(s); print(round(len(s) / 1e6, 2), 'MB')

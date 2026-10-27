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
open('ohsta-hero.html','w').write(s); print(round(len(s)/1e6,2),'MB')

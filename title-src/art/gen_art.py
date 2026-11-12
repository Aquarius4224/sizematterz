import xml.etree.ElementTree as ET, base64, io, json
from PIL import Image
names={'Z – 第二排':'Z2','R – 第二排':'R','E – 第二排':'E2','T2 – 第二排':'T2','T1 – 第二排':'T1','A – 第二排':'A','M – 第二排':'M',
'E – 第一排':'E1','Z – 第一排':'Z1','I – 第一排':'I','S – 第一排':'S','藍色水花':'splashB','右側藍色亮片':'mR2','右側黃色亮片':'mR1',
'右側橘色弧線':'snake','左側黃色亮片':'mL2','左側粉紅亮片':'mL1','粉紅水花':'splashP','字體背板與紫色描邊 (可隱藏)':'back'}
r=ET.parse('stack.xml').getroot(); L=[]
for l in list(r.iter('layer'))[::-1]:
    im=Image.open(l.get('src')).convert('RGBA'); b=io.BytesIO(); im.save(b,'WEBP',quality=88,method=6)
    L.append(dict(id=names[l.get('name')],x=int(l.get('x')),y=int(l.get('y')),w=im.width,h=im.height,src='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()))
pos={d['id']:d for d in L}
holes={}
for k,(cx,cy,rx,ry) in {'I':(77,30,26,11),'T1':(95,35,34,12),'T2':(95,34,31,12)}.items():
    src={'I':'data/layer09.png','T1':'data/layer04.png','T2':'data/layer03.png'}[k]
    im=Image.open(src).convert('RGB'); px=[im.getpixel((cx-rx-6,cy)),im.getpixel((cx+rx+6,cy))]
    col=tuple(sum(p[i] for p in px)//len(px) for i in range(3))
    holes[k]=dict(x=pos[k]['x']+cx,y=pos[k]['y']+cy,rx=rx,ry=ry,col='rgb(%d,%d,%d)'%col)
art=dict(W=1536,H=768,L=L,holes=holes)
open('title_art.js','w').write('const TITLE_ART = '+json.dumps(art,separators=(',',':'))+';\n')
print(len(open('title_art.js').read()), holes)

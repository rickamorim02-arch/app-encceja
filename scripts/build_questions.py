import json,re,subprocess,tempfile,zipfile,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROVAS=[('Linguagens','3 - Linguagens, Códigos e suas Tecnologias.zip'),('Ciências Humanas','1 - Ciências Humanas e suas Tecnologias.zip'),('Ciências da Natureza','2 - Ciências da Natureza e suas Tecnologias.zip'),('Matemática','Matematica_ENCCEJA_PROVAS.zip')]
MATERIAL={'Linguagens':['3 - Linguagens, Códigos e suas Tecnologias.zip'],'Ciências Humanas':['1 - Ciências Humanas e suas Tecnologias.zip'],'Ciências da Natureza':['2 - Ciências da Natureza e suas Tecnologias.zip'],'Matemática':['Matematica_ENCCEJA_INEP_A.zip','Matematica_ENCCEJA_INEP_B.zip']}
def pdftext(data,p):
 p.write_bytes(data);o=p.with_suffix('.txt');subprocess.run(['pdftotext','-layout',str(p),str(o)],check=True,stdout=subprocess.DEVNULL);return o.read_text('utf-8',errors='replace').replace('\x0c','\n')
def year(s):
 m=re.search(r'20(?:18|19|20)',s);return int(m.group()) if m else None
def is_gab(n):return bool(re.search(r'gabar|gab_',n,re.I))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
STOP=set('para pela pelo como mais menos onde quando sobre entre essa esse esta este suas seus uma uns umas que com por dos das nos nas aos nao'.split())
def words(s):return {w for w in re.findall(r'[a-z]{4,}',norm(s)) if w not in STOP}
def gabarito(t):
 d={}
 for line in t.splitlines():
  for n,a in re.findall(r'(?<!\d)(\d{1,3})\s*[-.:)]?\s*([ABCD])(?!\w)',line.upper()):
   if 1<=int(n)<=120:d[int(n)]=a
 return d
def questions(t):
 ms=list(re.finditer(r'(?im)^\s*QUEST[ÃA]O\s+(\d{1,3})\b',t));out=[]
 for i,m in enumerate(ms):
  n=int(m.group(1));b=t[m.end():ms[i+1].start() if i+1<len(ms) else len(t)].strip();am=list(re.finditer(r'(?m)^\s*([ABCD])\s*[).\-–]?\s+',b))
  if len(am)<4:continue
  by={}
  for j,x in enumerate(am):
   end=am[j+1].start() if j+1<len(am) else len(b);by.setdefault(x.group(1),re.sub(r'\s+',' ',b[x.end():end].strip()))
  if set(by)!=set('ABCD'):continue
  en=re.sub(r'\s+',' ',b[:am[0].start()].strip())
  if len(en)>=15:out.append((n,en,[by[x] for x in 'ABCD']))
 return out
def paras(t):return [re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n+',t) if 100<=len(re.sub(r'\s+',' ',p).strip())<=1000]
def comment(q,ps):
 qw=words(q);best='';score=0
 for p in ps:
  s=len(qw&words(p))
  if s>score:score=s;best=p
 if score<2:return 'Gabarito oficial confirmado. Não foi localizado no Material INEP fornecido um trecho com correspondência suficiente para comentário automático sem extrapolação.'
 if len(best)>520:best=best[:517].rsplit(' ',1)[0]+'...'
 return 'Comentário baseado no Material INEP: '+best
allq=[];report=[]
with tempfile.TemporaryDirectory() as d:
 td=Path(d);corpus={}
 for area,zips in MATERIAL.items():
  ps=[]
  for zn in zips:
   with zipfile.ZipFile(ROOT/zn) as z:
    for n in z.namelist():
     nn=norm(n)
     if n.lower().endswith('.pdf') and 'prova' not in nn and 'gabar' not in nn and 'resumo' not in nn and ('material inep' in nn or area=='Matemática'):
      try:ps+=paras(pdftext(z.read(n),td/f'm-{abs(hash((zn,n)))}.pdf'))
      except:pass
  corpus[area]=ps
 for area,zn in PROVAS:
  with zipfile.ZipFile(ROOT/zn) as z:
   names=[n for n in z.namelist() if n.lower().endswith('.pdf') and ('prova' in norm(n) or 'gabar' in norm(n))]
   for y in sorted(set(v for n in names if (v:=year(n)))):
    yn=[n for n in names if year(n)==y];gab={}
    for n in yn:
     if is_gab(n):gab.update(gabarito(pdftext(z.read(n),td/f'g-{abs(hash((area,y,n)))}.pdf')))
    count=0
    for n in [x for x in yn if not is_gab(x)]:
     for num,en,opts in questions(pdftext(z.read(n),td/f'p-{abs(hash((area,y,n)))}.pdf')):
      if num not in gab:continue
      c='ABCD'.index(gab[num]);allq.append({'id':f'inep-{y}-{norm(area).replace(" ","")[:6]}-{num}','a':area,'t':f'ENCCEJA {y} • Questão {num}','q':en,'o':opts,'c':c,'e':comment(en+' '+opts[c],corpus[area]),'source':'INEP','commentSource':'Material INEP','year':y,'number':num});count+=1
    report.append({'area':area,'year':y,'gabaritos':len(gab),'questoes_integradas':count,'trechos_material':len(corpus[area])})
allq=sorted({q['id']:q for q in allq}.values(),key=lambda q:(q['year'],q['a'],q['number']))
(ROOT/'questions-data.js').write_text('window.ENCCEJA_QUESTIONS='+json.dumps(allq,ensure_ascii=False,separators=(',',':'))+';\n','utf-8');(ROOT/'questions-report.json').write_text(json.dumps({'total':len(allq),'por_arquivo':report},ensure_ascii=False,indent=2)+'\n','utf-8')
if not allq:raise RuntimeError('Nenhuma questão oficial validada; nada foi publicado.')
print('OK',len(allq));print(json.dumps(report,ensure_ascii=False))

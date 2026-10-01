import json,re,subprocess,tempfile,zipfile,unicodedata,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROVAS=[('Linguagens','3 - Linguagens, Códigos e suas Tecnologias.zip'),('Ciências Humanas','1 - Ciências Humanas e suas Tecnologias.zip'),('Ciências da Natureza','2 - Ciências da Natureza e suas Tecnologias.zip'),('Matemática','Matematica_ENCCEJA_PROVAS.zip')]
MATERIAL={'Linguagens':['3 - Linguagens, Códigos e suas Tecnologias.zip'],'Ciências Humanas':['1 - Ciências Humanas e suas Tecnologias.zip'],'Ciências da Natureza':['2 - Ciências da Natureza e suas Tecnologias.zip'],'Matemática':['Matematica_ENCCEJA_INEP_A.zip','Matematica_ENCCEJA_INEP_B.zip']}
TARGET=400

def pdftext(data,p):
 p.write_bytes(data);o=p.with_suffix('.txt');subprocess.run(['pdftotext','-layout',str(p),str(o)],check=True,stdout=subprocess.DEVNULL);return o.read_text('utf-8',errors='replace').replace('\x0c','\n')
def year(s):
 m=re.search(r'20(?:18|19|20)',s);return int(m.group()) if m else None
def is_gab(n):return bool(re.search(r'gabar|gab_',n,re.I))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
STOP=set('para pela pelo como mais menos onde quando sobre entre essa esse esta este suas seus uma uns umas que com por dos das nos nas aos nao muito pode podem sendo ainda cada tambem atraves partir forma grande mesmo'.split())
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
def clean_answer(s):
 s=re.sub(r'\s+',' ',s).strip().rstrip('.;');return s[:1].lower()+s[1:] if s else s
def best_sentence(q,ps):
 qw=words(q);best='';score=0
 for p in ps:
  for s in re.split(r'(?<=[.!?])\s+',p):
   s=re.sub(r'\s+',' ',s).strip()
   if not 45<=len(s)<=260:continue
   sc=len(qw&words(s))
   if sc>score:score=sc;best=s
 return best,score
def simplify(s):
 reps=[('a fim de','para'),('com o objetivo de','para'),('em decorrência de','por causa de'),('por meio de','usando'),('efetuar','fazer'),('realizar','fazer'),('utilizar','usar'),('possibilita','permite'),('possibilitam','permitem'),('necessita','precisa'),('necessitam','precisam')]
 for a,b in reps:s=re.sub(r'\b'+re.escape(a)+r'\b',b,s,flags=re.I)
 return re.sub(r'\s+',' ',s).strip()
def comment(q,answer,letter,ps):
 ans=clean_answer(answer);base=f'Resposta certa: {letter}. A ideia principal é {ans}.';sent,score=best_sentence(q+' '+answer,ps)
 if score<2:return base+' O gabarito é oficial do INEP. O material fornecido não trouxe um trecho curto e claro o bastante para explicar mais sem inventar.'
 sent=simplify(sent)
 if len(sent)>220:sent=sent[:217].rsplit(' ',1)[0]+'...'
 return base+' O material do INEP reforça isso: '+sent

def material_sentences(ps):
 out=[];seen=set()
 for p in ps:
  for s in re.split(r'(?<=[.!?])\s+',p):
   s=re.sub(r'\s+',' ',s).strip(' •-')
   if not 70<=len(s)<=230:continue
   if re.search(r'quest[aã]o|gabarito|prova\s+20|resposta correta',norm(s)):continue
   k=norm(s)
   if k in seen:continue
   seen.add(k);out.append(s)
 return out

def study_questions(corpus,needed):
 areas=list(MATERIAL);sentences={a:material_sentences(corpus[a]) for a in areas};candidates=[]
 for area in areas:
  vocab=[]
  for s in sentences[area]:
   vocab += [w for w in re.findall(r'\b[A-Za-zÀ-ÿ]{6,}\b',s) if norm(w) not in STOP]
  vocab=list(dict.fromkeys(vocab))
  for s in sentences[area]:
   terms=[w for w in re.findall(r'\b[A-Za-zÀ-ÿ]{7,}\b',s) if norm(w) not in STOP]
   if not terms:continue
   # termo mais distintivo: maior palavra; a resposta é literalmente recuperável do material.
   answer=sorted(terms,key=lambda x:(len(x),x),reverse=True)[0]
   masked=re.sub(r'\b'+re.escape(answer)+r'\b','____',s,count=1,flags=re.I)
   pool=[w for w in vocab if norm(w)!=norm(answer) and abs(len(w)-len(answer))<=4]
   if len(pool)<3:continue
   h=int(hashlib.sha256((area+s).encode()).hexdigest(),16)
   distract=[]
   for j in range(len(pool)):
    w=pool[(h+j*37)%len(pool)]
    if norm(w) not in {norm(x) for x in distract} and norm(w)!=norm(answer):distract.append(w)
    if len(distract)==3:break
   if len(distract)<3:continue
   opts=distract+[answer];rot=h%4;opts=opts[rot:]+opts[:rot];c=opts.index(answer);letter='ABCD'[c]
   candidates.append({'area':area,'sentence':s,'masked':masked,'opts':opts,'c':c,'letter':letter})
 # distribuição equilibrada por área até atingir o alvo
 selected=[];by={a:[x for x in candidates if x['area']==a] for a in areas};i=0
 while len(selected)<needed and any(i<len(by[a]) for a in areas):
  for a in areas:
   if len(selected)>=needed:break
   if i<len(by[a]):selected.append(by[a][i])
  i+=1
 if len(selected)<needed:raise RuntimeError(f'Material INEP insuficiente para gerar {needed} questões de estudo; somente {len(selected)} elegíveis.')
 out=[]
 for n,x in enumerate(selected,1):
  out.append({'id':f'material-inep-{n:03d}','a':x['area'],'t':f'Material INEP • Estudo {n:03d}','q':'Complete a frase de acordo com o material do INEP: '+x['masked'],'o':x['opts'],'c':x['c'],'e':f'Resposta certa: {x["letter"]}. No material do INEP, a frase aparece assim: {x["sentence"]}','source':'Elaborada do Material INEP','commentSource':'Material INEP','year':None,'number':n})
 return out

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
      letter=gab[num];c='ABCD'.index(letter);allq.append({'id':f'inep-{y}-{norm(area).replace(" ","")[:6]}-{num}','a':area,'t':f'ENCCEJA {y} • Questão {num}','q':en,'o':opts,'c':c,'e':comment(en,opts[c],letter,corpus[area]),'source':'INEP','commentSource':'Material INEP','year':y,'number':num});count+=1
    report.append({'area':area,'year':y,'gabaritos':len(gab),'questoes_integradas':count,'trechos_material':len(corpus[area])})
allq=sorted({q['id']:q for q in allq}.values(),key=lambda q:(q['year'] or 9999,q['a'],q['number']))
official=len(allq);needed=TARGET-official
if needed<0:raise RuntimeError(f'Banco oficial já excede alvo: {official}>{TARGET}')
allq += study_questions(corpus,needed)
if len(allq)!=TARGET:raise RuntimeError(f'Total final inválido: {len(allq)}; esperado {TARGET}')
(ROOT/'questions-data.js').write_text('window.ENCCEJA_QUESTIONS='+json.dumps(allq,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
(ROOT/'questions-report.json').write_text(json.dumps({'total':len(allq),'oficiais_inep':official,'elaboradas_material_inep':needed,'por_arquivo':report},ensure_ascii=False,indent=2)+'\n','utf-8')
print('OK',len(allq),'=',official,'oficiais +',needed,'elaboradas do Material INEP')

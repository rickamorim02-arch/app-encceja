import json,re,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
('Linguagens','3 - Linguagens, Códigos e suas Tecnologias.zip'),
('Ciências Humanas','1 - Ciências Humanas e suas Tecnologias.zip'),
('Ciências da Natureza','2 - Ciências da Natureza e suas Tecnologias.zip'),
('Matemática','Matematica_ENCCEJA_PROVAS.zip')]
def pdftext(data,p):
 p.write_bytes(data); out=p.with_suffix('.txt'); subprocess.run(['pdftotext','-layout',str(p),str(out)],check=True); return out.read_text('utf-8',errors='replace').replace('\x0c','\n')
def year(s):
 m=re.search(r'20(?:18|19|20)',s); return int(m.group()) if m else None
def is_gab(n): return bool(re.search(r'gabar|gab_',n,re.I))
def parse_gabarito(t):
 ans={}
 # aceita linhas/tabelas contendo numero seguido de A-D; evita fabricar respostas
 for line in t.splitlines():
  pairs=re.findall(r'(?<!\d)(\d{1,3})\s*[-.:)]?\s*([ABCD])(?!\w)',line.upper())
  for n,a in pairs:
   n=int(n)
   if 1<=n<=120: ans[n]=a
 return ans
def parse_questions(t):
 # Questões ENCCEJA são delimitadas por 'QUESTÃO N'. Preserva texto extraído; só aceita 4 alternativas A-D.
 ms=list(re.finditer(r'(?im)^\s*QUEST[ÃA]O\s+(\d{1,3})\b',t)); out=[]
 for i,m in enumerate(ms):
  n=int(m.group(1)); block=t[m.end():ms[i+1].start() if i+1<len(ms) else len(t)].strip()
  am=list(re.finditer(r'(?m)^\s*([ABCD])\s*[).\-–]?\s+',block))
  if len(am)<4: continue
  by={}
  for j,x in enumerate(am):
   letter=x.group(1); end=am[j+1].start() if j+1<len(am) else len(block)
   if letter not in by: by[letter]=re.sub(r'\s+',' ',block[x.end():end].strip())
  if set(by)!=set('ABCD'): continue
  en=re.sub(r'\s+',' ',block[:am[0].start()].strip())
  if len(en)<15 or any(len(by[x])<1 for x in 'ABCD'): continue
  out.append((n,en,[by[x] for x in 'ABCD']))
 return out
allq=[]; report=[]
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 for area,zname in SOURCES:
  z=zipfile.ZipFile(ROOT/zname); names=[n for n in z.namelist() if n.lower().endswith('.pdf') and ('prova' in n.lower() or 'gabar' in n.lower())]
  years=sorted(set(y for n in names if (y:=year(n))))
  for y in years:
   yn=[n for n in names if year(n)==y]; gabs={}
   for n in yn:
    if is_gab(n): gabs.update(parse_gabarito(pdftext(z.read(n),td/f'g-{area[:2]}-{y}-{abs(hash(n))}.pdf')))
   provas=[n for n in yn if not is_gab(n)]
   count=0
   for n in provas:
    qs=parse_questions(pdftext(z.read(n),td/f'p-{area[:2]}-{y}-{abs(hash(n))}.pdf'))
    for num,en,opts in qs:
     if num not in gabs: continue
     c='ABCD'.index(gabs[num]); qid=f'inep-{y}-{re.sub("[^a-z]","",area.lower())[:5]}-{num}'
     allq.append({'id':qid,'a':area,'t':f'ENCCEJA {y} • Questão {num}','q':en,'o':opts,'c':c,'e':f'Gabarito oficial INEP: {gabs[num]}.','source':'INEP','year':y,'number':num})
     count+=1
   report.append({'area':area,'year':y,'gabaritos':len(gabs),'questoes_integradas':count})
# deduplica por id sem inventar dados
uniq={q['id']:q for q in allq}; allq=list(uniq.values()); allq.sort(key=lambda q:(q['year'],q['a'],q['number']))
(ROOT/'questions-data.js').write_text('window.ENCCEJA_QUESTIONS='+json.dumps(allq,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
(ROOT/'questions-report.json').write_text(json.dumps({'total':len(allq),'por_arquivo':report},ensure_ascii=False,indent=2)+'\n','utf-8')
if not allq: raise RuntimeError('Nenhuma questão oficial validada; nada foi publicado.')
print('OK questões oficiais validadas:',len(allq)); print(json.dumps(report,ensure_ascii=False))

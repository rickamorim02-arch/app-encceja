# Fonte exclusiva: resumos fornecidos pelo usuário. Não completar lacunas com conteúdo externo.
import json,re,subprocess,tempfile,zipfile,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[('Linguagens, Códigos e suas Tecnologias','3 - Linguagens, Códigos e suas Tecnologias.zip'),('Matemática e suas Tecnologias','Matematica_ENCCEJA_RESUMOS.zip'),('Ciências Humanas e suas Tecnologias','1 - Ciências Humanas e suas Tecnologias.zip'),('Ciências da Natureza e suas Tecnologias','2 - Ciências da Natureza e suas Tecnologias.zip')]
def pdf_text(p):
 out=p.with_suffix('.txt'); subprocess.run(['pdftotext','-layout',str(p),str(out)],check=True); return out.read_text('utf-8',errors='replace')
def clean(t):
 t=t.replace('\x0c','\n'); lines=[re.sub(r'\s+$','',x) for x in t.splitlines()]
 while lines and not lines[0].strip(): lines.pop(0)
 return '\n'.join(lines).strip()
def to_html(t):
 blocks=[]
 for b in re.split(r'\n\s*\n',t):
  b=' '.join(x.strip() for x in b.splitlines() if x.strip())
  if b: blocks.append('<p>'+html.escape(b)+'</p>')
 return ''.join(blocks)
def title(t,n):
 for line in t.splitlines():
  s=line.strip(' •\t-')
  if s and len(s)>8 and not s.lower().startswith(('elabore','resumo')): return s[:120]
 return f'Aula {n:02d}'
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 for idx,(area,zname) in enumerate(SOURCES,1):
  aulas=[]
  with zipfile.ZipFile(ROOT/zname) as z:
   members=[m for m in z.namelist() if not m.endswith('/') and 'resum' in m.lower() and m.lower().endswith('.pdf')]
   if area.startswith('Matemática'): members=[m for m in z.namelist() if not m.endswith('/') and m.lower().endswith('.pdf')]
   for m in members:
    q=re.search(r'Aula\s*(\d+)',m,re.I)
    if not q: continue
    n=int(q.group(1)); p=td/f'{idx}-{n}.pdf'; p.write_bytes(z.read(m)); t=clean(pdf_text(p)); aulas.append({'n':f'Aula {n:02d}','t':title(t,n),'html':to_html(t)})
  if area.startswith('Ciências Humanas'):
   p=ROOT/'Aula 00.PDF'; t=clean(pdf_text(p)); aulas.append({'n':'Aula 00','t':title(t,0),'html':to_html(t)})
  aulas.sort(key=lambda a:int(re.search(r'\d+',a['n']).group())); nums=[int(re.search(r'\d+',a['n']).group()) for a in aulas]
  if nums!=list(range(10)): raise RuntimeError(f'{area}: aulas encontradas {nums}, esperado 0-9')
  data={'nome':area,'aulas':aulas}; (ROOT/f'reading-data-{idx}.js').write_text(f'window.ENCCEJA_READING_PART_{idx}='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
  print(area,len(aulas))
print('OK: 4 áreas, 40 aulas geradas somente a partir dos resumos fornecidos.')

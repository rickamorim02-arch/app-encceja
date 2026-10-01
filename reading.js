(function(){
const MATERIAS=[
 {nome:'Linguagens, Códigos e suas Tecnologias',aulas:[
  {n:'Aula 00',t:'Leitura e interpretação de textos',html:'<h3>Conteúdo da aula</h3><p>Espaço preparado para os resumos de leitura do ENCCEJA. Os conteúdos serão organizados em tópicos, conceitos essenciais e pontos de revisão, seguindo a mesma estrutura de leitura usada no aplicativo SEFAZ-AL.</p>'},
  {n:'Aula 01',t:'Gêneros textuais e comunicação',html:'<h3>Conteúdo da aula</h3><p>Área preparada para receber o conteúdo teórico desta aula.</p>'}
 ]},
 {nome:'Matemática e suas Tecnologias',aulas:[
  {n:'Aula 00',t:'Números e operações',html:'<h3>Conteúdo da aula</h3><p>Área preparada para resumos, conceitos, exemplos e pontos importantes para a prova.</p>'},
  {n:'Aula 01',t:'Razão, proporção e porcentagem',html:'<h3>Conteúdo da aula</h3><p>Área preparada para receber o conteúdo teórico desta aula.</p>'}
 ]},
 {nome:'Ciências Humanas e suas Tecnologias',aulas:[
  {n:'Aula 00',t:'Sociedade, cidadania e cultura',html:'<h3>Conteúdo da aula</h3><p>Área preparada para os conteúdos de História, Geografia, Filosofia e Sociologia relacionados ao ENCCEJA.</p>'}
 ]},
 {nome:'Ciências da Natureza e suas Tecnologias',aulas:[
  {n:'Aula 00',t:'Ciência, ambiente e vida',html:'<h3>Conteúdo da aula</h3><p>Área preparada para os conteúdos de Biologia, Física e Química relacionados ao ENCCEJA.</p>'}
 ]}
];
let flat=[];MATERIAS.forEach((m,mi)=>m.aulas.forEach((a,ai)=>flat.push({m,mi,a,ai})));
function show(mi,ai){const m=MATERIAS[mi],a=m.aulas[ai],v=document.getElementById('readingBody');if(!v)return;v.innerHTML='<div class="card"><small>'+m.nome+' • '+a.n+'</small><h2>'+a.t+'</h2>'+a.html+'</div>';document.querySelectorAll('.readingLesson').forEach(b=>b.classList.remove('on'));const b=document.querySelector('[data-read="'+mi+'-'+ai+'"]');if(b)b.classList.add('on');localStorage.setItem('encceja-reading-last',mi+'-'+ai);window.scrollTo(0,0)}
function init(){if(document.getElementById('reading'))return true;const app=document.querySelector('.app'),nav=app&&app.querySelector('nav');if(!app||!nav)return false;const style=document.createElement('style');style.textContent='.readingLesson{width:100%;padding:12px;margin:6px 0;text-align:left;border:1px solid #24517c;border-radius:12px;background:#07182e;color:#fff}.readingLesson.on{border-color:#ffd52e;box-shadow:0 0 0 1px #ffd52e}.readingText{line-height:1.65}.readingText h3{color:#ffd52e;margin-top:22px}.readingText p{color:#e7eef7}.readingSubject{margin-bottom:10px}.readingSubject summary{cursor:pointer;padding:4px 0}';document.head.appendChild(style);const sec=document.createElement('section');sec.id='reading';sec.className='panel hidden';sec.innerHTML='<h2>📖 Leitura</h2><p>Resumos organizados por matéria e aula.</p><div id="readingSubjects"></div><div id="readingBody" class="readingText"></div>';app.insertBefore(sec,nav);const root=sec.querySelector('#readingSubjects');MATERIAS.forEach((m,mi)=>{const d=document.createElement('details');d.className='card readingSubject';if(mi===0)d.open=true;d.innerHTML='<summary><b>'+m.nome+'</b></summary><div></div>';const list=d.querySelector('div');m.aulas.forEach((a,ai)=>{const b=document.createElement('button');b.className='readingLesson';b.dataset.read=mi+'-'+ai;b.innerHTML='<b>'+a.n+'</b><br><small>'+a.t+'</small>';b.onclick=()=>show(mi,ai);list.appendChild(b)});root.appendChild(d)});const b=document.createElement('button');b.id='nreading';b.innerHTML='📖<br>Leitura';b.onclick=function(){document.querySelectorAll('.app>main,.app>section').forEach(e=>e.classList.add('hidden'));const ff=document.getElementById('feedFilter');if(ff)ff.classList.add('hidden');nav.querySelectorAll('button').forEach(x=>x.classList.remove('on'));sec.classList.remove('hidden');b.classList.add('on');let p=(localStorage.getItem('encceja-reading-last')||'0-0').split('-').map(Number);show(p[0]||0,p[1]||0)};nav.insertBefore(b,nav.lastElementChild);nav.querySelectorAll('button:not(#nreading)').forEach(x=>x.addEventListener('click',()=>sec.classList.add('hidden')));return true}
let n=0,t=setInterval(()=>{n++;if(init()||n>120)clearInterval(t)},50);
})();
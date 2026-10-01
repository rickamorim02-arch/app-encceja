(function(){
  function initEssay(){
    const D=window.ENCCEJA_ESSAY_TOPICS;
    const sec=document.getElementById('essay');
    if(!D||!D.length||!sec)return false;

    let current=parseInt(localStorage.getItem('encceja-redacao-atual')||'0',10);
    if(!Number.isInteger(current)||current<0||current>=D.length)current=0;

    sec.innerHTML=`
      <h2>✍️ Redação</h2>
      <p>Escolha um tema, escreva sua redação e depois consulte o modelo de orientação.</p>
      <div class="card">
        <b>🔎 Escolher tema</b>
        <input id="essaySearch" type="search" placeholder="Pesquisar entre os 100 temas..." autocomplete="off">
        <select id="essaySelect" aria-label="Selecionar tema de redação"></select>
        <button id="essayRandom" type="button" class="primary">🎲 Sortear tema</button>
      </div>
      <div id="essayStatus" class="card"></div>
      <div id="essayPrompt" class="card"></div>
      <textarea id="essayText" rows="14" placeholder="Escreva aqui sua redação..."></textarea>
      <button id="essaySave" type="button" class="primary">💾 Salvar redação</button>
      <button id="essayModelButton" type="button" class="secondary">📘 Mostrar modelo de orientação</button>
      <div id="essayModel" class="card hidden"></div>
      <div id="essayPoints" class="card"></div>`;

    const search=document.getElementById('essaySearch');
    const select=document.getElementById('essaySelect');
    const text=document.getElementById('essayText');
    const status=document.getElementById('essayStatus');
    const prompt=document.getElementById('essayPrompt');
    const model=document.getElementById('essayModel');
    const points=document.getElementById('essayPoints');
    const modelButton=document.getElementById('essayModelButton');

    function fillSelect(filter){
      const f=(filter||'').trim().toLowerCase();
      select.innerHTML='';
      D.forEach((x,i)=>{
        if(f && !x.t.toLowerCase().includes(f))return;
        const o=document.createElement('option');
        o.value=String(i);o.textContent=(i+1)+'. '+x.t;
        select.appendChild(o);
      });
      const wanted=[...select.options].find(o=>Number(o.value)===current);
      if(wanted)select.value=String(current);
      else if(select.options.length)select.selectedIndex=0;
    }

    function openTopic(i,origin){
      i=Number(i);
      if(!Number.isInteger(i)||i<0||i>=D.length)return;
      current=i;
      localStorage.setItem('encceja-redacao-atual',String(i));
      const x=D[i];
      prompt.innerHTML='<b>Tema '+(i+1)+'</b><h3>'+x.t+'</h3><p>'+x.p+'</p>';
      text.value=localStorage.getItem('encceja-redacao-'+(i+1))||'';
      model.innerHTML='<h3>📘 Modelo de orientação</h3><p>'+x.m+'</p>';
      model.classList.add('hidden');
      modelButton.textContent='📘 Mostrar modelo de orientação';
      points.innerHTML='<b>✅ Pontos para autocorreção</b><ul>'+x.k.map(v=>'<li>'+v+'</li>').join('')+'</ul>';
      status.textContent=(origin==='random'?'Tema sorteado: ':'Tema selecionado: ')+(i+1)+'. '+x.t;
      fillSelect(search.value);
      if([...select.options].some(o=>Number(o.value)===i))select.value=String(i);
    }

    search.addEventListener('input',()=>fillSelect(search.value));
    select.addEventListener('change',()=>openTopic(select.value,'manual'));
    select.addEventListener('click',()=>{if(select.value!=='')openTopic(select.value,'manual')});
    document.getElementById('essayRandom').addEventListener('click',()=>{
      let used=[];
      try{used=JSON.parse(localStorage.getItem('encceja-redacao-sorteados')||'[]')}catch(e){used=[]}
      if(!Array.isArray(used)||used.length>=D.length)used=[];
      const pool=D.map((_,i)=>i).filter(i=>!used.includes(i));
      const i=pool[Math.floor(Math.random()*pool.length)];
      used.push(i);localStorage.setItem('encceja-redacao-sorteados',JSON.stringify(used));
      search.value='';fillSelect('');openTopic(i,'random');
    });
    function saveText(){localStorage.setItem('encceja-redacao-'+(current+1),text.value)}
    text.addEventListener('input',saveText);
    document.getElementById('essaySave').addEventListener('click',()=>{saveText();status.textContent='✅ Redação do tema '+(current+1)+' salva neste aparelho.'});
    modelButton.addEventListener('click',()=>{
      const hidden=model.classList.toggle('hidden');
      modelButton.textContent=hidden?'📘 Mostrar modelo de orientação':'📕 Ocultar modelo de orientação';
      if(!hidden)model.scrollIntoView({block:'nearest',behavior:'smooth'});
    });

    fillSelect('');openTopic(current,'manual');
    return true;
  }
  let tries=0;
  const timer=setInterval(()=>{tries++;if(initEssay()||tries>120)clearInterval(timer)},50);
})();

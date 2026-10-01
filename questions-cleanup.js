(function(){
  const qs=window.ENCCEJA_QUESTIONS||[];
  const footer=/\s*(?:\d+\s+)?(?:Ciências da Natureza e suas Tecnologias|Ciências Humanas e suas Tecnologias|Linguagens, Códigos e suas Tecnologias|Matemática e suas Tecnologias)\s*[–-]\s*ENCCEJA\s*20\d{2}(?:\s+\d+)?\s*\*[A-Z0-9]+\*\s*$/i;
  let changed=0;
  qs.forEach(q=>{
    if(!Array.isArray(q.o)) return;
    q.o=q.o.map(v=>{
      const original=String(v);
      const clean=original.replace(footer,'').trim();
      if(clean!==original) changed++;
      return clean;
    });
  });
  window.ENCCEJA_QUESTION_CLEANUP={alternativasCorrigidas:changed};
  if(typeof render==='function') render();
})();

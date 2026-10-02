const CACHE='encceja-offline-v1';
const CORE=['./','./index.html','./manifest.webmanifest','./questions-data.js?v=2','./questions-cleanup.js?v=1','./reading-data-1.js?v=1','./reading-data-2.js?v=1','./reading-data-3.js?v=1','./reading-data-4.js?v=1','./reading.js?v=3','./essay-data.js?v=6','./essay.js?v=4'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(CORE.map(u=>c.add(u)))).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request,{ignoreSearch:false}).then(hit=>{const net=fetch(e.request).then(r=>{if(r&&r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r});return hit||net.catch(()=>caches.match('./index.html'))}))});

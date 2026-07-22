const fs=require('fs'); const path=require('path'); const {JSDOM}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const repertorio=fs.readFileSync(path.join(__dirname,'..','data','repertorio.json'),'utf8');
let blob=null;
let ghPut=null; // registra o corpo do PUT enviado ao GitHub

/* localStorage em memória — simula https / GitHub Pages, onde o navegador grava */
function memLS(){ const m={}; return {
  getItem:k=>(k in m?m[k]:null), setItem:(k,v)=>{m[k]=String(v)},
  removeItem:k=>{delete m[k]}, clear:()=>{for(const k in m)delete m[k]} }; }

/* env base: click/blob stubados, fetch devolve o repertorio.json real */
const baseEnv=extra=>({runScripts:'dangerously',pretendToBeVisual:true,url:'https://x/',
  beforeParse(win){
    win.URL.createObjectURL=b=>{blob=b;return 'blob:x'};
    win.HTMLAnchorElement.prototype.click=function(){};
    win.confirm=()=>true; win.alert=()=>{};
    win.fetch=async(u,opts)=>{
      if(String(u).includes('api.github.com')){
        if(opts&&opts.method==='PUT'){ ghPut=JSON.parse(opts.body); return {ok:true,status:201,json:async()=>({})}; }
        return {ok:true,status:200,json:async()=>({sha:'sha123'})};
      }
      return {ok:true,json:async()=>JSON.parse(repertorio),text:async()=>repertorio};
    };
    if(extra) extra(win);
  }});
const comLS=ls=>baseEnv(win=>Object.defineProperty(win,'localStorage',{configurable:true,get:()=>ls}));
const semLS=()=>baseEnv(win=>Object.defineProperty(win,'localStorage',{configurable:true,
  get(){throw new win.DOMException('insecure','SecurityError')}}));
const offline=ls=>baseEnv(win=>{Object.defineProperty(win,'localStorage',{configurable:true,get:()=>ls});
  win.fetch=async()=>{throw new Error('offline')};});

const tap=(w,e)=>{if(!e)throw new Error('faltou elemento');e.dispatchEvent(new w.MouseEvent('click',{bubbles:true}))};
const ch=(w,n)=>w.document.querySelectorAll('#content .sec .chords')[n].textContent.replace(/\s+/g,' ').trim();
const wait=ms=>new Promise(r=>setTimeout(r,ms));
let pass=true; const ok=(c,m)=>{console.log((c?'  ✅ ':'  ❌ ')+m); if(!c)pass=false;};

(async()=>{
  // ---------- A) editar no app e exportar o repertorio.json oficial ----------
  console.log('A) editar → exportar repertorio.json');
  const ls=memLS();
  const d=new JSDOM(html,comLS(ls)), w=d.window, $=i=>w.document.getElementById(i);
  await wait(40); // deixa o fetch/atualizarDados resolver
  ok(!$('banner').classList.contains('show'),'sem banner quando o localStorage grava');
  ok($('hPos').textContent.split('/')[1]>0,'carregou as músicas do data/repertorio.json (fetch)');

  tap(w,$('bEdit')); tap(w,w.document.querySelectorAll('#content .sec')[0]);
  $('fCh').value='XX · YY'; tap(w,$('secSave'));
  ok(ch(w,0)==='XX · YY','edição da parte aparece na tela');

  tap(w,$('bTools'));
  ok(/1 música/.test($('pubStatus').innerHTML),'status: 1 edição não publicada');

  tap(w,$('bExportJson'));
  const exp=JSON.parse(await blob.text());
  ok(exp.musicas.some(m=>JSON.stringify(m.st).includes('XX · YY')),'export mescla a edição dentro de musicas');
  ok(exp.musicas.some(m=>m.bl),'campo bl preservado no export (bug antigo)');
  ok(exp.musicas.length===JSON.parse(repertorio).musicas.length,'export tem todas as músicas');

  // ---------- B) offline: usa o cache local, sem internet ----------
  console.log('\nB) offline (fetch falha) usa o cache e o rascunho local');
  const d2=new JSDOM(html,offline(ls)), w2=d2.window, $2=i=>w2.document.getElementById(i);
  await wait(40);
  ok($2('hTitle').textContent.length>0,'offline: carrega do cache guardado');
  ok(ch(w2,0)==='XX · YY','offline: rascunho não publicado persiste neste aparelho');
  ok(!$2('banner').classList.contains('show'),'offline com localStorage ok: sem banner');

  // ---------- C) limpar rascunho volta ao oficial ----------
  console.log('\nC) limpar rascunho local');
  const orig=ch(w2,0);
  tap(w2,$2('bTools')); tap(w2,$2('bLimpar'));
  ok(ch(w2,0)!=='XX · YY','após limpar, a parte volta ao repertório oficial');
  ok(/Tudo salvo/.test($2('pubStatus').innerHTML),'status volta a "tudo salvo e publicado"');

  // ---------- D) file:// (localStorage bloqueado): edita na sessão, avisa ----------
  console.log('\nD) file:// / preview isolado');
  const d3=new JSDOM(html,semLS()), w3=d3.window, $3=i=>w3.document.getElementById(i);
  await wait(40);
  ok($3('banner').classList.contains('show'),'banner de aviso aparece quando não dá pra salvar');
  tap(w3,$3('bEdit')); tap(w3,w3.document.querySelectorAll('#content .sec')[0]);
  $3('fCh').value='ZZ · WW'; tap(w3,$3('secSave'));
  ok(ch(w3,0)==='ZZ · WW','edição funciona na sessão mesmo sem armazenamento');

  // ---------- E) salvar direto no GitHub (commit via API) ----------
  console.log('\nE) salvar direto no GitHub');
  ghPut=null;
  const lsE=memLS();
  const dE=new JSDOM(html,comLS(lsE)), wE=dE.window, $E=i=>wE.document.getElementById(i);
  await wait(40);
  $E('ghToken').value='github_pat_teste'; tap(wE,$E('bTools')); tap(wE,$E('bGhSave'));
  ok(JSON.parse(lsE.getItem('blackShow_gh')).token==='github_pat_teste','token guardado no aparelho');

  tap(wE,$E('bEdit')); tap(wE,wE.document.querySelectorAll('#content .sec')[0]);
  $E('fCh').value='QQ · RR'; tap(wE,$E('secSave'));
  ok($E('savePill').classList.contains('show'),'pill "Salvar" aparece com edição pendente');

  tap(wE,$E('bSalvarGh'));
  await wait(80);
  ok(ghPut && typeof ghPut.content==='string','fez PUT no repertorio.json com content base64');
  const enviado = Buffer.from(ghPut.content,'base64').toString('utf8');
  ok(enviado.includes('QQ · RR'),'o JSON enviado ao GitHub contém a edição');
  ok(JSON.parse(enviado).musicas.some(m=>m.bl),'JSON enviado preserva o campo bl');
  ok(!$E('savePill').classList.contains('show'),'pill some após salvar (rascunho limpo)');
  ok(ch(wE,0)==='QQ · RR','edição continua na tela após salvar (adotada como base)');

  // ---------- F) dispensar o pill com o ✕ ----------
  console.log('\nF) dispensar o lembrete de salvar');
  const lsF=memLS();
  const dF=new JSDOM(html,comLS(lsF)), wF=dF.window, $F=i=>wF.document.getElementById(i);
  await wait(40);
  tap(wF,$F('bEdit')); tap(wF,wF.document.querySelectorAll('#content .sec')[0]);
  $F('fCh').value='DD · EE'; tap(wF,$F('secSave'));
  ok($F('savePill').classList.contains('show'),'pill aparece após editar');
  tap(wF,$F('pillX'));
  ok(!$F('savePill').classList.contains('show'),'✕ oculta o pill');
  // outra edição na mesma sessão não força o pill de volta (segue oculto)
  tap(wF,wF.document.querySelectorAll('#content .sec')[1]);
  $F('fCh').value='FF · GG'; tap(wF,$F('secSave'));
  ok(!$F('savePill').classList.contains('show'),'depois de dispensado, segue oculto na sessão');

  console.log('\n'+(pass?'✅ TODOS OS TESTES PASSARAM':'❌ HÁ FALHAS'));
  process.exit(pass?0:1);
})();

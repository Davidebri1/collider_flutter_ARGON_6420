# Made by Claude. The configuration form: the launch window's page on the PC, and <address>/config online
# (Claude, 2026-10-23: moved here from collider_app.py so Collider online can show it too).
FORM = r"""<!doctype html><html><head><meta charset="utf-8"><title>Collider</title>
<style>
/* The launch window, redone by Claude (2026-10-21) in Apple's grouped-settings layout (iOS Settings; seen in Mobbin on
   Wispr Flow and GroupMe): grey page, white rounded groups, small grey headings above them, plain readable type.
   David: "This cyber tech look is hard to read and annoying." Light, and dark when Windows is set to dark. */
:root{color-scheme:light dark;--bg:#F2F2F7;--card:#FFFFFF;--text:#000000;--sub:#6C6C70;--sep:rgba(60,60,67,.16);--field:#F2F2F7;--accent:#007AFF;--red:#FF3B30}
@media (prefers-color-scheme:dark){:root{--bg:#000000;--card:#1C1C1E;--text:#FFFFFF;--sub:#8E8E93;--sep:rgba(84,84,88,.55);--field:#2C2C2E;--accent:#0A84FF;--red:#FF453A}}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.4 "Segoe UI Variable Text","Segoe UI",system-ui,sans-serif;user-select:none;-webkit-font-smoothing:antialiased}
form{padding:22px 18px 26px;max-width:760px;margin:0 auto}
.host{display:flex;align-items:baseline;gap:12px;margin:0 4px 6px}
.host label{color:var(--sub);font-size:15px}
.host input{font:600 30px/1.1 "Segoe UI Variable Display","Segoe UI",system-ui,sans-serif;width:150px;background:transparent;border:0;border-bottom:1px solid var(--sep);color:var(--text);padding:2px 0;outline:none}
.host input:focus{border-bottom-color:var(--accent)}
.host input.bad{border-bottom-color:var(--red);color:var(--red)}
h2{font-size:13px;font-weight:400;color:var(--sub);text-transform:uppercase;letter-spacing:.02em;margin:24px 16px 7px}
.row{background:var(--card);border-radius:12px;padding:12px 14px;margin-bottom:10px}
.grid{display:grid;grid-template-columns:120px 1fr 28px;gap:8px;align-items:center}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
input.f,textarea.f{width:100%;background:var(--field);border:0;border-radius:8px;color:var(--text);padding:8px 10px;font:14px/1.45 "Segoe UI Variable Text","Segoe UI",system-ui,sans-serif;outline:none;user-select:text}
input.f:focus,textarea.f:focus{box-shadow:0 0 0 2px var(--accent)}
textarea.f{min-height:72px;resize:vertical}
input.f::placeholder,textarea.f::placeholder{color:var(--sub)}
.uses{color:var(--sub);font-size:12.5px;margin-top:8px}
.x{background:none;border:0;color:var(--sub);cursor:pointer;font-size:20px;line-height:1;width:28px;height:28px;border-radius:14px}
.x:hover{background:var(--field)}
.add{background:var(--card);border:0;border-radius:12px;color:var(--accent);width:100%;padding:10px;cursor:pointer;font-size:22px;line-height:1}
.sw{display:flex;align-items:center;justify-content:space-between;font-size:15px}
.sw input{width:42px;height:24px;accent-color:#34C759}
.go{margin-top:20px;width:100%;padding:13px;border:0;border-radius:12px;background:var(--accent);color:#fff;font:600 17px "Segoe UI Variable Text","Segoe UI",system-ui,sans-serif;cursor:pointer}
.go:active{opacity:.85}
.where{color:var(--sub);font-size:12px;margin:12px 4px 0;word-break:break-all}
.kv{display:grid;grid-template-columns:190px 1fr;gap:10px;align-items:center;padding:7px 0;border-bottom:1px solid var(--sep)}
.kv:last-child{border-bottom:0}
.kv span{color:var(--text);font-size:14px}
.m{display:grid;grid-template-columns:1fr 1fr 1fr 28px;gap:8px;margin-bottom:8px;align-items:center}
.m>:first-child{grid-column:1/4;grid-row:1}
.m>button.x{grid-column:4;grid-row:1}
.mw{padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--sep)}
.mw:last-of-type{border-bottom:0}
.mw textarea.f{min-height:34px}
</style></head><body>
<form id="f" autocomplete="off">
  <div class="host"><label for="host">Host</label><input id="host" inputmode="numeric" autofocus></div>
  <div id="agents"></div>
  <h2>Providers</h2>
  <div id="rows"></div>
  <button type="button" class="add" id="add" title="Add provider">+</button>
  <div id="answers"></div>
  <h2>Themes</h2>
  <div class="row"><input class="f" id="themes"></div>
  <h2>Purchases</h2>
  <div id="buy"></div>
  <div class="row sw"><label for="bypass">Bypass</label><input type="checkbox" id="bypass"></div>
  <button class="go" type="submit">Launch</button>
  <div class="where" id="where"></div>
</form>
<script>
const C=INITIAL;let rows=C.providers.map(r=>Object.assign({name:'',endpoint:'',key:'',models:''},r));
const R=document.getElementById('rows'),H=document.getElementById('host');
const S=JSON.parse(JSON.stringify(C.settings));
const N={consensus_agent:'Consensus agent model',agent_chain:'Consensus agent backups',agent_prompt:'Consensus agent instruction',smartgen_prompt:'Smart Gen agent instruction',plan_prompt:'Search planning instruction',models:'Models',depth:'Response instruction by mode',line_length:'Summary length (characters)',search:'Web search by mode',plan_queries:'Planned searches by mode',source_chars:'Source length by mode (characters)',max_tokens:'Response length by mode (tokens)',deadline:'Response wait by mode (seconds)',silence:'Longest silence while streaming (seconds)',tuning:'Tuning',pack_price:'Pack price',tracks_per_pack:'Tracks per pack',imagine:'Discover Market'};
function inp(v,set){const long=typeof v==='string'&&(v.length>70||v.includes('\n'));const e=document.createElement(long?'textarea':'input');e.className='f';e.value=Array.isArray(v)?v.join(', '):v;if(long)e.rows=Math.min(14,v.split('\n').length+1);e.addEventListener('input',()=>set(e.value));return e;}
function typed(old,s){if(typeof old==='number'){const n=Number(s);return isNaN(n)?old:n;}if(Array.isArray(old))return s.split(',').map(x=>x.trim()).filter(Boolean).map((x,i)=>typeof old[i]==='number'?Number(x):x);return s;}
const MF=['id','label','short','provider','via','color','temperature'];
function drawModels(box){box.innerHTML='';S.models.forEach((m,i)=>{const w=document.createElement('div');w.className='mw';const r=document.createElement('div');r.className='m';MF.forEach(f=>{const e=inp(m[f]===undefined||m[f]===null?'':String(m[f]),s=>{m[f]=f==='temperature'&&s.trim()!==''&&!isNaN(Number(s))?Number(s):s;});e.placeholder=f;r.appendChild(e);});
const x=document.createElement('button');x.type='button';x.className='x';x.textContent='×';x.onclick=()=>{S.models.splice(i,1);drawModels(box);};r.appendChild(x);w.appendChild(r);
const sy=document.createElement('textarea');sy.className='f';sy.placeholder='system';sy.rows=Math.max(1,Math.min(8,(m.system||'').split('\n').length));sy.value=m.system||'';sy.addEventListener('input',()=>{m.system=sy.value;});w.appendChild(sy);box.appendChild(w);});
const a=document.createElement('button');a.type='button';a.className='add';a.textContent='+';a.onclick=()=>{S.models.push({id:'',label:'',short:'',provider:'',via:'NVIDIA',color:'#8B90A0',temperature:'',system:''});drawModels(box);};box.appendChild(a);}
function section(k,host){const h=document.createElement('h2');h.textContent=N[k];host.appendChild(h);const box=document.createElement('div');box.className='row';const v=S[k];
if(k==='models')drawModels(box);
else if(v&&typeof v==='object'&&!Array.isArray(v))Object.keys(v).forEach(sk=>{const r=document.createElement('div');r.className='kv';const l=document.createElement('span');l.textContent=sk;r.appendChild(l);r.appendChild(inp(v[sk],s=>{v[sk]=typed(C.settings[k][sk],s);}));box.appendChild(r);});
else box.appendChild(inp(v,s=>{S[k]=typed(C.settings[k],s);}));
host.appendChild(box);}
['consensus_agent','agent_chain','agent_prompt','smartgen_prompt','plan_prompt','models'].forEach(k=>section(k,document.getElementById('agents')));
['depth','line_length','search','plan_queries','source_chars','max_tokens','deadline','silence','tuning'].forEach(k=>section(k,document.getElementById('answers')));
['pack_price','tracks_per_pack'].forEach(k=>section(k,document.getElementById('buy')));
['imagine'].forEach(k=>section(k,document.getElementById('answers')));
function draw(){R.innerHTML='';rows.forEach((r,i)=>{const d=document.createElement('div');d.className='row';
d.innerHTML=`<div class="grid"><input class="f" data-k="name" placeholder="Name"><input class="f" data-k="key" placeholder="Key"><button type="button" class="x" title="Remove">×</button></div>
<div class="grid2"><input class="f" data-k="endpoint" placeholder="Address"><input class="f" data-k="models" placeholder="Models"></div><div class="uses"></div>`;
d.querySelectorAll('input').forEach(inp=>{inp.value=r[inp.dataset.k]||'';inp.addEventListener('input',()=>{r[inp.dataset.k]=inp.value;});});
d.querySelector('.x').onclick=()=>{rows.splice(i,1);C.uses.splice(i,1);draw();};
if(/tavily|fal\.run/i.test((r.endpoint||'')+(r.name||'')))d.querySelector('[data-k=models]').style.visibility='hidden';
d.querySelector('.uses').textContent=C.uses[i]||'';R.appendChild(d);});}
document.getElementById('add').onclick=()=>{rows.push({name:'',endpoint:'',key:'',models:''});C.uses.push('');draw();};
H.value=C.host;if(!C.host){document.querySelector('.host').style.display='none';document.querySelector('.go').textContent='Save';}document.getElementById('themes').value=C.themes;document.getElementById('bypass').checked=C.bypass;
document.getElementById('where').textContent='Saved to '+WHERE;draw();H.focus();H.select();
H.addEventListener('input',()=>H.classList.remove('bad'));
let busy=false;
document.getElementById('f').onsubmit=async e=>{e.preventDefault();if(busy)return;
if(!window.pywebview){busy=true;const g=document.querySelector('.go');try{const r=await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({providers:rows,themes:document.getElementById('themes').value,bypass:document.getElementById('bypass').checked,settings:S})});g.textContent=r.ok?'Saved':'Save';setTimeout(()=>{g.textContent='Save';},1600);}finally{busy=false;}return;}
busy=true;
try{const r=await pywebview.api.launch({host:H.value,providers:rows,themes:document.getElementById('themes').value,bypass:document.getElementById('bypass').checked,settings:S});
if(r&&r.error){H.classList.add('bad');H.focus();H.select();}}finally{busy=false;}};
</script></body></html>"""

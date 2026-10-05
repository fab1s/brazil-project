// Mobile presentation reuses the existing controls and their event handlers.
const mobile = matchMedia('(max-width: 760px), (max-height: 500px) and (pointer: coarse)');
const panel = document.querySelector('#layerPanel');
const workspace = document.querySelector('.map-workspace');
const button = (text, action) => { const b=document.createElement('button'); b.type='button'; b.textContent=text; b.addEventListener('click',action); return b; };
const icons={search:'<circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/>',layers:'<path d="m12 3 10 5-10 5L2 8Z"/><path d="m2 12 10 5 10-5M2 16l10 5 10-5"/>',summary:'<path d="M4 3v17h17M8 16v-5m5 5V6m5 10V9"/>',close:'<path d="m6 6 12 12M6 18 18 6"/>',collapse:'<path d="m6 9 6 6 6-6"/>',expand:'<path d="m6 15 6-6 6 6"/>'};
function iconButton(b,icon,label){b.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[icon]}</svg>`;b.setAttribute('aria-label',label);b.title=label;return b;}
const closePopups=()=>document.querySelectorAll('.maplibregl-popup-close-button').forEach(b=>b.click());
const dock=document.createElement('div'); dock.className='mobile-dock';
const layers=button('Layers',()=>setLayers(!document.body.classList.contains('mobile-layers-open')));
layers.setAttribute('aria-controls','layerPanel');
const summaries=button('Data summaries',()=>document.querySelector('#openInsights').click());
iconButton(layers,'layers','Layers');iconButton(summaries,'summary','Data summaries');dock.append(layers,summaries); workspace.append(dock);
const close=button('Done',()=>setLayers(false)); close.className='mobile-panel-close'; iconButton(close,'close','Close layers');panel.prepend(close);
function setLayers(open){ document.body.classList.toggle('mobile-layers-open',open); layers.setAttribute('aria-expanded',String(open)); if(open){closePopups();document.querySelector('#closeInsights').click();} }
const floating=document.createElement('section'); floating.className='mobile-indicator'; floating.setAttribute('aria-label','Active census indicator'); workspace.append(floating);
let preferred; let minimized=false;
function sync(){
 const cards=[...document.querySelectorAll('.indicator-control')].filter(c=>c.querySelector('input[type=checkbox]')?.checked);
 const card=cards.find(c=>c===preferred)||cards.at(-1); floating.replaceChildren(); floating.hidden=!card;
 if(!card)return;
 const title=document.createElement('strong'); title.textContent=card.querySelector('.layer-toggle strong').textContent;
 const selector=document.createElement('select'); selector.setAttribute('aria-label','Active indicator controls');
 cards.forEach(c=>{const o=document.createElement('option');o.textContent=c.querySelector('.layer-toggle strong').textContent;o.selected=c===card;selector.append(o);});
 selector.addEventListener('change',()=>{preferred=cards[selector.selectedIndex];sync();});
 const header=document.createElement('div');header.className='mobile-indicator-header';
 const toggle=iconButton(button('',()=>{minimized=!minimized;sync();}),minimized?'expand':'collapse',minimized?'Expand legend':'Minimize legend');toggle.setAttribute('aria-expanded',String(!minimized));
 header.append(cards.length>1?selector:title,toggle);floating.append(header);if(minimized)return;
 const years=document.createElement('div');years.className='mobile-years';
 card.querySelectorAll('.indicator-measures input').forEach(r=>{const b=button(r.nextElementSibling.textContent,()=>{r.click();sync();});b.setAttribute('aria-pressed',String(r.checked));years.append(b);}); floating.append(years);
 for(const s of ['.indicator-description','.ratio-ramp','.ratio-labels']){const n=card.querySelector(s);if(n)floating.append(n.cloneNode(true));}
}
panel.addEventListener('change',e=>{preferred=e.target.closest('.indicator-control')||preferred;sync();});
new MutationObserver(sync).observe(document.querySelector('#indicatorSections'),{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','style']});
const search=document.querySelector('#locationSearch');
const searchToggle=button('Search',()=>{const open=!search.classList.contains('mobile-search-open');search.classList.toggle('mobile-search-open',open);searchToggle.setAttribute('aria-expanded',String(open));if(open){setLayers(false);document.querySelector('#locationSearchInput').focus();}});searchToggle.className='mobile-search-toggle';searchToggle.setAttribute('aria-expanded','false');iconButton(searchToggle,'search','Search');search.prepend(searchToggle);
document.querySelector('#openInsights').addEventListener('click',()=>{if(mobile.matches){setLayers(false);closePopups();search.classList.remove('mobile-search-open');}});
new MutationObserver(()=>{if(mobile.matches&&document.querySelector('.calculation-dialog[open],.maplibregl-popup'))setLayers(false);document.body.classList.toggle('mobile-details-open',!!document.querySelector('.maplibregl-popup'));}).observe(document.querySelector('#map'),{childList:true,subtree:true});
document.addEventListener('click',e=>{if(mobile.matches&&e.target.closest('.indicator-info-button')){setLayers(false);closePopups();}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){setLayers(false);search.classList.remove('mobile-search-open');}});
function adapt(){document.body.classList.toggle('mobile-layout',mobile.matches);if(!mobile.matches)setLayers(false);sync();}
mobile.addEventListener('change',adapt);window.addEventListener('orientationchange',()=>setTimeout(adapt,150));adapt();

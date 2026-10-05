import { indicatorScale, NO_DATA_COLOUR } from "./indicator-scales.js?v=20261005-obras-2";
// SOURCE: Exact expressions in IBGE Census - Temporal Comparison.qmd.
const calculationDetails = {
  "black": {
    "icon": "user-round",
    "meaning": "Black (preta) population",
    "n10": "pessoa03_V003",
    "n22": "raca_V01318",
    "d10": "pessoa03_V001",
    "d22": "V0001",
    "s10": "IBGE 2010 Census · Pessoa (population), via censobr",
    "s22": "IBGE 2022 Census · Pessoas (population counts) and Basico (total population), via censobr; matched by census tract"
  },
  "brown": {
    "icon": "user-round",
    "meaning": "Brown (parda) population",
    "n10": "pessoa03_V005",
    "n22": "raca_V01320",
    "d10": "pessoa03_V001",
    "d22": "V0001",
    "s10": "IBGE 2010 Census · Pessoa (population), via censobr",
    "s22": "IBGE 2022 Census · Pessoas (population counts) and Basico (total population), via censobr; matched by census tract"
  },
  "black_brown": {
    "icon": "users-round",
    "meaning": "Black (preta) + Brown (parda) population",
    "n10": "pessoa03_V003 + pessoa03_V005",
    "n22": "raca_V01318 + raca_V01320",
    "d10": "pessoa03_V001",
    "d22": "V0001",
    "s10": "IBGE 2010 Census · Pessoa (population), via censobr",
    "s22": "IBGE 2022 Census · Pessoas (population counts) and Basico (total population), via censobr; matched by census tract"
  },
  "literacy": {
    "icon": "book-open",
    "meaning": "Literate people aged 15+",
    "n10": "pessoa01_V012 … pessoa01_V077",
    "n22": "alfabetizacao_V00748 … alfabetizacao_V00760",
    "d10": "pessoa13_V049 … pessoa13_V134",
    "d22": "alfabetizacao_V00644 … alfabetizacao_V00656",
    "s10": "IBGE 2010 Census · Pessoa (population), via censobr",
    "s22": "IBGE 2022 Census · Pessoas (population), via censobr"
  },
  "rudimentary_sanitation": {
    "icon": "waves",
    "meaning": "Households using a rudimentary pit, ditch, or discharge to a river, lake or sea (including stream in 2022)",
    "n10": "domicilio01_V019 + domicilio01_V020 + domicilio01_V021",
    "n22": "domicilio02_V00312 + domicilio02_V00313 + domicilio02_V00314",
    "d10": "domicilio01_V002",
    "d22": "domicilio01_V00001",
    "s10": "IBGE 2010 Census · Domicilio (households), via censobr",
    "s22": "IBGE 2022 Census · Domicilio (households), via censobr"
  },
  "water_network": {
    "icon": "droplets",
    "meaning": "Households supplied by the general water network",
    "n10": "domicilio01_V012",
    "n22": "domicilio02_V00111",
    "d10": "domicilio01_V002",
    "d22": "domicilio01_V00001",
    "s10": "IBGE 2010 Census · Domicilio (households), via censobr",
    "s22": "IBGE 2022 Census · Domicilio (households), via censobr"
  },
  "waste_collection": {
    "icon": "trash-2",
    "meaning": "Households with waste collection (2022 combines direct collection and communal containers)",
    "n10": "domicilio01_V035",
    "n22": "domicilio02_V00397 + domicilio02_V00398",
    "d10": "domicilio01_V002",
    "d22": "domicilio01_V00001",
    "s10": "IBGE 2010 Census · Domicilio (households), via censobr",
    "s22": "IBGE 2022 Census · Domicilio (households), via censobr"
  },
  "sewer_septic": {
    "icon": "network",
    "meaning": "Households using a general sewer / stormwater network or septic system (2022 includes septic / filter systems connected and not connected to the network)",
    "n10": "domicilio01_V017 + domicilio01_V018",
    "n22": "domicilio02_V00309 + domicilio02_V00310 + domicilio02_V00311",
    "d10": "domicilio01_V002",
    "d22": "domicilio01_V00001",
    "s10": "IBGE 2010 Census · Domicilio (households), via censobr",
    "s22": "IBGE 2022 Census · Domicilio (households), via censobr"
  }
};

// CONTRACT: Independent indicator sections share a single set of tile sources.
// Annual values are common-area estimates; change is in percentage points.
Object.assign(calculationDetails, {"houses": {"icon": "house", "meaning": "Houses, excluding village / condominium houses", "n10": "domicilio01_V003", "n22": "domicilio01_V00047", "d10": "domicilio01_V002", "d22": "domicilio01_V00001", "s10": "IBGE 2010 Census · Domicilio (households), via censobr", "s22": "IBGE 2022 Census · Domicilio (households), via censobr"}, "village_condo": {"icon": "blocks", "meaning": "Houses in villages or condominiums (not a specific measure of gated communities)", "n10": "domicilio01_V004", "n22": "domicilio01_V00048", "d10": "domicilio01_V002", "d22": "domicilio01_V00001", "s10": "IBGE 2010 Census · Domicilio (households), via censobr", "s22": "IBGE 2022 Census · Domicilio (households), via censobr"}, "apartments": {"icon": "building-2", "meaning": "Apartments", "n10": "domicilio01_V005", "n22": "domicilio01_V00049", "d10": "domicilio01_V002", "d22": "domicilio01_V00001", "s10": "IBGE 2010 Census · Domicilio (households), via censobr", "s22": "IBGE 2022 Census · Domicilio (households), via censobr"}, "income": {"icon": "wallet", "meaning": "Gross monthly income of household heads with income, before personal taxes and deductions"}});

export function createSocialIndicators({ map, state, bounds, archiveSuffix, url, popupNode, refresh, closePopup, onFirstTile }) {
  calculationDetails.population_density={icon:'grid',meaning:'Population density',s10:'IBGE 2010 Census · Pessoa, via censobr',s22:'IBGE 2022 Census · Basico, via censobr',n10:'pessoa03_V001',n22:'V0001',d10:'Area (km²)',d22:'Area (km²)'};
  const indicators = [
    ['population_density','Population Density','People per km²'],
    ['black','Black Population Proportion','Population'],
    ['brown','Brown Population Proportion','Population'],
    ['black_brown','Black + Brown Population Proportion','Population'],
    ['literacy','Literacy Proportion','People aged 15+'],
    ['rudimentary_sanitation','Rudimentary Sanitation Proportion','Households'],
    ['water_network','Water Network Proportion','Households'],
    ['waste_collection','Waste Collection Proportion','Households'],
    ['sewer_septic','Sewer / Septic Proportion','Households'],
    ['houses','Houses Proportion','Households'],
    ['village_condo','Village / Condominium Houses Proportion','Households'],
    ['apartments','Apartments Proportion','Households'],
    ['income','Household-head-weighted Income','July 2022 R$'],
  ];
  const choices = new Map(indicators.map(([key,label,unit]) => [key,{key,label,unit,enabled:key==='black',measure:'2022',opacity:1}]));
  const tracked = new Map(), layerKeys = new Map();
  const root = document.getElementById('indicatorSections');
  const level = () => map.getZoom()<7?'overview':map.getZoom()<10?'mid':'detail';
  const active = () => [...choices.values()].filter(c=>c.enabled);
  const hasRenderable=()=>active().some(c=>c.key!=='income'||level()!=='overview');
  const field = c => `${c.key}_${c.measure}`;
  const definitions = tier => tier==='overview' ? [{id:'social-overview',bounds:[-74.5,-35.5,-32.5,6.2],tier}] : Object.entries(bounds).filter(([,b])=>{const v=map.getBounds();return b[0]<=v.getEast()&&b[2]>=v.getWest()&&b[1]<=v.getNorth()&&b[3]>=v.getSouth();}).map(([r,b])=>({id:`social-${tier}-${r}`,bounds:b,tier}));
  // CONTRACT: Derive percentage change from annual values, independent of legacy tile change units.
  const densityChange=p=>p.population_density_2010>0&&p.population_density_2022!=null?100*(p.population_density_2022/p.population_density_2010-1):null;
  const displayedValue=(p,c)=>c.key==='population_density'&&c.measure==='change'?densityChange(p):p[field(c)];
  const densityChangeExpression=['case',['all',['>', ['coalesce',['get','population_density_2010'],0],0],['has','population_density_2022'],['!=',['get','population_density_2022'],null]],['*',100,['-',['/',['get','population_density_2022'],['get','population_density_2010']],1]],0];
  const colour = c => {
    const scale=indicatorScale(c.key,c.measure);
    const value=c.key==='population_density'&&c.measure==='change'?densityChangeExpression:['get',field(c)];
    return ['case',valid(c),['interpolate',['linear'],value,...scale.values.flatMap((v,i)=>[v,scale.colours[i]])],NO_DATA_COLOUR];
  };
  const valid = c => c.key==='population_density'&&c.measure==='change'?['all',['>', ['coalesce',['get','population_density_2010'],0],0],['has','population_density_2022'],['!=',['get','population_density_2022'],null]]: ['all',['has',field(c)],['!=',['get',field(c)],null]];
  function remove(id) {
    clearTimeout(tracked.get(id)?.timer);
    for(const [layer,entry] of layerKeys) if(entry.source===id) {if(map.getLayer(layer)) map.removeLayer(layer);layerKeys.delete(layer);}
    if(map.getSource(id)) map.removeSource(id);
  }
  function retry(id) {
    const item=tracked.get(id);
    if(!item||item.ready||!hasRenderable()||!definitions(level()).some(d=>d.id===id)&&id!=='social-overview') return;
    if(item.attempt>=3){item.failed=true;clearTimeout(item.timer);refresh();return;}
    remove(id);tracked.delete(id);add(item.definition,item.attempt+1);sync();
  }
  function add(definition,attempt=1) {
    if(map.getSource(definition.id)) return;
    const item={definition,attempt,ready:false,failed:false};tracked.set(definition.id,item);
    map.addSource(definition.id,{type:'vector',url:url(definition.id+'-'+archiveSuffix),bounds:definition.bounds});
    item.timer=setTimeout(()=>retry(definition.id),45000);
  }
  function sync() {
    state.visible.social=active().length>0;
    document.getElementById('emptyMapHint').hidden=Object.values(state.visible).some(Boolean);
    const desired=definitions(level()), wanted=new Set(desired.map(d=>d.id));
    const complete=desired.length>0&&desired.every(d=>tracked.get(d.id)?.ready);
    for(const [source,item] of tracked) {
      if(!map.getSource(source)) continue;
      for(const c of choices.values()) {
        const id=`${source}--${c.key}`;
        if(c.enabled&&!map.getLayer(id)) {
          const before=['favelas-fill','obras-fill','ibama-fill'].find(id=>map.getLayer(id));
          map.addLayer({id,type:'fill',source,'source-layer':'social',paint:{'fill-color':colour(c),'fill-opacity':c.opacity,'fill-antialias':false}},before);
          layerKeys.set(id,{source,key:c.key,overview:item.definition.tier==='overview'});
        }
        if(!map.getLayer(id)) continue;
        const fallback=item.definition.tier==='overview'&&!complete;
        map.setLayoutProperty(id,'visibility',c.enabled&&(c.key!=='income'||(level()!=='overview'&&item.definition.tier!=='overview'))&&(wanted.has(source)||fallback)?'visible':'none');
        map.setPaintProperty(id,'fill-opacity',c.opacity);
        map.setPaintProperty(id,'fill-color',colour(c));map.setFilter(id,null);
      }
    }
    const incomeCard=root.querySelector('[data-indicator=income]');if(incomeCard)renderLegend(choices.get('income'),incomeCard);
    refresh();
  }
  function ensure() {
    // WHY: isStyleLoaded also waits for tiles; a zoom transition must add its next tier while basemap tiles load.
    if(!map.getStyle()?.layers)return;
    if(!hasRenderable()){sync();return;}
    for(const d of [...definitions('overview'),...definitions(level())])add(d);
    sync();
  }
  function renderLegend(c,card) {
    const scale=indicatorScale(c.key,c.measure);
    const prefix=c.key==='income'&&level()==='overview'?'Zoom in to level 7+ to view income. ':'';
    card.querySelector('.indicator-description').textContent=prefix+(c.measure==='change'?'2010–2022 change':c.measure)+' · '+scale.unit+' · '+(scale.nonlinear?'Continuous nonlinear scale.':'Continuous linear scale.');
    const ramp=card.querySelector('.ratio-ramp');
    ramp.classList.remove('change-ramp');
    ramp.style.background='linear-gradient(90deg, '+scale.colours.map((colour,i)=>colour+' '+100*i/(scale.colours.length-1)+'%').join(', ')+')';
    const labels=card.querySelector('.ratio-labels');labels.classList.add('continuous-ticks');
    labels.replaceChildren(...scale.labels.map((label,i)=>{const el=document.createElement('span');el.textContent=label;el.style.left=100*i/(scale.labels.length-1)+'%';return el;}));
    let note=card.querySelector('.scale-availability');
    if(!note){note=document.createElement('p');note.className='scale-availability';labels.after(note);}
    note.innerHTML='<span class="no-data-swatch" aria-hidden="true"></span> Unavailable'+((c.key==='income'||c.key==='population_density')?' · + at the upper end means colour saturation.':'');
  }
  const calculationDialog=document.createElement('dialog');
  calculationDialog.className='calculation-dialog';
  calculationDialog.setAttribute('aria-labelledby','calculation-title');
  calculationDialog.innerHTML='<header class="calculation-dialog-header"><span class="calculation-dialog-icon" aria-hidden="true"></span><div><p>CALCULATION</p><h2 id="calculation-title"></h2></div><button type="button" class="calculation-close" aria-label="Close calculation details">×</button></header><div class="calculation-dialog-body"></div>';
  document.body.append(calculationDialog);
  calculationDialog.querySelector('.calculation-close').addEventListener('click',()=>calculationDialog.close());
  calculationDialog.addEventListener('click',event=>{if(event.target===calculationDialog){const r=calculationDialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)calculationDialog.close();}});
  let calculationTrigger=null;
  calculationDialog.addEventListener('close',()=>{calculationTrigger?.setAttribute('aria-expanded','false');calculationTrigger?.focus();});
  const groups = [
    ['Population', ['black', 'brown', 'black_brown', 'population_density']],
    ['Education', ['literacy']],
    ['Income', ['income']],
    ['Housing', ['houses', 'village_condo', 'apartments']],
    ['Basic Services', ['rudimentary_sanitation', 'water_network', 'waste_collection', 'sewer_septic']],
  ];
  const groupContainers = new Map();
  for (const [label, keys] of groups) {
    const group = document.createElement('section');
    group.className = 'indicator-group';
    const heading = document.createElement('h2'); heading.textContent = label;
    group.append(heading); root.append(group);
    for (const key of keys) groupContainers.set(key, group);
  }
  for(const c of choices.values()) {
    const card=document.createElement('section');card.className='layer-control indicator-control';card.dataset.indicator=c.key;
    card.innerHTML=`<div class="indicator-heading"><label class="layer-toggle"><input type="checkbox" id="indicator-${c.key}" ${c.enabled?'checked':''}><i class="layer-icon layer-icon-social ${c.key==='brown'?'brown-population-icon':''}" data-lucide="${calculationDetails[c.key].icon}" aria-hidden="true"></i><span><strong>${c.label}</strong><small class="layer-meta"><span class="geometry-kinds"><span class="geometry-kind" data-tooltip="Area" aria-label="Area"><i data-lucide="hexagon" aria-hidden="true"></i></span></span>IBGE · ${c.unit}</small></span></label><button type="button" class="indicator-info-button" aria-label="Calculation details for ${c.label}" aria-expanded="false" aria-haspopup="dialog" title="Calculation details"><i data-lucide="info" aria-hidden="true"></i></button></div><div id="info-${c.key}" class="indicator-info" hidden></div><div class="indicator-settings" ${c.enabled?'':'hidden'}><fieldset class="indicator-measures"><legend class="sr-only">${c.label}: select year or change</legend>${[['2010','2010'],['2022','2022'],['change',c.key==='population_density'?'Change (%)':c.key==='income'?'Change (%)':'Change (pp)']].map(([v,t])=>`<label><input type="radio" name="measure-${c.key}" value="${v}" ${v===c.measure?'checked':''}><span>${t}</span></label>`).join('')}</fieldset><p class="indicator-description"></p><div class="ratio-ramp"></div><div class="ratio-labels"></div><label class="indicator-opacity">Opacity <output>100%</output><input aria-label="${c.label} opacity" type="range" min="0" max="100" value="100"></label></div>`;
    const detail=calculationDetails[c.key];
    const denominator=c.key==='literacy'?'Total population aged 15+':c.unit==='Population'?'Total population':'Total households';
    const info=card.querySelector('.indicator-info');
    const numeratorLabel={black:'Black population',brown:'Brown population',black_brown:'Black + Brown population',literacy:'Literate people aged 15+',rudimentary_sanitation:'Households with rudimentary sanitation',water_network:'Households with network water',waste_collection:'Households with waste collection',sewer_septic:'Households with sewer / septic',houses:'Houses',village_condo:'Village / condominium houses',apartments:'Apartments'}[c.key];
    // WHY: Show the mapped percentage directly; retain exact source expressions below.
    info.innerHTML=`<h3>Formula</h3><div class="annual-formulas">${['2010','2022'].map(year=>`<section><h4>${year}</h4><div class="display-formula" role="math" aria-label="Percentage in ${year} equals ${numeratorLabel} divided by ${denominator}, multiplied by 100"><span class="formula-symbol">P<sub>${year}</sub> =</span><span class="formula-fraction"><span>${numeratorLabel}</span><span>${denominator}</span></span><span>× 100</span></div></section>`).join('')}</div><p class="formula-caption">P = percentage. Counts are summed within each common area.</p><h4>Change in percentage points</h4><div class="display-formula change-equation" role="math" aria-label="Change in percentage points equals the 2022 percentage minus the 2010 percentage"><span>Δ<sub>pp</sub> = P<sub>2022</sub> − P<sub>2010</sub></span></div><p>For example: 20% → 25% = <strong>+5 pp</strong>.</p><details class="formula-details"><summary>Source variables</summary>${['2010','2022'].map(year=>{const suffix=year==='2010'?'10':'22';return `<h4>${year}</h4><p class="indicator-source">Census datasets: ${detail['s'+suffix]}</p><dl><dt>Numerator</dt><dd><code>${detail['n'+suffix]}</code></dd><dt>Denominator</dt><dd><code>${detail['d'+suffix]}</code></dd></dl><div class="display-formula source-fraction" role="math" aria-label="${c.key} ratio ${year} equals the sum of ${detail['n'+suffix]} divided by the sum of ${detail['d'+suffix]}"><code>${c.key}_ratio_${year} =</code><span class="formula-fraction"><span><code>Σ(${detail['n'+suffix]})</code></span><span><code>Σ(${detail['d'+suffix]})</code></span></span></div>`;}).join('')}<p>The exported ratio is between 0 and 1. The map multiplies it by 100 to show a percentage.</p><p class="indicator-formula"><code>${c.key}_ratio_change_pp = 100 × (${c.key}_ratio_2022 − ${c.key}_ratio_2010)</code></p></details><details class="formula-details"><summary>Aggregation and missing values</summary><p>Σ means sum the counts over tracts assigned to the same <code>common_id</code> using <code>lookup_2010</code> or <code>lookup_2022</code>, then divide. These are ratios of totals, not averages of tract ratios. ${c.key==='literacy'?'The … ranges include every variable between the two codes. Each row first sums those columns with <code>rowSums(..., na.rm = TRUE)</code>. ':''}For expressions with +, missing components are replaced by zero before addition. Group sums use <code>sum(..., na.rm = TRUE)</code>; an all-missing count sum therefore becomes zero. A ratio is calculated only when its denominator is greater than zero.</p><p>A full join retains areas found in either year. An absent year stays unavailable, and change requires both years. Values outside 0–1 are shown as unavailable. Common-area values are displayed on their component 2022 polygons.</p><p>At municipality overview zoom, common areas are counted once per municipality. The map divides summed valid numerators by summed valid denominators for each year, then subtracts the annual ratios and multiplies by 100. Annual coverage may differ.</p><p class="indicator-source">Calculation source: <code>IBGE Census - Temporal Comparison.qmd</code></p></details>`;
    if(['houses','village_condo','apartments'].includes(c.key)) {
      
      const method=info.querySelectorAll('.formula-details')[1];
      method.innerHTML='<summary>Aggregation and missing values</summary><p>Counts are summed within each common_id before dividing. Missing numerator counts are treated as zero by the source sums. An entirely missing denominator remains unavailable; partial missing counts are ignored. Both years are retained with a full join, and change requires both ratios. Invalid proportions are unavailable.</p><p>Municipality summaries count each common area once per municipality and divide summed valid counts. Annual coverage may differ.</p><p>Source: the exported '+c.key+'_change_sf.gpkg and supplied R calculation.</p>';
    }
    if(c.key==='income') info.innerHTML=`<h3>Household-head-weighted income</h3><p>Gross monthly income of household heads with income, before personal income tax and social-security deductions. Includes income from work, pensions and other sources; it is not take-home or total household income. Tract means are weighted by household-head counts in tracts with usable data. Values describe common comparison areas, including supported splits and merges.</p><p><i>U</i><sub>t</sub> contains tracts with a valid income mean and positive household-head count in year <i>t</i>; <i>i</i> identifies a tract. Both sums use the same tracts.</p><h4>2010 · July 2022 reais</h4><div class="display-formula income-formula" role="math" aria-label="2010 weighted mean multiplied by the inflation index ratio"><span>Y<sub>2010</sub> =</span><span class="formula-fraction"><span><span class="income-sum"><span>Σ</span><sub>i ∈ U<sub>2010</sub></sub></span>[(V022<sub>i</sub> / V021<sub>i</sub>) × V020<sub>i</sub>]</span><span><span class="income-sum"><span>Σ</span><sub>i ∈ U<sub>2010</sub></sub></span>V020<sub>i</sub></span></span><span>×</span><span class="formula-fraction"><span>INPC<sub>Jul 2022</sub></span><span>INPC<sub>Jul 2010</sub></span></span></div><h4>Inflation factor · July 2010 → July 2022</h4><div class="display-formula income-formula" role="math" aria-label="Inflation factor equals 6645.74 divided by 3200.06, approximately 2.076755"><span>F =</span><span class="formula-fraction"><span>6,645.74</span><span>3,200.06</span></span><span>≈ 2.076755</span></div><p>Divide the July 2022 INPC index (6,645.74) by the July 2010 index (3,200.06). Multiply the 2010 income by this factor to express it in July 2022 reais. R$1.00 in July 2010 corresponds to approximately R$2.08 in July 2022 prices—an accumulated price increase of 107.68%. The calculation uses the full ratio, not the rounded display value.</p><h4>2022</h4><div class="display-formula income-formula" role="math" aria-label="2022 weighted income sum divided by included household heads"><span>Y<sub>2022</sub> =</span><span class="formula-fraction"><span><span class="income-sum"><span>Σ</span><sub>i ∈ U<sub>2022</sub></sub></span>(V06004<sub>i</sub> × V06001<sub>i</sub>)</span><span><span class="income-sum"><span>Σ</span><sub>i ∈ U<sub>2022</sub></sub></span>V06001<sub>i</sub></span></span></div><h4>Real change</h4><div class="display-formula income-formula" role="math" aria-label="Percentage change equals 2022 income minus 2010 income divided by 2010 income times 100"><span>Δ% =</span><span class="formula-fraction"><span>Y<sub>2022</sub> − Y<sub>2010</sub></span><span>Y<sub>2010</sub></span></span><span>× 100</span></div><p>Absolute change = Y₂₀₂₂ − Y₂₀₁₀, in July 2022 reais. Percentage change is not percentage-point change.</p><details class="formula-details"><summary>Source variables and inflation</summary><p>2010 ResponsavelRenda: V022 total monthly income of household heads; V021 heads with positive income; V020 all household heads. 2022 ResponsavelRenda: V06004 mean income of heads with income; V06001 all heads of occupied permanent private households.</p><p>The INPC inflation factor is shown above.</p></details><details class="formula-details"><summary>Weighting and coverage</summary><p>Weighting uses all heads, although the tract means describe heads with income. This is an approximation, not the exact pooled mean among income recipients; household-scope differences remain a qualification.</p><p>Income change is available for 279,962 of 287,178 common areas. Only tracts with a valid mean and positive household-head weight contribute, using the same tracts in both sums. Missing values are not treated as zero. Groups with no usable pairs remain unavailable. The contributing subset can differ between years. Each common ID is shown as one merged area. Income is shown from zoom 7; no municipal income overview is calculated.</p><p>Annual values use the same common-area boundaries; partially covered groups represent only their available tracts. Large changes are retained; values beyond the legend endpoints use the endpoint colour.</p></details>`;
    if(c.key==='population_density') info.innerHTML=`<h3>Formula</h3><div class="annual-formulas">${['2010','2022'].map(year=>`<section><h4>${year}</h4><div class="display-formula" role="math" aria-label="Population divided by area in square kilometres"><span>D<sub>${year}</sub> =</span><span class="formula-fraction"><span>Population</span><span>Area in km²</span></span></div></section>`).join('')}</div><h4>Percentage change</h4><div class="display-formula" role="math" aria-label="Percentage change equals 2022 density minus 2010 density, divided by 2010 density, times 100"><span class="formula-fraction"><span>D<sub>2022</sub> − D<sub>2010</sub></span><span>D<sub>2010</sub></span></span><span>× 100</span></div><p>2010 is the starting point: positive values mean an increase; negative values mean a decrease.</p><details class="formula-details"><summary>Source variables</summary><p>2010: IBGE Census · Pessoa (via censobr), pessoa03_V001.</p><p>2022: IBGE Census · Basico (via censobr), V0001.</p><p>Area: 2022 census polygons combined within each comparison area, measured in km² using the equal-area projection EPSG:6933.</p></details><details class="formula-details"><summary>Aggregation and missing values</summary><p>Population is summed within each comparison area and divided by its area. Both years use the same boundaries. Missing source population counts are ignored in group sums; an all-missing sum follows the source calculation and becomes zero. Missing years remain unavailable. Zero population gives zero density. Percentage change needs both years and a positive 2010 density.</p><p>At municipality overview, each comparison area's population and area is counted once per municipality. Values describe the included common areas and may cross municipality boundaries. Coverage may differ by year. Density is total population divided by total included area, not an average of densities.</p></details>`;
    const descriptions = {
      population_density: 'The number of residents per square kilometre, using the same comparison-area boundaries for both years.',
      black: 'The share of residents who identify as Black (preta).',
      brown: 'The share of residents who identify as Brown (parda).',
      black_brown: 'The combined share of residents who identify as Black (preta) or Brown (parda).',
      literacy: 'The share of people aged 15 or older who can read and write.',
      rudimentary_sanitation: 'The share of households using a rudimentary pit, ditch, or discharge into a water body for sewage disposal.',
      water_network: 'The share of households supplied by the general water network.',
      waste_collection: 'The share of households whose rubbish is collected.',
      sewer_septic: 'The share of households using a sewer network or septic system.',
      houses: 'The share of households in houses, excluding the separate village or condominium category.',
      village_condo: 'The share of households in houses within villages or condominiums; these are not necessarily gated communities.',
      apartments: 'The share of households in apartments.'
    };
    const description=document.createElement('p');
    description.className='indicator-description-intro';
    description.textContent=descriptions[c.key];
    info.prepend(description);
    const infoButton=card.querySelector('.indicator-info-button');
    infoButton.addEventListener('click',()=>{
      calculationDialog.querySelector('h2').textContent=c.label;
      calculationDialog.querySelector('.calculation-dialog-icon').replaceChildren(card.querySelector('.layer-icon').cloneNode(true));
      const content=info.cloneNode(true);content.hidden=false;content.removeAttribute('id');
      calculationDialog.querySelector('.calculation-dialog-body').replaceChildren(content);
      calculationTrigger=infoButton;infoButton.setAttribute('aria-expanded','true');
      calculationDialog.showModal();calculationDialog.querySelector('.calculation-dialog-body').scrollTop=0;
    });
    groupContainers.get(c.key).append(card);renderLegend(c,card);
    card.querySelector('input[type=checkbox]').addEventListener('change',event=>{
      c.enabled=event.target.checked;card.querySelector('.indicator-settings').hidden=!c.enabled;closePopup();
      if(!active().length)for(const item of tracked.values())clearTimeout(item.timer);
      else for(const [id,item] of tracked)if(!item.ready){remove(id);tracked.delete(id);}
      ensure();sync();
    });
    card.querySelectorAll('input[type=radio]').forEach(input=>input.addEventListener('change',()=>{c.measure=input.value;closePopup();renderLegend(c,card);ensure();sync();}));
    card.querySelector('input[type=range]').addEventListener('input',event=>{c.opacity=Number(event.target.value)/100;card.querySelector('output').textContent=`${event.target.value}%`;sync();});
  }
  const note=document.createElement('details');note.className='indicator-method';note.innerHTML='<summary>About these measures</summary><p>Annual proportions use complete common areas, shown as merged 2022 polygons. Internal tract boundaries are removed. Only positive-area overlap establishes a match. Boundary changes are assumed not to materially change the inhabited population; this assumption has not been checked against habitation data. Change is 2022 minus 2010 in percentage points. The source calculations treat missing count components as zero and ignore missing counts in group sums. Missing years and zero denominators remain unavailable. Undefined and invalid estimates remain unavailable. National views show weighted municipality summaries for proportions; annual coverage may differ.</p>';root.append(note);
  map.on('moveend',ensure);
  map.on('style.load',()=>{for(const item of tracked.values())clearTimeout(item.timer);tracked.clear();layerKeys.clear();ensure();});
  map.on('sourcedata',event=>{const item=tracked.get(event.sourceId);if(item&&event.tile&&event.tile.state==='loaded'){item.received=true;if(event.sourceId!=='social-overview')onFirstTile?.();}if(item&&!item.ready&&item.received&&event.isSourceLoaded){item.ready=true;clearTimeout(item.timer);sync();}});
  map.on('idle',()=>{let changed=false;for(const [id,item]of tracked)if(!item.ready&&item.received&&map.getSource(id)&&map.isSourceLoaded(id)){item.ready=true;clearTimeout(item.timer);changed=true;}if(changed)sync();});
  map.on('error',event=>{const item=tracked.get(event.sourceId);if(item&&!item.failed&&!item.retryQueued){item.ready=false;item.retryQueued=true;clearTimeout(item.timer);item.timer=setTimeout(()=>retry(event.sourceId),2000*item.attempt);}});
  function format(v,pp=false){if(v==null||!Number.isFinite(Number(v)))return'Unavailable';const n=Number(v)*(pp?1:100);return`${pp&&n>0?'+':''}${n.toFixed(1)}${pp?' pp':'%'}`;}
  const moneyFormat=new Intl.NumberFormat('en-GB',{style:'currency',currency:'BRL',currencyDisplay:'narrowSymbol',maximumFractionDigits:2});
  function measureFormat(v,c,measure=c.measure){if(c.key==='population_density')return v==null||!Number.isFinite(Number(v))?'Unavailable':`${measure==='change'&&Number(v)>0?'+':''}${Number(v).toLocaleString('en-GB',{maximumFractionDigits:1})}${measure==='change'?'%':' people/km²'}`;if(c.key!=='income')return format(v,measure==='change');if(v==null||!Number.isFinite(Number(v)))return 'Unavailable';return measure==='change'?`${Number(v)>0?'+':''}${Number(v).toFixed(1)}%`:moneyFormat.format(Number(v));}
  const countFormat=new Intl.NumberFormat('en-GB',{maximumFractionDigits:0});
  const countValue=v=>v==null||!Number.isFinite(Number(v))?'Unavailable':countFormat.format(Number(v));
  const countLabels={black:'Black population',brown:'Brown population',black_brown:'Black + Brown population',literacy:'Literate people aged 15+',rudimentary_sanitation:'Rudimentary sanitation households',water_network:'Network water households',waste_collection:'Waste collection households',sewer_septic:'Sewer / septic households',houses:'Houses',village_condo:'Village / condominium houses',apartments:'Apartments'};
  const choiceFor=id=>choices.get(layerKeys.get(id)?.key)||choices.get('black');
  state.visible.social=true;
  setTimeout(ensure,0);
  return {
    recover:()=>{for(const [id,item] of tracked)if(item.failed){remove(id);tracked.delete(id);}ensure();},
    ids:()=>[...layerKeys.keys()].filter(id=>map.getLayer(id)&&map.getLayoutProperty(id,'visibility')!=='none'),
    overview:id=>layerKeys.get(id)?.overview,
    selected:id=>active().length>0&&(id==='social-overview'||definitions(level()).some(d=>d.id===id)),
    status:()=>{if(!hasRenderable())return null;const pending=definitions(level()).map(d=>tracked.get(d.id));return pending.some(t=>t?.failed)?{message:'IBGE indicators failed to load.',failed:true}:pending.some(t=>!t?.ready)?{message:'Loading IBGE indicators…',failed:false}:null;},
    label:(p,id)=>{const c=choiceFor(id);return`${c.label} · ${measureFormat(displayedValue(p,c),c)}`;},
    popup:(p,overview,id)=>{
      const c=choiceFor(id);
      if(c.key==='population_density') {
        const rows=[['Common ID',overview?null:p.common_id],['Municipality code',p.code_muni],['2010 tracts in group',overview?null:p.n_2010],['2022 tracts in group',overview?null:p.n_2022],['2010',measureFormat(p.population_density_2010,c,'2010')],['2022',measureFormat(p.population_density_2022,c,'2022')],['Change',measureFormat(densityChange(p),c,'change')]];
        for(const y of ['2010','2022'])rows.push([`Population · ${y}`,countValue(p['population_density_n'+y])],[`Included area · ${y} (km²)`,p['population_density_d'+y]==null?'Unavailable':Number(p['population_density_d'+y]).toLocaleString('en-GB',{maximumFractionDigits:2})]);
        const node=popupNode(c.label,overview?`Municipality ${p.code_muni}`:`Common area ${p.common_id}`,measureFormat(displayedValue(p,c),c),rows,'Common-area estimate','social');
        const note=document.createElement('p');note.className='popup-count-note';note.textContent=overview?'Totals cover included comparison areas; coverage can differ by year.':'Population and area cover the complete merged common area.';node.append(note);return node;
      }
      if(c.key==='income') {
        const rows=[['Common ID',p.common_id],['Municipality code',p.code_muni],['2010 · July 2022 R$',measureFormat(p.income_2010,c,'2010')],['2022 · R$',measureFormat(p.income_2022,c,'2022')],['Real change',measureFormat(p.income_change,c,'change')],['Change · R$',measureFormat(p.income_change_brl,c,'2022')],['2010 heads included',countValue(p.income_heads_2010)],['2022 heads included',countValue(p.income_heads_2022)],['2010 tracts included',`${countValue(p.income_tracts_used_2010)} / ${countValue(p.income_tracts_total_2010)}`],['2022 tracts included',`${countValue(p.income_tracts_used_2022)} / ${countValue(p.income_tracts_total_2022)}`],['2010 tracts missing weights',countValue(p.income_missing_weights_2010)],['2022 tracts missing weights',countValue(p.income_missing_weights_2022)]];
        const node=popupNode(c.label,`Common area ${p.common_id}`,measureFormat(displayedValue(p,c),c),rows,'Weighted income · common area','social');
        const note=document.createElement('p');note.className='popup-count-note';note.textContent='Gross monthly income before personal taxes and deductions. Tract means for heads with income, weighted by available household-head counts. Both years in July 2022 reais; weighting is approximate.' + ((p.income_complete_2010===0||p.income_complete_2022===0)?' Partial coverage: the contributing tracts may differ between years.':'');node.append(note);return node;
      }
      const totalLabel=c.key==='literacy'?'Total people aged 15+':c.unit==='Population'?'Total population':'Total households';
      const rows=[['Common ID',overview?null:p.common_id],['Municipality code',p.code_muni],['2010 tracts in group',overview?null:p.n_2010],['2022 tracts in group',overview?null:p.n_2022],['2010',format(p[`${c.key}_2010`])],['2022',format(p[`${c.key}_2022`])],['Change',format(p[`${c.key}_change`],true)]];
      for(const year of ['2010','2022']) rows.push([`${countLabels[c.key]} · ${year}`,countValue(p[`${c.key}_n${year}`])],[`${totalLabel} · ${year}`,countValue(p[`${c.key}_d${year}`])]);
      const node=popupNode(c.label,overview?`Municipality ${p.code_muni}`:`Common area ${p.common_id}`,format(p[field(c)],c.measure==='change'),rows,'Common-area estimate','social');
      const note=document.createElement('p');note.className='popup-count-note';note.textContent=overview?'Counts cover common areas included in each year’s estimate. Coverage may differ.':'Counts cover the complete merged common area. Original tract boundaries are reference data.';node.append(note);
      return node;
    },
  };
}

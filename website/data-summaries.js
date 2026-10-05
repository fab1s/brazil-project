// SECTION: Nationwide census summaries; counts are deduplicated during the build.
export async function loadDataSummaries(fetchJson) {
  const root=document.getElementById('censusSummaryCards');
  const number=new Intl.NumberFormat('en-GB',{maximumFractionDigits:0});
  const fmt=v=>v==null?'Unavailable':number.format(v);
  const pct=v=>v==null?'Unavailable':`${v.toFixed(1)}%`;
  const el=(tag,text,className)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;if(className)n.className=className;return n;};
  function table(headers,rows){const t=el('table',null,'census-summary-table');const head=el('thead'),tr=el('tr');headers.forEach(h=>tr.append(el('th',h)));head.append(tr);t.append(head);const body=el('tbody');rows.forEach(row=>{const r=el('tr');row.forEach((v,i)=>r.append(el(i?'td':'th',v)));body.append(r);});t.append(body);return t;}
  try {
    const [data,mapData]=await Promise.all([fetchJson('data/indicator-summaries.json'),fetchJson('data/social.json')]);root.replaceChildren();
    const coverage=el('article',null,'summary-card');coverage.append(el('h3','Comparison coverage'),el('p',`${fmt(mapData.featureCount)} merged common areas. Groups retain every contributing tract, including those crossing municipality boundaries.`));
    const rows=['2010','2022'].map(year=>{const c=mapData.population_coverage[year],p=c.measures.population,h=c.measures.households;return [year,fmt(c.unmatched_tract_ids),fmt(p.unmatched_known_total),fmt(p.unmatched_missing_values),fmt(h.unmatched_known_total),fmt(h.unmatched_missing_values)];});
    coverage.append(table(['Year','Unmatched tracts','Known excluded people','Missing population values','Known excluded households','Missing household values'],rows),el('p','Known totals exclude missing values and may be incomplete. Unmatched tracts are excluded from temporal comparison; they are not assigned to a nearby group.','summary-note'));root.append(coverage);
    const fav=el('article',null,'summary-card');fav.append(el('h3','Favelas and communities · 2022'),table(['Measure','Count'],[['Communities',fmt(data.favelas.communities)],['Municipalities covered',fmt(data.favelas.municipalities)],['States covered',fmt(data.favelas.states)]]));
    const detail=el('details');detail.append(el('summary','Communities by state'),table(['State','Communities'],data.favelas.byState.map(s=>[s.name,fmt(s.count)])));fav.append(detail);root.append(fav);
    for(const topic of ['Population','Education','Housing','Basic services']){
      root.append(el('h3',topic,'summary-topic'));
      for(const item of data.indicators.filter(i=>i.topic===topic)){
        const density=item.key==='population_density';
        const value=v=>density?(v==null?'Unavailable':`${v.toLocaleString('en-GB',{maximumFractionDigits:1})} people/km²`):pct(v);
        const card=el('article',null,'summary-card');card.append(el('h3',item.label));
        const unit=item.topic==='Population'?'people':item.topic==='Education'?'people aged 15+':'households';
        const [a,b]=item.annual;card.append(table(['Available areas','2010','2022'],[[density?'Density':'Share',value(a.percent),value(b.percent)],['Areas with data',fmt(a.areas),fmt(b.areas)],['Areas without data',fmt(item.totalAreas-a.areas),fmt(item.totalAreas-b.areas)]]));
        const [p,q]=item.paired;card.append(el('p',`Change using the same ${fmt(p.areas)} areas in both years: ${item.changePP==null?'Unavailable':`${item.changePP>0?'+':''}${item.changePP.toFixed(1)} ${density?'%':'percentage points'}`}`,'summary-change'));
        card.append(el('p',`${value(p.percent)} in 2010 → ${value(q.percent)} in 2022.`, 'summary-note'));
        const counts=el('details');counts.append(el('summary',density?'Population and area used':'Counts used in the yearly shares'),table(['Count','2010','2022'],[[density?'Population':`Matching ${unit}`,fmt(a.numerator),fmt(b.numerator)],[density?'Included area (km²)':`Total eligible ${unit}`,fmt(a.denominator),fmt(b.denominator)]]));card.append(counts);root.append(card);
      }
    }
  }catch(error){root.textContent='Census summaries are temporarily unavailable.';console.error(error);}
}

// Fixed continuous colour anchors; not class boundaries.
export const NO_DATA_COLOUR = '#b8bec6';
const sequential = {
  5:['#f3f0eb','#b6c8c6','#6d999b','#286673','#0c2635'],
  6:['#f3f0eb','#c8d7d4','#92b6b5','#53888e','#205968','#0c2635'],
  7:['#f3f0eb','#d4dfdc','#aac6c3','#7aa4a6','#477f88','#205968','#0c2635']
};
const diverging=['#a52f48','#d18493','#edccd3','#f7f7f7','#c8e1e5','#76a3af','#1d6274'];
const annual={
 income:[0,1000,2000,5000,10000,20000,40000],
 population_density:[0,100,1000,5000,10000,20000,50000],
 black:[0,5,10,20,40,100], brown:[0,25,50,75,100],black_brown:[0,25,50,75,100],
 literacy:[0,60,80,90,95,100],rudimentary_sanitation:[0,1,5,20,50,100],
 water_network:[0,50,80,95,99,100],waste_collection:[0,50,80,95,99,100],sewer_septic:[0,50,80,95,99,100],
 houses:[0,25,50,75,100],apartments:[0,25,50,75,100],village_condo:[0,1,5,10,25,100]
};
export function indicatorScale(key,measure){
 const absolute=key==='income'||key==='population_density', change=measure==='change';
 const ticks=change?(absolute?[-100,-50,-10,0,10,50,100]:[-100,-25,-5,0,5,25,100]):annual[key];
 const colours=change?diverging:sequential[ticks.length];
 const labels=ticks.map((v,i)=>{
   let label=change?(v<0?'−'+Math.abs(v):v>0?'+'+v:'0'):(absolute&&v>=1000?v/1000+'k':String(v));
   if(i===ticks.length-1&&absolute)label+='+';
   return label;
 });
 return {ticks,labels,colours,values:ticks.map(v=>!absolute&&!change?v/100:v),
   unit:change?(absolute?'%':'pp'):key==='income'?'July 2022 R$':key==='population_density'?'people/km²':'%',
   nonlinear:change||!['brown','black_brown','houses','apartments'].includes(key)};
}

"""Reader-facing summaries of saved artifacts; never performs acquisition."""
import json
import numpy as np
import pandas as pd
from brazil_project.io import WorkflowError


def markdown(text):
    from IPython.display import display, Markdown
    display(Markdown(text))


def table(frame, caption=None):
    """Render readable tables without losing identifiers or changing stored values."""
    if caption:
        markdown(caption)
    from IPython.display import display, HTML
    display(HTML(frame.to_html(index=False, na_rep='Unavailable', float_format=lambda x: f'{x:,.4f}')))


def figure(ctx, name, fig, caption):
    import matplotlib.pyplot as plt
    from IPython.display import display, Image
    scope = 'municipality_'+ctx.municipality if ctx.municipality else 'national'
    path = ctx.root/'outputs/figures/reports'/scope/(name+'.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    display(Image(filename=str(ctx.require(path))))
    markdown(caption)


def summary(result, stage):
    """Keep diagnostic counts visible; retain complete provenance in one disclosure."""
    if stage == 'harmonisation':
        table(pd.DataFrame([{'Measure':label,'Count':result[key]} for label,key in
              [('Comparison groups','groups'),('Merged 2022 features','common_geometry_features'),('Reference 2022 pieces','tracts_2022'),('Repeated reference IDs','duplicate_base_ids')]]))
        rows=[]
        for year, coverage in result['population_coverage'].items():
            for measure, values in coverage['measures'].items():
                rows.append({'Year':year,'Measure':measure,'Matched tract IDs':coverage['matched_tract_ids'],
                    'Unmatched tract IDs':coverage['unmatched_tract_ids'],'Known unmatched total':values['unmatched_known_total'],
                    'Unmatched missing values':values['unmatched_missing_values'],'Matched missing values':values['matched_missing_values']})
        table(pd.DataFrame(rows),'Coverage: known totals exclude unavailable values; missing values are not zero.')
        markdown('Execution mode: `'+result['mode']+'`. '+result['assumption'])
    elif stage == 'obrasgov':
        table(pd.DataFrame({'Cleaning step':['Input snapshot records','Retained records','Excluded from this derivative','Archived retained-record count'],
                            'Count':[result.get(k) for k in ['records','cleaned_records','removed','baseline_cleaned_records']]}))
        markdown('Archived row-count agreement: **'+('yes' if result.get('count_matches_baseline') else 'no/unavailable')+'**. This checks counts only, not record identity or coordinate accuracy. Source: `'+result['source']+'`.')
    elif stage == 'indicators':
        table(pd.DataFrame([{'Indicator':k.replace('_',' ').title(),'Common areas':v['common_areas'],'Unavailable change':v.get('missing_change','See density table')}
                            for k,v in result.items() if isinstance(v,dict) and 'common_areas' in v]))
    elif stage == 'overview':
        table(pd.DataFrame([{'Comparison':'2000 → '+year,'Classification':key,'2000 tracts':value}
                           for year,counts in result['classification_counts'].items() for key,value in counts.items()]))
        markdown('Municipality: `'+result['municipality']+'`; geometry calculations use '+result['adapter']+'.')
    elif stage == 'census-exploration':
        table(pd.DataFrame([{'Year':year,'Mapped tract pieces':v['map_tracts'],'BH usable tract observations':v['BH_summary']['count'],
                            'BH median Black share (%)':100*v['BH_summary']['50%']} for year,v in result['annual'].items()]))
        markdown('Scope: '+', '.join(result['scope'])+'. Overlay: '+result['metro_overlay']+'.')
    elif stage == 'ibama':
        table(pd.DataFrame({'Measure':['Licensed source records','Untranslated sectors'],'Count':[result['records'],result['unknown_sectors']]}))
        markdown('Input source: `'+result['source']+'`; this refresh does not harvest live records.')
    elif stage == 'land-value':
        markdown('**Exploratory; cadastral processing incomplete.** Imported workbook sheets: '+', '.join(result['workbook_sheets'])+'.')
        for name in result.get('missing_exact_inputs',[]):markdown('Required input unavailable: `'+name+'`. No alternative date is substituted.')
    elif stage == 'obrasgov-location-qa':
        table(pd.DataFrame({'Measure':['Original source records','Geometry components','Eligible point/line components before state check','Quarantined components','Offshore components quarantined'],
                            'Count':[result[k] for k in ['source_records','components','map_components','quarantined_components','far_offshore_components']]}))
        table(pd.DataFrame([{'Location status':k.replace('_',' '),'Components':v} for k,v in result['component_status_counts'].items()]))
        markdown('Eligibility is a screening decision, not verified geocoding. Coordinates corrected: **'+str(result['coordinates_corrected'])+'**.')
    elif stage == 'primary-state':
        table(pd.DataFrame([{'Relation to reported primary state':k.replace('_',' '),'Components':v} for k,v in result['component_counts'].items()]))
        markdown(f"Of entirely outside components, {result['entirely_outside_intersecting_other_states']:,} intersect another state and {result['entirely_outside_intersecting_no_state']:,} intersect no mapped state territory. Multi-state projects and coastal boundaries need interpretation.")
    else:
        table(pd.DataFrame([{'Measure':k.replace('_',' ').title(),'Value':v} for k,v in result.items() if not isinstance(v,(dict,list)) and k!='generated_at']))
    # CONTRACT: full machine evidence remains available, but is not the reading path.
    markdown('<details>\n<summary>Technical provenance and complete processing record</summary>\n\n```json\n'+json.dumps(result,indent=2,ensure_ascii=False)+'\n```\n\n</details>')


def indicator_view(ctx, frame, name):
    """Summaries describe distributions of common areas, not population averages."""
    import matplotlib.pyplot as plt
    rows=[]
    ratio=name not in ('income','population_density')
    annual=[f'{name}_ratio_{y}' if ratio else f'{name}_{y}' for y in (2010,2022)]
    unit='%' if ratio else ('July 2022 BRL' if name=='income' else 'people/km²')
    for year,col in zip((2010,2022),annual):
        v=pd.to_numeric(frame[col],errors='coerce').replace([np.inf,-np.inf],np.nan)
        if ratio:v=100*v
        rows.append({'Year':year,'Unit':unit,'Available areas':v.notna().sum(),'Unavailable areas':v.isna().sum(),'Median across areas':v.median(),'25th percentile':v.quantile(.25),'75th percentile':v.quantile(.75)})
    table(pd.DataFrame(rows),'Unweighted distribution across common areas. These are not national population-weighted estimates.')
    change=f'{name}_ratio_change_pp' if ratio else ('income_change_brl' if name=='income' else 'population_density_change')
    table(frame[['common_id',*annual,change]].head(5),'First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.')
    if name in ('black','income','population_density'):
        values=[pd.to_numeric(frame[c],errors='coerce').replace([np.inf,-np.inf],np.nan).dropna().to_numpy()*(100 if ratio else 1) for c in annual]
        fig,ax=plt.subplots(figsize=(7,4));ax.boxplot(values,labels=['2010','2022'],showfliers=False)
        ax.set_ylabel(unit);ax.set_title(name.replace('_',' ').title()+' across common areas');ax.grid(axis='y',alpha=.2)
        figure(ctx,'indicator_'+name,fig,'Median and middle 50% of available common-area estimates; whiskers follow 1.5×IQR. Outliers are hidden in the figure and retained in the data. Annual availability can differ; this is descriptive, not a paired causal comparison.')


def harmonisation_diagram(ctx):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axes=plt.subplots(1,4,figsize=(12,3))
    for ax,title,nold,nnew in zip(axes,['One to one','Split','Merge','Complex'],[1,1,2,2],[1,2,1,3]):
        ax.set(xlim=(0,3),ylim=(0,3));ax.axis('off');ax.set_title(title)
        for x,n,label,color in [(0,nold,'2010','#B4516C'),(1.9,nnew,'2022','#087F86')]:
            for i in range(n):ax.add_patch(Rectangle((x,.5+2*i/n),1,2/n,facecolor=color,edgecolor='white'))
            ax.text(x+.5,.1,label,ha='center')
        ax.annotate('',xy=(1.85,1.5),xytext=(1.05,1.5),arrowprops={'arrowstyle':'->'})
    figure(ctx,'harmonisation_relationships',fig,'Schematic only: no measured tract boundaries. Connected links form one common_id; complete 2022 pieces are merged for analysis. Largest positive overlap is selected in both directions. Yearly footprints may differ under the accepted research assumption.')


def overview_example(ctx, tract):
    """Use the same real tracts/threshold as the saved interactive example."""
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from brazil_project.io import identifiers
    if ctx.municipality and ctx.municipality != '3106200':
        markdown('The preserved examples concern Belo Horizonte and are omitted outside that municipality. The scoped classification table remains above.')
        return
    path=ctx.require(ctx.path('census','tracts'))
    where=f"CAST(CAST(code_tract AS INTEGER) AS TEXT) = '{tract}'"
    old=gpd.read_file(path,layer='2000_urban',where=where)
    if old.empty:raise WorkflowError('Example 2000 tract unavailable: '+tract)
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,year in zip(axes,(2010,2022)):
        overlaps=gpd.read_file(ctx.require(ctx.artifact('overview',f'intersections_2000_{year}.gpkg')),where=f"CAST(CAST(code_tract_2000 AS INTEGER) AS TEXT) = '{tract}'")
        ids=identifiers(overlaps.loc[overlaps.overlap_pct>.05,'code_tract_new']).dropna().unique()
        if len(ids):
            query='CAST(CAST(code_tract AS INTEGER) AS TEXT) IN ('+','.join("'"+v+"'" for v in ids)+')'
            new=gpd.read_file(path,layer=str(year),where=query).to_crs(5880)
            new.plot(ax=ax,color='#E0EEEB',edgecolor='#087F86',linewidth=1)
        old.to_crs(5880).boundary.plot(ax=ax,color='#B4516C',linewidth=2)
        ax.set_title(f'2000 → {year}');ax.set_axis_off()
    figure(ctx,'overview_'+tract,fig,'Real 2000 tract '+tract+' (rose outline) and newer tracts (teal), selected by the original >5% overlap rule. No basemap; complete newer outlines may extend outside the old tract. This exploratory classification differs from the 2010–2022 harmonisation method.')


def show_chunk(ctx, source, index):
    manifest=json.loads((ctx.root/'code/config/report_chunks.json').read_text())
    entry=manifest[source][index-1];stage,artifact=entry['stage'],entry['artifact']
    seen=getattr(ctx,'_report_presented',set());ctx._report_presented=seen
    identity=(stage,artifact)
    # WHY: original cell order is retained without repeating the same result.
    special=entry['chunk_label'].startswith('example_') or entry['chunk_label'] in ('vizualisation','visualization_black_ratio','count_charts')
    if identity in seen and not special:
        markdown('<!-- Saved result already presented; original cell retained for traceability. -->')
        return
    seen.add(identity)
    if artifact=='report':
        result=json.loads(ctx.require(ctx.artifact(stage,'report.json')).read_text())
        if stage=='harmonisation':
            pointer=json.loads(ctx.require(ctx.artifact(stage,'current.json')).read_text())
            if result.get('generation')!=pointer.get('generation'):raise WorkflowError('Report and harmonisation pointer differ; rerun processing.')
        if not special:summary(result,stage)
    else:
        if stage=='harmonisation':
            from brazil_project.harmonisation.census import load_bundle
            frames,_=load_bundle(ctx,[artifact]);frame=frames[artifact]
        else:frame=pd.read_parquet(ctx.require(ctx.artifact(stage,artifact+'.parquet')))
        if stage=='indicators':indicator_view(ctx,frame,artifact)
        elif not special:
            preview=frame.drop(columns=['geometry','harmonisation_version'],errors='ignore').head(10)
            if stage in ('obrasgov','ibama'):preview=preview.rename(columns={'projects':'Source records','share':'Share of classified records (fraction)'})
            table(preview,f'{len(frame):,} saved rows; showing up to ten. See the codebook for column definitions.')
        if stage=='harmonisation':
            markdown('One row per common_id. area_km2 is the saved equal-area denominator; geometry belongs to the same versioned lookup bundle.')
            merged_example(ctx, frames)
    from IPython.display import Image, display
    if stage=='charts':
        for name in ['urban_inadequate_sanitation_2010_2022.png','urban_inadequate_sanitation_income_boxplots_2022.png']:
            path=ctx.root/'outputs/figures'/('municipality_'+ctx.municipality if ctx.municipality else 'brazil')/name
            display(Image(filename=str(ctx.require(path))))
            markdown('Current conference output: `'+name+'`. See the explanation above for populations, quintiles and exclusions.')
    if stage=='obrasgov' and entry['chunk_label']=='count_charts':
        # Relabel presentation accurately: the producer counts rows, not unique IDs.
        import matplotlib.pyplot as plt
        for name in ('type_counts','type_subtype_counts'):
            data=pd.read_parquet(ctx.require(ctx.artifact(stage,name+'.parquet')))
            labels=data.type_en if name=='type_counts' else data.type_en+' — '+data.subtype_en
            fig,ax=plt.subplots(figsize=(10,6));ax.barh(labels.iloc[::-1],data.projects.iloc[::-1],color='#087F86');ax.set_xlabel('Source records');ax.set_title('Obrasgov classified records');ax.tick_params(axis='y',labelsize=8)
            figure(ctx,name,fig,'Largest 15 saved categories; counts describe source rows, which can repeat project IDs. Missing translations are excluded from classified counts. Full classified records determine the saved share denominator, before truncation to 15 categories.')
    if stage=='ibama' and entry['chunk_label']=='vizualisation':
        import matplotlib.pyplot as plt
        data=pd.read_parquet(ctx.require(ctx.artifact(stage,'sector_counts.parquet')))
        fig,ax=plt.subplots(figsize=(8,4));ax.barh(data.tp_sector_en.fillna('Untranslated'),data.projects,color='#087F86');ax.set_xlabel('Licensed source records')
        figure(ctx,'ibama_sectors',fig,'Counts of licensed source records by translated sector, including untranslated values. This does not measure environmental impact or distinct developments.')
        markdown('Interactive map: `outputs/maps/ibama.html` (local HTML; GitHub cannot execute it).')
    if stage=='overview' and entry['chunk_label'].startswith('example_'):
        examples={'example_1_split':'310620025610001','example_2_split':'310620005650306','example_3_reshape':'310620005620021','example_3_stable':'310620005620008'}
        overview_example(ctx,examples[entry['chunk_label']])
    if stage=='census-exploration' and entry['chunk_label']=='visualization_black_ratio':
        for year in (2010,2022):display(Image(filename=str(ctx.require(ctx.root/f'outputs/figures/census-exploration/black_ratio_boxplot_{year}.png'))))
        markdown('Belo Horizonte tract-level distributions, using each year’s original geography; the vertical axis is a fraction (0.10 = 10%). Boxplots give equal weight to each usable tract, not each resident. These are not harmonised change estimates. Interactive map: `outputs/maps/black_ratio_2010_2022.html`.')


def merged_example(ctx, frames):
    """Display one real multi-tract group from the validated bundle, in current scope."""
    import geopandas as gpd
    import matplotlib.pyplot as plt
    sizes=frames['group_sizes']
    candidates=sizes[sizes.n_2022>1].copy()
    if candidates.empty:
        markdown('No multi-tract 2022 group exists in this scope; a merged-boundary example is not applicable.')
        return
    key=candidates.assign(order=candidates.common_id.astype(str)).sort_values('order').iloc[0].common_id
    current=json.loads(ctx.require(ctx.artifact('harmonisation','current.json')).read_text())
    path=ctx.require(ctx.intermediate/'harmonisation/bundles'/current['generation']/'base_geometry_2022.parquet')
    pieces=gpd.read_parquet(path,filters=[('common_id','==',key)])
    common=frames['common_geometry_2022'];merged=common[common.common_id==key]
    if pieces.empty or len(merged)!=1:raise WorkflowError('Merged example is inconsistent with its bundle')
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,data,title in zip(axes,(pieces,merged),('Reference 2022 pieces','Merged analytical feature')):
        data.to_crs(5880).plot(ax=ax,color='#E0EEEB',edgecolor='#087F86',linewidth=1)
        ax.set_title(title);ax.set_axis_off()
    figure(ctx,'common_area_merged',fig,'Actual common_id '+str(key)+': complete reference pieces at left, one merged analytical feature at right. Original pieces remain saved. This shows removal of internal boundaries, not equality of 2010 and 2022 footprints.')

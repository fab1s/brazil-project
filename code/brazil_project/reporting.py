"""Display saved scientific artifacts without executing acquisition while rendering."""
import json
import os
from pathlib import Path
import pandas as pd
from brazil_project.io import WorkflowError


def show_chunk(ctx,source,index):
    manifest=json.loads((ctx.root/'code/config/report_chunks.json').read_text())
    entry=manifest[source][index-1]
    stage,artifact=entry['stage'],entry['artifact']
    from IPython.display import display,Image,HTML
    github_preview = os.environ.get('BRAZIL_REPORT_FORMAT') == 'gfm'

    def show_map(path):
        if github_preview:
            # COMPATIBILITY: GitHub strips JavaScript; keep interactive maps in
            # HTML reports rather than embedding unusable widgets in Markdown.
            from IPython.display import Markdown
            display(Markdown('Local interactive map (outside Git): `' + str(path.relative_to(ctx.root)) + '`'))
        else:
            display(HTML(path.read_text()))
    folder=ctx.intermediate/stage
    if artifact=='report':
        path=folder/'report.json'
        result=json.loads(ctx.require(path).read_text())
        if stage=='harmonisation':
            pointer=json.loads(ctx.require(ctx.intermediate/'harmonisation/current.json').read_text())
            if result.get('generation')!=pointer.get('generation'): raise WorkflowError('Report and harmonisation pointer differ; rerun processing.')
        display(result)
    else:
        path=ctx.artifact(stage, artifact+'.parquet')
        if ctx.require(path):
            if stage=='harmonisation':
                from brazil_project.harmonisation.census import load_bundle
                frames,_=load_bundle(ctx,[artifact]);frame=frames[artifact]
            else: frame=pd.read_parquet(path)
            display(frame.drop(columns='geometry',errors='ignore').head(20))
            display({'artifact_rows':len(frame),'path':str(path.relative_to(ctx.root))})
    if stage=='charts':
        for name in ['urban_inadequate_sanitation_2010_2022.png','urban_inadequate_sanitation_income_boxplots_2022.png']:
            path=ctx.root/'outputs/figures'/('municipality_'+ctx.municipality if ctx.municipality else 'brazil')/name
            display(Image(filename=str(ctx.require(path))))
    if stage=='ibama' and entry['chunk_label']=='vizualisation':
        path=ctx.root/'outputs/maps/ibama.html'
        show_map(ctx.require(path))
    if stage=='overview' and entry['chunk_label'].startswith('example_'):
        examples={'example_1_split':'310620025610001','example_2_split':'310620005650306','example_3_reshape':'310620005620021','example_3_stable':'310620005620008'}
        path=ctx.root/'outputs/maps'/('municipality_'+ctx.municipality if ctx.municipality else 'overview')/(examples[entry['chunk_label']]+'.html')
        show_map(ctx.require(path))
    if stage=='census-exploration' and entry['chunk_label']=='visualization_black_ratio':
        path=ctx.root/'outputs/maps/black_ratio_2010_2022.html'
        show_map(ctx.require(path))

"""Display saved scientific artifacts without executing acquisition while rendering."""
import json
from pathlib import Path
import pandas as pd
from brazil_project.io import WorkflowError


def show_chunk(ctx,source,index):
    manifest=json.loads((ctx.root/'config/notebook_chunks.json').read_text())
    entry=manifest[source][index-1]
    stage,artifact=entry['stage'],entry['artifact']
    from IPython.display import display,Image,HTML
    folder=ctx.intermediate/stage
    if artifact=='report':
        path=folder/'report.json'
        if path.exists(): display(json.loads(path.read_text()))
        else: display({'stage':stage,'status':'not generated','command':f'brazil-project run {stage}'})
    else:
        path=ctx.artifact(stage, artifact+'.parquet')
        if path.exists():
            frame=pd.read_parquet(path)
            display(frame.drop(columns='geometry',errors='ignore').head(20))
            display({'artifact_rows':len(frame),'path':str(path.relative_to(ctx.root))})
        else: display({'artifact':artifact,'status':'not generated','stage':stage})
    if stage=='charts':
        for name in ['urban_inadequate_sanitation_2010_2022.png','urban_inadequate_sanitation_income_boxplots_2022.png']:
            path=ctx.root/'outputs/figures/brazil'/name
            if path.exists(): display(Image(filename=str(path)))
    if stage=='ibama' and entry['chunk_label']=='vizualisation':
        path=ctx.root/'outputs/maps/ibama.html'
        if path.exists(): display(HTML(path.read_text()))
    if stage=='overview' and entry['chunk_label'].startswith('example_'):
        examples={'example_1_split':'310620025610001','example_2_split':'310620005650306','example_3_reshape':'310620005620021','example_3_stable':'310620005620008'}
        path=ctx.root/'outputs/maps/overview'/(examples[entry['chunk_label']]+'.html')
        if path.exists(): display(HTML(path.read_text()))
    if stage=='census-exploration' and entry['chunk_label']=='visualization_black_ratio':
        path=ctx.root/'outputs/maps/black_ratio_2010_2022.html'
        if path.exists(): display(HTML(path.read_text()))

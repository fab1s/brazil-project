"""Preserve original prose and chunk order while exposing explicit stage artifacts."""
from pathlib import Path
import re
import csv
import json
ROOT=Path(__file__).resolve().parents[2]
ARCHIVE=ROOT/'data/archive/original_code'

def stage_for(path):
    text=str(path)
    if 'CS2Nordic' in text:return 'charts'
    if 'Temporal Comparison' in text:return 'indicators'
    if 'harmonisation' in text:return 'harmonisation'
    if 'Overview' in text:return 'overview'
    if '/IBAMA/' in text:return 'ibama'
    if '/Obrasgov/' in text:return 'obrasgov'
    if '/Land value/' in text:return 'land-value'
    return 'census-exploration'


def artifact(stage,label,body):
    if stage=='indicators':
        names={'black_change_sf':'black','literacy_sf':'literacy','rudimentary__sanitation_sf':'rudimentary_sanitation',
               'water_network_sf':'water_network','waste_collection_sf':'waste_collection','sewer_septic_sf':'sewer_septic',
               'brown_sf':'brown','black_brown_sf':'black_brown','income_sf':'income','houses_sf':'houses',
               'village_condo_sf':'village_condo','apartment_sf':'apartments','population_density_sf':'population_density'}
        return names.get(label,'report')
    if stage=='harmonisation':return 'common_geometry_2022' if label=='harmonisation' else 'report'
    if stage=='land-value':return 'annex_i' if label=='import_price_table' else 'report'
    if stage=='obrasgov':return 'type_subtype_counts' if label in ['subtype_frequency','count_charts'] else 'report'
    if stage=='ibama':return 'sector_counts' if label=='joining' else 'report'
    if stage=='charts':return 'year_summary'
    if stage=='overview':
        if '2022' in label:return 'change_summary_2000_2022'
        if '2010' in label:return 'change_summary_2000_2010'
    return 'report'


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--overwrite-generated',action='store_true')
    args=parser.parse_args()
    if any((ROOT/'research/notebooks').glob('*.qmd')) and not args.overwrite_generated:
        raise SystemExit('Migrated reports already exist; preserve maintained files. Use --overwrite-generated only for an intentional regeneration.')
    mapping=[];reports={}
    for original in sorted(ARCHIVE.rglob('*.qmd')):
        rel=original.relative_to(ARCHIVE);stage=stage_for(rel)
        name=re.sub(r'[^a-z0-9]+','_',original.stem.lower()).strip('_')+'.qmd'
        destination=ROOT/'research/notebooks'/name
        text=original.read_text()
        header,sep,rest=text[4:].partition('\n---') if text.startswith('---\n') else ('','','')
        if sep:
            # COMPATIBILITY: Retain visual editing when translating executable chunks.
            if not re.search(r'^editor:', header, re.M):
                header += '\neditor: visual'
            text='---\n'+header.strip()+'\njupyter: python3\n---'+rest
        entries=[];count=0
        def replace(match):
            nonlocal count
            count+=1;label=match[1].strip() or f'unnamed_{count}'
            body=match[2];target=artifact(stage,label,body)
            entry={'source_file':str(rel),'chunk_index':count,'chunk_label':label,'original_language':'R','original_sha256':__import__('hashlib').sha256(body.encode()).hexdigest(),
                   'stage':stage,'implementation':{'indicators':'code/brazil_project/indicators/temporal.py','harmonisation':'code/brazil_project/harmonisation/census.py','overview':'code/scripts/r/overview.R','ibama':'code/brazil_project/infrastructure/projects.py','obrasgov':'code/brazil_project/infrastructure/projects.py','land-value':'code/brazil_project/land_value/property.py','charts':'code/brazil_project/visualisation/charts.py','census-exploration':'code/brazil_project/visualisation/census.py'}[stage],
                   'artifact':target,'notebook':str(destination.relative_to(ROOT)),'acquisition_disabled_in_original':bool(re.search(r'#\|\s*eval:\s*false',body)),
                   'status':'implemented; validation recorded separately'}
            mapping.append(entry);entries.append(entry)
            prelude='''from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
''' if count==1 else ''
            code=prelude+f'show_chunk(ctx, {str(rel)!r}, {count})\n'
            return '```{python}\n#| label: '+name[:-4]+'_'+str(count)+'\n'+code+'```'
        text=re.sub(r'```\{r\s*([^}]*)\}\n(.*?)\n```',replace,text,flags=re.S)
        if stage=='harmonisation':
            text=text.replace('The final layer keeps the 2022 census tract boundaries unchanged and records their relationship with the 2010 areas.', 'Original tract pieces remain reference geometry. Active outputs merge complete 2022 groups by common_id and exclude contact-only matches; see the approved harmonisation policy.')
        # Existing image references point to the copied original outputs, never OneDrive.
        def image(match):
            from urllib.parse import unquote,quote
            old=original.parent/unquote(match[1]);relative=old.relative_to(ARCHIVE)
            copied=ROOT/'data/archive/original_outputs'/relative
            import os
            return ']('+quote(os.path.relpath(copied,destination.parent)) + ')'
        text=re.sub(r'\]\(([^)]+\.png)\)',image,text)
        destination.write_text(text)
        reports[str(rel)]=entries
    for original in sorted(ARCHIVE.rglob('*.R')):
        mapping.append({'source_file':str(original.relative_to(ARCHIVE)),'chunk_index':0,'chunk_label':'standalone_script','original_language':'R','original_sha256':__import__('hashlib').sha256(original.read_bytes()).hexdigest(),'stage':'ibama','implementation':'code/brazil_project/infrastructure/projects.py','artifact':'licensed_projects','notebook':'research/notebooks/ibama_data_extraction.qmd','acquisition_disabled_in_original':False,'status':'implemented; alternate original translation-column spelling retained'})
    destination=ROOT/'docs/evidence/workflow_mapping.csv'
    with destination.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(mapping[0]), lineterminator='\n');writer.writeheader();writer.writerows(mapping)
    (ROOT/'code/config/notebook_chunks.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    print(f'Mapped {len(mapping)} executable source entries in {len(reports)} Quarto reports and standalone R code')

if __name__=='__main__':main()

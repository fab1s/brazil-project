"""Resumable raw API snapshots; routine processing never triggers downloads."""
import hashlib
import json
import os
from datetime import datetime, timezone
import geopandas as gpd
import pandas as pd
import requests
import shapely
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from brazil_project.io import WorkflowError

OBRAS='https://api-publica.obrasgov.gestao.gov.br/obras'
ENRICH='https://cipi.economia.gov.br/cipi-backend/api/public/projetoinvestimento/listar-geometrias-ids-projetos'
IBAMA={kind:f'https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_{suffix}/FeatureServer/{layer}'
       for kind,suffix,layer in [('points','p',16),('lines','l',15),('polygons','a',14)]}


def session():
    client=requests.Session()
    client.mount('https://',HTTPAdapter(max_retries=Retry(total=4,backoff_factor=1,status_forcelist=[429,500,502,503,504],allowed_methods=['GET','POST'])))
    return client


def cached_json(client,path,url,params=None,body=None):
    request={'url':url,'params':params,'body':body}
    fingerprint=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
    if path.exists():
        record=json.loads(path.read_text())
        if record.get('fingerprint')!=fingerprint: raise WorkflowError(f'Cached request differs: {path}')
        return record['response']
    path.parent.mkdir(parents=True,exist_ok=True)
    response=client.get(url,params=params,timeout=120) if body is None else client.post(url,json=body,timeout=120)
    response.raise_for_status();data=response.json()
    if isinstance(data,dict) and 'error' in data: raise WorkflowError(f'{url}: {data["error"]}')
    record={'fingerprint':fingerprint,'request':request,'retrieved_at':datetime.now(timezone.utc).isoformat(),'response':data}
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(record,ensure_ascii=False));os.replace(temp,path)
    return data


def pages(client,folder,resource):
    records=[];total=None;page=1
    while total is None or page<=total:
        body=cached_json(client,folder/f'{resource}_{page:06}.json',f'{OBRAS}/{resource}',{'pagina':page,'tamanho_da_pagina':200})
        if not isinstance(body,dict) or not isinstance(body.get('data'),list): raise WorkflowError('Unexpected Obrasgov page format')
        if body.get('page_number',page)!=page: raise WorkflowError('Obrasgov returned a different page number')
        reported=body.get('total_pages')
        if not isinstance(reported,int) or reported<0: raise WorkflowError('Obrasgov total_pages missing or invalid')
        if total is not None and total!=reported: raise WorkflowError('Obrasgov total_pages changed mid-download; start a new snapshot')
        total=reported;records.extend(body['data']);page+=1
    return records


def flatten_projects(records):
    rows=[]
    drop={'repassadores','tomadores','investimentos_previstos','ppas','eixos_tipos','fotos','pins','areas_restricao','executores'}
    for project in records:
        row={k:v for k,v in project.items() if k not in drop}
        row={k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()}
        row['vl_investimento_previsto_total']=sum(float(v['vl_investimento_previsto']) for v in (project.get('investimentos_previstos') or []) if v.get('vl_investimento_previsto') is not None)
        pins=[shapely.from_wkt(v['pin']) for v in (project.get('pins') or []) if v and v.get('pin')]
        row['geometry']=shapely.GeometryCollection(pins) if pins else None
        for taxonomy in project.get('eixos_tipos') or [{}]:
            expanded=dict(row);expanded.update(taxonomy or {});rows.append(expanded)
    if not rows: raise WorkflowError('No Obrasgov project records')
    return gpd.GeoDataFrame(rows,geometry='geometry',crs=4674)


def enrich_projects(frame,metadata,client,folder):
    target=[r for r in metadata if r.get('origem_geometria') in ['Shapefile','Vetorização']]
    ids=list(dict.fromkeys(str(r['id_projeto_investimento']) for r in target))
    wanted={r['id_geometria'] for r in target}
    geometries=[]
    for offset in range(0,len(ids),20):
        body=cached_json(client,folder/f'enrichment_{offset//20:06}.json',ENRICH,body=ids[offset:offset+20])
        if not isinstance(body,list): raise WorkflowError('Unexpected Obrasgov enrichment response')
        for project in body:
            for geometry in project.get('geometrias',[]):
                if geometry.get('id') not in wanted or not geometry.get('coordinates'): continue
                srid=geometry.get('srid')
                if not srid: raise WorkflowError('Enriched geometry has no SRID; do not infer CRS')
                value=gpd.GeoSeries([shapely.from_wkt(geometry['coordinates'])],crs=int(srid)).to_crs(4674).iloc[0]
                geometries.append({'id_projeto_investimento':str(project['idUnico']),'id_geometria':geometry['id'],'geometry':value,'srid':srid})
    replacement={}
    for record in geometries: replacement.setdefault(record['id_projeto_investimento'],[]).append(record['geometry'])
    result=frame.copy()
    for index,record in result.iterrows():
        values=replacement.get(str(record.id_projeto_investimento))
        if values: result.at[index,'geometry']=shapely.GeometryCollection(values)
    return result,geometries


def run(ctx,source):
    # Snapshots are immutable and resumed; use a new directory for a new harvest.
    folder=ctx.root/ctx.config['infrastructure'].get(source+'_snapshot',f'data/raw/{source}/api_snapshot')
    client=session()
    try:
        if source=='ibama':
            frames=[]
            for kind,url in IBAMA.items():
                payload=cached_json(client,folder/f'{kind}_ids.json',url+'/query',{'where':'1=1','returnIdsOnly':'true','f':'json'})
                ids=payload.get('objectIds');field=payload.get('objectIdFieldName')
                if not isinstance(ids,list) or not field: raise WorkflowError('ArcGIS object ID list missing')
                features=[]
                for offset in range(0,len(ids),200):
                    body=cached_json(client,folder/f'{kind}_{offset//200:06}.json',url+'/query',{'objectIds':','.join(map(str,ids[offset:offset+200])),'outFields':'*','outSR':4674,'f':'geojson'})
                    batch=body.get('features')
                    if not isinstance(batch,list): raise WorkflowError('ArcGIS features missing')
                    if len(batch)!=len(ids[offset:offset+200]): raise WorkflowError('ArcGIS query truncated; reduce batch size in adapter')
                    features.extend(batch)
                if features:
                    frame=gpd.GeoDataFrame.from_features(features,crs=4674)
                    if frame[field].duplicated().any(): raise WorkflowError('Duplicated ArcGIS object IDs')
                    frame['source_layer']=kind;frames.append(frame)
            if not frames: raise WorkflowError('IBAMA returned no features')
            result=gpd.GeoDataFrame(pd.concat(frames,ignore_index=True),geometry='geometry',crs=4674)
        else:
            records=pages(client,folder,'projeto-investimento')
            result=flatten_projects(records)
            metadata=pages(client,folder,'geometria')
            result,enriched=enrich_projects(result,metadata,client,folder)
            ctx.write_table(pd.DataFrame([{k:v for k,v in r.items() if k!='geometry'} for r in enriched]),'acquire-obrasgov','geometry_provenance')
        ctx.write_geo(result,'acquire-'+source,'projects')
        return ctx.report('acquire-'+source,{'records':len(result),'snapshot':str(folder.relative_to(ctx.root)),'status':'completed'})
    except Exception as error:
        ctx.report('acquire-'+source,{'status':'incomplete','error':str(error),'snapshot':str(folder.relative_to(ctx.root))})
        raise WorkflowError(f'{source} acquisition incomplete: {error}. Cached successful requests retained for resumption.') from error

"""Conference chart populations and tables with preserved missing-data rules."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from brazil_project.io import WorkflowError, lookup_keys, keys


def ntile(frame, value, n=5):
    ordered=frame.sort_values([value,'common_id'],kind='stable').copy()
    length=len(ordered)
    small, larger=divmod(length,n)
    counts=[small+int(i<larger) for i in range(n)]
    ordered['racial_quintile']=np.repeat(np.arange(1,n+1),counts)
    return ordered[['common_id','racial_quintile']]


def sanitation(frame, lookup, year):
    if year==2010:
        denominator='domicilio01_V002'
        cols=['domicilio01_V019','domicilio01_V020','domicilio01_V021','domicilio01_V023']
    else:
        denominator='domicilio01_V00001'
        cols=['domicilio02_V00312','domicilio02_V00313','domicilio02_V00314','domicilio02_V00307','domicilio02_V00308']
    counts=frame[cols].apply(pd.to_numeric,errors='coerce')
    households=pd.to_numeric(frame[denominator],errors='coerce')
    inadequate=counts.sum(axis=1,min_count=len(cols))
    usable=np.isfinite(households)&(households>0)&np.isfinite(counts).all(axis=1)&(counts>=0).all(axis=1)&(inadequate<=households)
    data=pd.DataFrame({f'id_{year}':frame.code_tract,'households':households.where(usable,0),'inadequate_sanitation':inadequate.where(usable,0)})
    keys(data,f'id_{year}')
    joined=data.merge(lookup_keys(lookup,year),on=f'id_{year}',how='left',validate='one_to_one').dropna(subset=['common_id'])
    result=joined.groupby('common_id')[['households','inadequate_sanitation']].sum().reset_index()
    result['year']=year
    return result


def populations(frames,lookups,race,income):
    common=[]
    for year in (2010,2022):
        san=sanitation(frames[year],lookups[year],year)
        racial=race[year][['common_id',f'black_brown_ratio_{year}']].rename(columns={f'black_brown_ratio_{year}':'racial_share'})
        common.append(san.merge(racial,on='common_id',validate='one_to_one'))
    urban=frames[2022][['code_tract','situacao']].rename(columns={'code_tract':'id_2022'}).merge(lookup_keys(lookups[2022],2022),on='id_2022',how='left',validate='one_to_one').dropna(subset=['common_id'])
    urban['urban']=urban.situacao.eq('Urbana').fillna(False)
    urban_ids=urban.groupby('common_id').urban.all()
    data=pd.concat(common,ignore_index=True)
    data=data[data.common_id.isin(urban_ids[urban_ids].index)&np.isfinite(data.racial_share)&data.racial_share.between(0,1)&(data.households>0)&(data.inadequate_sanitation>=0)&(data.inadequate_sanitation<=data.households)].copy()
    annual22=data[data.year==2022].copy()
    paired_ids=data.groupby('common_id').size()
    paired=data[data.common_id.isin(paired_ids[paired_ids==2].index)].merge(ntile(data[(data.year==2022)&data.common_id.isin(paired_ids[paired_ids==2].index)],'racial_share'),on='common_id',validate='many_to_one')
    summary=paired.groupby(['year','racial_quintile'])[['households','inadequate_sanitation']].sum().reset_index()
    summary['percentage']=100*summary.inadequate_sanitation/summary.households
    income_data=annual22.merge(income[['common_id','income_2022']],on='common_id',how='inner',validate='one_to_one').rename(columns={'income_2022':'income'})
    income_data=income_data[np.isfinite(income_data.income)&(income_data.income>=0)].copy()
    if income_data.empty: raise WorkflowError('No urban common areas have valid 2022 sanitation and income data')
    cutoffs=income_data.income.quantile([1/3,2/3]).to_numpy()
    if not np.isfinite(cutoffs).all() or cutoffs[0]>=cutoffs[1]: raise WorkflowError('Income cannot be split into three distinct income bands')
    income_data['sanitation_percentage']=100*income_data.inadequate_sanitation/income_data.households
    income_data=income_data.merge(ntile(annual22,'racial_share'),on='common_id',validate='one_to_one')
    income_data['income_band']=pd.cut(income_data.income,[-np.inf,*cutoffs,np.inf],labels=['Lower income','Middle income','Higher income'],right=True)
    box=income_data[income_data.racial_quintile.isin([1,5])].copy()
    return paired,annual22,summary,box,cutoffs


def plot_change(paired,summary,path):
    wide=summary.pivot(index='racial_quintile',columns='year',values='percentage').dropna()
    if wide.empty: raise WorkflowError('No paired quintiles available for chart')
    ranges=paired[paired.year==2022].groupby('racial_quintile').racial_share.agg(['min','max'])
    fig,ax=plt.subplots(figsize=(12,7))
    for q,row in wide.iterrows():
        ax.scatter(q,row[2022],color='#087F86',s=100,label='2022' if q==wide.index[0] else None,zorder=2)
        if q!=1: ax.annotate('',xy=(q,row[2022]),xytext=(q,row[2010]),arrowprops={'arrowstyle':'-|>','color':'#7FA8AD'})
        ax.scatter(q,row[2010],color='#B4516C',marker='s',s=100,label='2010' if q==wide.index[0] else None,zorder=3)
        difference=row[2022]-row[2010]
        ax.text(q,max(row[2010],row[2022])+2.2,('0.0 pp' if round(difference,1)==0 else f'{difference:+.1f} pp'),ha='center')
    ax.set_xticks(wide.index,[f'Q{q}\n{100*ranges.loc[q,"min"]:.1f}–{100*ranges.loc[q,"max"]:.1f}%' for q in wide.index])
    ax.set_ylim(0,max(60,np.ceil((wide.max().max()+7.2)/10)*10))
    ax.yaxis.set_major_formatter(PercentFormatter(100))
    ax.set_title('Inadequate sanitation in urban areas, 2010–2022\nBased on common areas with data in both census years.',loc='left',pad=20)
    ax.set_xlabel('Black/Brown population share in an area',labelpad=15)
    ax.set_ylabel('Households with inadequate sanitation (%)')
    ax.grid(axis='y',alpha=.2)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncols=2)
    fig.text(.08,.02,'Inadequate sanitation: rudimentary pit, ditch, or water-body disposal, or no bathroom or toilet.',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1))
    fig.savefig(path,dpi=180,facecolor='white'); plt.close(fig)


def plot_income(box,annual22,cutoffs,path):
    fig,axes=plt.subplots(1,3,figsize=(14,7),sharey=True)
    quintiles=annual22.merge(ntile(annual22,'racial_share'),on='common_id',validate='one_to_one').groupby('racial_quintile').racial_share.agg(['min','max'])
    annotations=[f'≤ R$ {cutoffs[0]:,.0f}',f'R$ {cutoffs[0]:,.0f}–{cutoffs[1]:,.0f}',f'> R$ {cutoffs[1]:,.0f}']
    for i,(ax,band) in enumerate(zip(axes,['Lower income','Middle income','Higher income'])):
        values=[box[(box.income_band==band)&(box.racial_quintile==q)].sanitation_percentage.to_numpy() for q in (1,5)]
        ax.boxplot(values,positions=[1,2],showfliers=False,patch_artist=True,boxprops={'facecolor':'#E5EFF0','edgecolor':'#087F86'},medianprops={'color':'#087F86'})
        ax.set_xticks([1,2],[f'Q{q} · {"Lowest" if q==1 else "Highest"}\n{100*quintiles.loc[q,"min"]:.1f}–{100*quintiles.loc[q,"max"]:.1f}%' if q in quintiles.index else f'Q{q}' for q in (1,5)])
        ax.set_title(band,pad=14); ax.text(1.5,106,annotations[i],ha='center',fontsize=9)
        ax.set_ylim(0,110); ax.set_yticks(range(0,101,20)); ax.yaxis.set_major_formatter(PercentFormatter(100)); ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Households with inadequate sanitation (%)')
    fig.suptitle('Inadequate sanitation in urban areas, 2022\nBy income band and Black/Brown population share.',x=.06,ha='left',fontsize=17)
    fig.supxlabel('Black/Brown population share in an area',y=.09)
    fig.text(.06,.025,'Boxes show the lowest and highest 2022 racial-composition quintiles; income bands use all eligible urban areas.\nInadequate sanitation: rudimentary pit, ditch, or water-body disposal, or no bathroom or toilet.',fontsize=9)
    fig.tight_layout(rect=(.02,.11,1,.9)); fig.savefig(path,dpi=180,facecolor='white'); plt.close(fig)


def run(ctx):
    frames={year:ctx.table('census',f'{year}_domicilio') for year in (2010,2022)}
    lookups={year:ctx.table('harmonisation',f'lookup_{year}') for year in (2010,2022)}
    race={year:ctx.table('indicators',f'black_brown_{year}_common') for year in (2010,2022)}
    paired,annual22,summary,box,cutoffs=populations(frames,lookups,race,ctx.table('indicators','income_2022_common'))
    for name,frame in [('paired_chart_data',paired),('eligible_2022',annual22),('year_summary',summary),('income_box_data',box)]: ctx.write_table(frame,'charts',name)
    destination=ctx.root/'outputs/figures'/ (('municipality_'+ctx.municipality) if ctx.municipality else 'brazil')
    destination.mkdir(parents=True,exist_ok=True)
    plot_change(paired,summary,destination/'urban_inadequate_sanitation_2010_2022.png')
    plot_income(box,annual22,cutoffs,destination/'urban_inadequate_sanitation_income_boxplots_2022.png')
    return ctx.report('charts',{'paired_rows':len(paired),'eligible_2022':len(annual22),'box_rows':len(box),'income_cutoffs':cutoffs.tolist(),'figures':str(destination.relative_to(ctx.root))})

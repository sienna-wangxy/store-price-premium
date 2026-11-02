"""Run from project root: python src/visualizations.py
Dependencies: numpy pandas scipy matplotlib.
Reads data/clean/prices_long.csv; writes PNG/PDF charts and summary CSV.
Estimated power is never used to filter stores.
Use --preliminary for previews made with uncorrected reference data.
"""
from pathlib import Path
import argparse
import textwrap
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ORDER = ['Bulldega', 'Durham Co-op', 'Food Lion', 'Gazelle', 'Harris Teeter', 'Whole Foods']
MIN_PRODUCTS = 5  # Same descriptive/testing convention as analysis.py; not a power threshold.


def flag(s):
    result = s.astype(str).str.lower().str.strip().map({'true':True,'false':False,'1':True,'0':False})
    if result.isna().any():
        raise ValueError('Missing or invalid boolean flags')
    return result.astype(bool)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='data/clean/prices_long.csv')
    parser.add_argument('--output-dir', default='outputs/figures')
    parser.add_argument('--preliminary', action='store_true')
    args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(args.input)
    for col in ['found','substitute','has_control']:
        d[col] = flag(d[col])
    if d.duplicated(['store','item']).any() or d[['store','item']].isna().any().any():
        raise ValueError('Require unique nonmissing store/product identifiers')
    for col in ['regular_price','control_price']:
        d[col] = pd.to_numeric(d[col], errors='raise')
    stores = [s for s in ORDER if s in set(d.store)] + sorted(set(d.store)-set(ORDER))
    # A reason for every recorded observation; absence of a row is not absence in store.
    d['status'] = np.select([~d.found, d.substitute, ~d.has_control],
                            ['No usable regular price','Excluded substitution / note','No reference price'],
                            default='Eligible')
    eligible = d.status.eq('Eligible')
    valid = np.isfinite(d.regular_price) & np.isfinite(d.control_price) & (d.regular_price>0) & (d.control_price>0)
    if (eligible & ~valid).any():
        raise ValueError('Eligible prices must be finite and positive')
    x=d[eligible].copy()
    if x.empty: raise ValueError('No eligible pairs')
    x['log_ratio']=np.log(x.regular_price/x.control_price)
    x['premium_pct']=100*np.expm1(x.log_ratio)
    rows=[]
    for s in stores:
        v=x.loc[x.store.eq(s),'log_ratio']; n=len(v)
        row={'store':s,'n_products':n,'premium_pct':100*np.expm1(v.mean()) if n else np.nan,
             'ci_low_pct':np.nan,'ci_high_pct':np.nan,'p_value':np.nan,'p_holm':np.nan}
        if n>=MIN_PRODUCTS and v.std()>0:
            margin=stats.t.ppf(.975,n-1)*stats.sem(v)
            row.update(ci_low_pct=100*np.expm1(v.mean()-margin),ci_high_pct=100*np.expm1(v.mean()+margin),
                       p_value=stats.ttest_1samp(v,0).pvalue)
        rows.append(row)
    r=pd.DataFrame(rows)
    ids=r.p_value.dropna().sort_values().index
    r.loc[ids,'p_holm']=np.minimum(1,np.maximum.accumulate(r.loc[ids,'p_value'].to_numpy()*np.arange(len(ids),0,-1)))
    r['significant_holm'] = pd.Series(pd.NA, index=r.index, dtype='boolean')
    tested = r.p_holm.notna()
    r.loc[tested, 'significant_holm'] = r.loc[tested, 'p_holm'] < 0.05
    r['outcome'] = 'Descriptive only; no valid test reported'
    r.loc[tested, 'outcome'] = 'No statistically significant difference detected'
    r.loc[tested & (r.p_holm < 0.05) & (r.premium_pct > 0), 'outcome'] = 'Significantly higher than reference'
    r.loc[tested & (r.p_holm < 0.05) & (r.premium_pct < 0), 'outcome'] = 'Significantly lower than reference'
    r.to_csv(out/'visualization_summary.csv',index=False)
    report = ('PRELIMINARY: older reference data.\n' if args.preliminary else '')
    report += 'Two-sided store-vs-reference tests; Holm family alpha = 0.05.\n'
    report += r[['store','n_products','premium_pct','p_holm','outcome']].to_string(index=False)
    report += '\n\nNo significant difference does not establish equivalent prices.\n'
    report += '50% is a planning effect, not the null or significance cutoff.\n'
    report += 'Individual 95% intervals are not adjusted for multiple comparisons.\n'
    (out/'outcomes.txt').write_text(report)
    print(report)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    prefix='PRELIMINARY — uncorrected reference data | ' if args.preliminary else ''
    common='Regular shelf prices; matched products; mixed reference sources; different product baskets across stores.\nSmall convenience sample; related products may not be independent. Results apply to sampled products and locations.'
    def save(fig,name,note):
        fig.text(.02,.025,note,fontsize=8,color='#444444',va='bottom')
        fig.savefig(out/(name+'.png'),dpi=180,facecolor='white')
        fig.savefig(out/(name+'.pdf'),facecolor='white')
        plt.close(fig)

    # Store effects: descriptive estimates retained even if no inferential test is run.
    fig,ax=plt.subplots(figsize=(12,6.5));fig.subplots_adjust(left=.23,right=.78,bottom=.23,top=.84)
    for i,row in r.iterrows():
        if np.isfinite(row.ci_low_pct):
            ax.errorbar(row.premium_pct,i,xerr=[[row.premium_pct-row.ci_low_pct],[row.ci_high_pct-row.premium_pct]],fmt='o',color='#176B77',capsize=4)
            label=f'Holm p = {row.p_holm:.3f}\n' + ('Significant difference' if row.p_holm < 0.05 else 'Not significant')
        else:
            ax.plot(row.premium_pct,i,'D',color='#777777');label='Descriptive only'
        ax.text(1.03,i,label,transform=ax.get_yaxis_transform(),va='center',fontsize=9)
    ax.axvline(0,color='#333333',lw=1)
    ax.axvline(50,color='#B66D24',ls='--',lw=1,label='50% planning target')
    ax.set_yticks(range(len(r)),[f'{v.store}  (n={v.n_products})' for v in r.itertuples()]);ax.invert_yaxis()
    ax.set_xlabel('Geometric mean premium vs reference (%)');ax.grid(axis='x',alpha=.15);ax.legend(loc='lower right',fontsize=8)
    fig.suptitle(prefix+'Price premiums and uncertainty',x=.02,ha='left',fontsize=15)
    save(fig,'store_premiums',common+'\nBars: individual 95% t intervals, not simultaneous intervals. Holm p-values cover tested stores.\n50% is a planning effect versus 0%, not a significance cutoff. Fewer than 5 pairs shown descriptively.')

    # Heatmap includes exclusions and missing records, with a separate symbol for each.
    items=sorted(d.loc[d.has_control,'item'].unique())
    wide=x.pivot(index='item',columns='store',values='premium_pct').reindex(index=items,columns=stores)
    state=d.pivot(index='item',columns='store',values='status').reindex(index=items,columns=stores)
    values=wide.to_numpy();bound=max(10,float(np.nanmax(np.abs(values))))
    cmap=plt.get_cmap('BrBG_r').copy();cmap.set_bad('#eeeeee')
    fig,ax=plt.subplots(figsize=(14,max(7,len(items)*.42+2)));fig.subplots_adjust(left=.39,right=.91,bottom=.22,top=.83)
    im=ax.imshow(np.ma.masked_invalid(values),cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound),aspect='auto')
    symbols={'No usable regular price':'M','Excluded substitution / note':'X','No reference price':'R'}
    for i in range(len(items)):
        for j in range(len(stores)):
            val=values[i,j];label=f'{val:+.0f}%' if np.isfinite(val) else symbols.get(state.iloc[i,j],'—')
            ax.text(j,i,label,ha='center',va='center',fontsize=8,color='white' if np.isfinite(val) and abs(val)>bound*.65 else '#222222')
    ax.set_yticks(range(len(items)),['\n'.join(textwrap.wrap(v,47)) for v in items],fontsize=8)
    ax.set_xticks(range(len(stores)),stores,rotation=30,ha='right')
    fig.colorbar(im,ax=ax,fraction=.035,pad=.025,label='Premium vs reference (%)')
    fig.suptitle(prefix+'Individual product price premiums',x=.02,ha='left',fontsize=15)
    save(fig,'product_heatmap',common+'\nCell values: arithmetic percentage change for each product. Rows include products with a reference in the data.\nM = no usable regular price; X = excluded substitution/note; R = no reference; — = no recorded row. Grey cells are not zero.')

    counts=pd.crosstab(d.store,d.status).reindex(stores,fill_value=0)
    categories=['Eligible','No usable regular price','Excluded substitution / note','No reference price']
    fig,ax=plt.subplots(figsize=(12,6));fig.subplots_adjust(left=.18,bottom=.26,top=.83,right=.98)
    left=np.zeros(len(stores))
    for status,color in zip(categories,['#176B77','#d9d9d9','#C78347','#9C87AA']):
        v=counts[status].to_numpy() if status in counts else np.zeros(len(stores))
        ax.barh(stores,v,left=left,label=status,color=color)
        for i,n in enumerate(v):
            if n: ax.text(left[i]+n/2,i,str(int(n)),ha='center',va='center',fontsize=9)
        left+=v
    ax.invert_yaxis();ax.set_xlabel('Recorded product rows');ax.legend(loc='upper left',bbox_to_anchor=(0,-.14),ncol=2,fontsize=9)
    fig.suptitle(prefix+'Coverage and exclusions',x=.02,ha='left',fontsize=15)
    save(fig,'product_coverage','Counts describe recorded rows, not a uniform planned basket. Missing price does not prove a product was unavailable.\nReason priority: missing regular price, then substitution/note, then missing reference. No rows are excluded based on power.')
    print('Saved PNG/PDF charts and visualization_summary.csv to',out)
    print('Rerun pilot_power.py separately for the corrected-data planning comparison; no stores are filtered by estimated power.')


if __name__=='__main__': main()

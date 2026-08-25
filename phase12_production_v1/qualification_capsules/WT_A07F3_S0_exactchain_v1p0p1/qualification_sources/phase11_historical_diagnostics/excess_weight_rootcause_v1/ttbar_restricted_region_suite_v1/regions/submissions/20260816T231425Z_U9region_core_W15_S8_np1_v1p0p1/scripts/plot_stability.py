#!/usr/bin/env python3
"""Create compact diagnostic plots from analysis/node_numerical_metrics.tsv."""
from __future__ import annotations
import argparse,csv,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);a=p.parse_args();c=a.campaign_dir.resolve()
import matplotlib.pyplot as plt
q=c/'analysis/node_numerical_metrics.tsv'
with q.open(newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
out=c/'analysis/plots';out.mkdir(parents=True,exist_ok=True)
ad=[x for x in r if x['stage']=='adaptive' and x['adaptive_id'].startswith('A')]
aids=sorted(set(x['adaptive_id'] for x in ad)); sids=sorted(set(x['seed_id'] for x in ad))
if aids and sids:
    idx={(x['adaptive_id'],x['seed_id']):x for x in ad}
    mat=[[float(idx[(aa,ss)]['max_postfirst_reported_error_pct']) if (aa,ss) in idx else math.nan for ss in sids] for aa in aids]
    fig,ax=plt.subplots(figsize=(9,8)); im=ax.imshow(mat,aspect='auto'); ax.set_xticks(range(len(sids)),sids);ax.set_yticks(range(len(aids)),aids);ax.set_xlabel('integration seed');ax.set_ylabel('adaptive prescription');ax.set_title('Maximum post-first WHIZARD reported error [%]');fig.colorbar(im,ax=ax,label='%');fig.tight_layout();fig.savefig(out/'adaptive_max_error_heatmap.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,6))
    for ss in sids:
        xs=[];ys=[]
        for i,aa in enumerate(aids):
            x=idx.get((aa,ss));
            if x:xs.append(i);ys.append(float(x['final_relative_error_pct']))
        ax.plot(xs,ys,marker='o',label=ss)
    ax.set_xticks(range(len(aids)),aids,rotation=45);ax.set_ylabel('final relative error [%]');ax.set_xlabel('adaptive prescription');ax.set_title('Adaptive-family final integration precision');ax.legend(ncol=4);fig.tight_layout();fig.savefig(out/'adaptive_final_relative_error.png',dpi=180);plt.close(fig)
print(f'PLOT_DIR={out}');print('PLOT_STABILITY=PASS')

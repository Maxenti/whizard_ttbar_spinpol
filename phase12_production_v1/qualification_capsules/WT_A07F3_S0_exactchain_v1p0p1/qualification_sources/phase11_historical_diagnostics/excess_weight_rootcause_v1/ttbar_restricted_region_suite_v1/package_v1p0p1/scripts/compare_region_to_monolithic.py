#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,math
from pathlib import Path
import sys;sys.path.insert(0,str(Path(__file__).resolve().parent));from common import write_tsv
p=argparse.ArgumentParser();p.add_argument('--region-campaign-dir',type=Path,required=True);p.add_argument('--monolithic-analysis',type=Path,required=True,help='node_numerical_metrics.tsv produced by this suite analyze_stability.py on the old 480 campaign');a=p.parse_args()
rc=a.region_campaign_dir.resolve();
with (rc/'analysis/region_sums.tsv').open(newline='') as f:rr=list(csv.DictReader(f,delimiter='\t'))
with a.monolithic_analysis.open(newline='') as f:mm=list(csv.DictReader(f,delimiter='\t'))
# recipe -> monolithic adaptive/fixed identity
mapr={'M0':('A00','F0'),'M1':('A07','F0'),'M2':('A10','F2'),'M3':('A12','F2'),'M4':('A14','F2'),'MFCC':('A07','F3')}
idx={(x['adaptive_id'],x['fixed_id'],x['seed_id']):x for x in mm if x['stage']=='fixed'};out=[]
for r in rr:
 aid,fid=mapr[r['recipe_id']];m=idx.get((aid,fid,r['seed_id']))
 if not m: continue
 rv,re=float(r['total_fb']),float(r['total_error_fb']);mv,me=float(m['final_integral_fb']),float(m['final_error_fb']);den=math.hypot(re,me);d=rv-mv
 out.append(dict(window_id=r['window_id'],recipe_id=r['recipe_id'],seed_id=r['seed_id'],region_sum_fb=rv,region_sum_error_fb=re,monolithic_fb=mv,monolithic_error_fb=me,difference_fb=d,relative_difference=d/mv if mv else math.nan,pull=d/den if den else math.nan))
write_tsv(rc/'analysis/region_vs_monolithic.tsv',out);print('COMPARE_REGION_TO_MONOLITHIC=PASS')

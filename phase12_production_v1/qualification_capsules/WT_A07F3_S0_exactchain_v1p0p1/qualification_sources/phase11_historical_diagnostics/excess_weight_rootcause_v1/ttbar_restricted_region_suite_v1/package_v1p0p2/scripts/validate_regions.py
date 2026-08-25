#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);a=p.parse_args();c=a.campaign_dir.resolve();T=json.loads((c/'frozen_config/validation_thresholds.json').read_text());q=c/'analysis/region_vs_monolithic.tsv'
if not q.is_file():raise SystemExit('ERROR: run compare_region_to_monolithic.py first')
with q.open(newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
issues=[]
for x in r:
 if abs(float(x['pull']))>T['region_closure']['max_abs_pull'] or abs(float(x['relative_difference']))>T['region_closure']['max_abs_relative_difference']:issues.append(f"{x['window_id']} {x['recipe_id']} {x['seed_id']} closure pull={x['pull']} rel={x['relative_difference']}")
out=c/'analysis/region_validation_report.txt';out.write_text('UNRESTRICTED REGION-PARTITION VALIDATION\n========================================\n'+('\n'.join(issues) if issues else 'All available seed/recipe closures satisfy the predeclared diagnostic thresholds.')+'\n')
print(out.read_text());print('REGION_VALIDATION_STATUS='+('PASS' if not issues else 'FAIL'))

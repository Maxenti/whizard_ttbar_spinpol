#!/usr/bin/env python3
"""Validate Phase 3 historical-reference capture without fabricating references."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.yamlio import load_yaml
REQUIRED={'whizard_fcc_ee_ttbar_card_or_template','fcc_ee_365gev_top_threshold_or_ttbar_sample_note','whizard_external_pythia_lhe_to_hepmc_example','legacy_local_10k_factorized_controls'}
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve()
    catalog=load_yaml(repo/'references/historical_fcc/reference_catalog.yaml'); refs=catalog.get('references',[]) or []
    observed={r.get('reference_class') for r in refs if isinstance(r,dict)}; missing=sorted(REQUIRED-observed); errors=[]; warnings=[]
    for r in refs:
        for key in ['reference_id','reference_class','source_url','retrieval_utc','local_snapshot','sha256','interpretation_note']:
            if key not in r: errors.append(f"reference {r.get('reference_id','<unknown>')} missing {key}")
        if r.get('local_snapshot') and not (repo/str(r['local_snapshot'])).is_file(): errors.append('snapshot missing: '+str(r['local_snapshot']))
    if missing: warnings.append('missing required reference classes: '+', '.join(missing))
    status='PASS' if not errors and not missing else ('FAIL' if errors else 'INCOMPLETE_REFERENCE_LOCK')
    out=write_phase_record(repo,'phase3_historical_references',status,{'missing_reference_classes':missing,'errors':errors,'warnings':warnings},['PHASE 3 HISTORICAL REFERENCE VALIDATION','='*72,f'STATUS: {status}',f'ERRORS: {len(errors)}',f'WARNINGS: {len(warnings)}'])
    print(out); return 0 if status in {'PASS','INCOMPLETE_REFERENCE_LOCK'} else 1
if __name__=='__main__': sys.exit(main())

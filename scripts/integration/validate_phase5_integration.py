#!/usr/bin/env python3
"""Validate Phase 5 static integration/seed planning."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.process_matrix import load_process_rows, expected_counts
from ttbar_spinpol.genchain.seed_policy import derive_seed
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve(); rows=load_process_rows(repo); errors=[]; seeds=[]
    for row in rows:
        seeds.append(derive_seed('full6f_365gev_ee_ttbar_spinpol_v1',row.sample_id,row.exact_subprocess_id,'qualification',0,'integration'))
        if not (repo/'sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1'/row.sample_id/row.exact_subprocess_id/'process.sin').is_file(): errors.append('missing rendered card for '+row.exact_subprocess_id)
    if len(seeds)!=len(set(seeds)): errors.append('deterministic integration seeds are not unique')
    status='PASS' if not errors else 'FAIL'; out=write_phase_record(repo,'phase5_integration_seed_static',status,{'counts':expected_counts(rows),'errors':errors},['PHASE 5 INTEGRATION/SEED STATIC VALIDATION','='*72,f'STATUS: {status}',f'ERRORS: {len(errors)}']); print(out); return 0 if not errors else 1
if __name__=='__main__': sys.exit(main())

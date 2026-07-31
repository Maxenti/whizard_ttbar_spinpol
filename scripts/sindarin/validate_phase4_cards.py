#!/usr/bin/env python3
"""Static Phase 4 validation for rendered SINDARIN cards."""
from __future__ import annotations
import argparse,re,sys
from pathlib import Path
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.process_matrix import load_process_rows, expected_counts
PLACEHOLDER=re.compile(r'\$\{[A-Z0-9_]+\}')
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve(); rows=load_process_rows(repo); outroot=repo/'sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1'; errors=[]
    for row in rows:
        card=outroot/row.sample_id/row.exact_subprocess_id/'process.sin'
        if not card.is_file(): errors.append(f'missing rendered card: {card}'); continue
        text=card.read_text()
        if PLACEHOLDER.search(text): errors.append(f'unresolved placeholder in {card}')
        if f'process {row.process_name}' not in text: errors.append(f'process line missing for {row.exact_subprocess_id}')
    if not (outroot/'rendered_cards_manifest.json').is_file(): errors.append('missing rendered_cards_manifest.json')
    status='PASS' if not errors else 'FAIL'; out=write_phase_record(repo,'phase4_sindarin_cards',status,{'counts':expected_counts(rows),'errors':errors},['PHASE 4 SINDARIN CARD VALIDATION','='*72,f'STATUS: {status}',f'ERRORS: {len(errors)}']); print(out); return 0 if not errors else 1
if __name__=='__main__': sys.exit(main())

#!/usr/bin/env python3
"""Derive deterministic generation/shower seeds."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from ttbar_spinpol.genchain.process_matrix import load_process_rows
from ttbar_spinpol.genchain.seed_policy import derive_seed
from ttbar_spinpol.genchain.yamlio import write_json
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); ap.add_argument('--shards-per-row',type=int,default=1); args=ap.parse_args(); repo=args.repo.resolve(); entries=[]; seen=set()
    if args.shards_per_row<1: raise SystemExit('ERROR: --shards-per-row must be >= 1')
    for row in load_process_rows(repo):
        for shard in range(args.shards_per_row):
            shard_id=f'{row.sample_id}__{row.exact_subprocess_id}__shard{shard:05d}'
            for stream in ['whizard_generation','pythia_shower']:
                seed=derive_seed('full6f_365gev_ee_ttbar_spinpol_v1',row.sample_id,row.exact_subprocess_id,'qualification',shard,stream)
                if seed in seen: raise SystemExit(f'ERROR: seed collision: {seed}')
                seen.add(seed); entries.append({'sample_id':row.sample_id,'exact_subprocess_id':row.exact_subprocess_id,'shard_index':shard,'shard_id':shard_id,'stream':stream,'seed':seed})
    out=repo/'inspection_outputs'/f'phase5_seed_matrix_shards{args.shards_per_row}.json'; write_json(out,{'status':'PASS','entries':entries,'unique_seeds':len(seen)}); print(out); return 0
if __name__=='__main__': sys.exit(main())

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

        # RUNTIME_PROVEN_PROCESS_LINE_LINT
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("processproc_"):
                errors.append(f"missing whitespace after process keyword in {card}: {stripped}")
            if stripped.startswith("process ") and "=>" in stripped:
                rhs = stripped.split("=>", 1)[1]
                bad_tokens = [
                    "e+", "e-", "mu+", "mu-",
                    "tau+", "tau-",
                    "nu_e", "anti_nu_e",
                    "nu_mu", "anti_nu_mu",
                    "nu_tau", "anti_nu_tau",
                    "anti_u", "anti_d", "anti_s", "anti_c", "anti_b",
                ]
                for tok in bad_tokens:
                    if tok in rhs:
                        errors.append(f"untranslated WHIZARD particle token {tok} in {card}: {stripped}")
                if " + " in rhs:
                    errors.append(f"plus-separated exact final state in {card}: {stripped}")

        # INVALID_HUMAN_PARTICLE_TOKENS
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("process ") and "=>" in stripped:
                rhs = stripped.split("=>", 1)[1]
                bad_tokens = [
                    "e+", "e-", "mu+", "mu-",
                    "tau+", "tau-",
                    "nu_e", "anti_nu_e",
                    "nu_mu", "anti_nu_mu",
                    "nu_tau", "anti_nu_tau",
                ]
                for tok in bad_tokens:
                    if tok in rhs:
                        errors.append(f"untranslated WHIZARD particle token {tok} in {card}: {stripped}")
                # Exact subprocesses should be a comma-separated particle list,
                # not a sum of alternative processes.
                if " + " in rhs:
                    errors.append(f"plus-separated exact final state in {card}: {stripped}")
        if re.search(r'(?m)^\\s*include\\s+"', text):
            errors.append(f'old WHIZARD include syntax in {card}')
        for line in text.splitlines():
            stripped=line.strip()
            if stripped.startswith('process ') and '=>' in stripped:
                final_rhs=stripped.split('=>',1)[1]
                # Exact WHIZARD final states are comma-separated; no plus-separator required here.
    if not (outroot/'rendered_cards_manifest.json').is_file(): errors.append('missing rendered_cards_manifest.json')
    status='PASS' if not errors else 'FAIL'; out=write_phase_record(repo,'phase4_sindarin_cards',status,{'counts':expected_counts(rows),'errors':errors},['PHASE 4 SINDARIN CARD VALIDATION','='*72,f'STATUS: {status}',f'ERRORS: {len(errors)}']); print(out); return 0 if not errors else 1
if __name__=='__main__': sys.exit(main())

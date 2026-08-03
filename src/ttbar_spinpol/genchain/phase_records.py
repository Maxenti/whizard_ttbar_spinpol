"""Write checksum-sealed phase records under inspection_outputs."""
from __future__ import annotations
import os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .checksums import sha256
from .yamlio import write_json

def utc_stamp() -> str: return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def git_state(repo: Path) -> dict[str, Any]:
    def run(args): return subprocess.check_output(['git','-C',str(repo),*args], text=True).strip()
    try: return {'commit':run(['rev-parse','HEAD']),'branch':run(['branch','--show-current']),'status_short':run(['status','--short'])}
    except Exception as exc: return {'error':str(exc)}

def write_phase_record(repo: Path, phase_name: str, status: str, payload: dict[str, Any],text_lines: list[str]) -> Path:
    base = repo / 'inspection_outputs'
    stamp = utc_stamp()

    # Parallel Condor shards can validate in the same second.  The old
    # timestamp-only directory name made otherwise successful jobs fail with
    # FileExistsError during final bookkeeping.  Keep the timestamp convention,
    # but add a deterministic short suffix when needed.
    for attempt in range(1000):
        suffix = '' if attempt == 0 else f'_{attempt:03d}'
        out = base / f'{phase_name}_{stamp}{suffix}'
        try:
            out.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            continue
    else:
        raise FileExistsError(f'Could not create unique phase record directory for {phase_name}_{stamp}')

    payload=dict(payload); payload.update({'status':status,'phase_name':phase_name,'repository':str(repo),'git_state':git_state(repo),'environment':{'PWD':os.getcwd(),'PYTHONPATH':os.environ.get('PYTHONPATH','')}})
    write_json(out/'validation.json', payload)
    (out/'PHASE_REPORT.txt').write_text('\n'.join(text_lines)+'\n', encoding='utf-8')
    lines=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS.txt': lines.append(f'{sha256(p)}  {p.name}')
    (out/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return out


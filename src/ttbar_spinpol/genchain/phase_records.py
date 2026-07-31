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

def write_phase_record(repo: Path, phase_name: str, status: str, payload: dict[str, Any], text_lines: list[str]) -> Path:
    out=repo/'inspection_outputs'/f'{phase_name}_{utc_stamp()}'; out.mkdir(parents=True, exist_ok=False)
    payload=dict(payload); payload.update({'status':status,'phase_name':phase_name,'repository':str(repo),'git_state':git_state(repo),'environment':{'PWD':os.getcwd(),'PYTHONPATH':os.environ.get('PYTHONPATH','')}})
    write_json(out/'validation.json', payload)
    (out/'PHASE_REPORT.txt').write_text('\n'.join(text_lines)+'\n', encoding='utf-8')
    lines=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!='SHA256SUMS.txt': lines.append(f'{sha256(p)}  {p.name}')
    (out/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return out

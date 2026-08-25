#!/usr/bin/env python3
from __future__ import annotations
import os, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import sha256, EXPECTED_UNRESTRICTED_SHA

def freeze_base(pkg:Path, repo:Path, source_card:Path, sub:Path, allow:bool=False):
    if not source_card.is_file(): raise SystemExit(f'ERROR missing source {source_card}')
    actual=sha256(source_card)
    if actual!=EXPECTED_UNRESTRICTED_SHA and not allow:
        raise SystemExit(f'ERROR unrestricted source SHA mismatch expected={EXPECTED_UNRESTRICTED_SHA} actual={actual}')
    if sub.exists() and any(sub.iterdir()): raise SystemExit(f'ERROR submission dir not empty: {sub}')
    for d in ['logs','frozen_config','frozen_source/common','scripts','records']: (sub/d).mkdir(parents=True,exist_ok=True)
    for p in (pkg/'config').glob('*'): shutil.copy2(p,sub/'frozen_config'/p.name)
    source_dir=source_card.parent
    shutil.copytree(source_dir/'common',sub/'frozen_source/common',dirs_exist_ok=True)
    if (source_dir/'render_context.json').is_file(): shutil.copy2(source_dir/'render_context.json',sub/'frozen_source/render_context.json')
    # Copy all runtime/analysis tools, so every concrete campaign is self-contained.
    for p in (pkg/'scripts').glob('*'):
        if p.is_file(): shutil.copy2(p,sub/'scripts'/p.name); os.chmod(sub/'scripts'/p.name,0o755 if p.suffix in ['.sh','.py'] else 0o644)
    return actual,source_dir

def localize_common_paths(text:str, old:Path, new:Path):
    old_s=str(old/'common'); new_s=str(new/'common')
    if old_s not in text: raise ValueError(f'expected absolute common path absent: {old_s}')
    return text.replace(old_s,new_s)

def shellq(x):
    x=str(x)
    if "'" in x: raise ValueError('single quote in path unsupported')
    return "'"+x+"'"

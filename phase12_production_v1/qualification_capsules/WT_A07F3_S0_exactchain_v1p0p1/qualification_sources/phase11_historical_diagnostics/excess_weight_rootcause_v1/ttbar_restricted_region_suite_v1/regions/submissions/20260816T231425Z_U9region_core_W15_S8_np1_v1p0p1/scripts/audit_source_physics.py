#!/usr/bin/env python3
"""Audit the frozen physics source used by a concrete suite campaign.

This script does not attempt to interpret every SINDARIN parameter.  Instead it
creates an explicit, reviewable provenance record containing hashes, the
process declaration, resonance/restriction lines, beam/ISR/polarization-like
lines, and (for restricted campaigns) a unified diff against the original
unrestricted process card after normalizing the frozen common-directory path.
"""
from __future__ import annotations
import argparse, difflib, hashlib, re
from pathlib import Path


def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()


def shell_env(path: Path) -> dict[str,str]:
    out={}
    for line in path.read_text().splitlines():
        if '=' not in line or line.lstrip().startswith('#'): continue
        k,v=line.split('=',1); v=v.strip()
        if len(v)>=2 and v[0]==v[-1] and v[0] in "'\"":v=v[1:-1]
        out[k.strip()]=v
    return out


def interesting(lines):
    rx=re.compile(r'(process\s+proc_epmum|restrictions|resonance_|sqrts|polariz|beams\s*=|gaussian|\bisr\b|isr_|\bmt\b|m_top|top_mass)',re.I)
    return [f'{i:5d}: {x}' for i,x in enumerate(lines,1) if rx.search(x)]

p=argparse.ArgumentParser()
p.add_argument('--campaign-dir',type=Path,required=True)
a=p.parse_args(); c=a.campaign_dir.resolve(); env=shell_env(c/'campaign.env')
report=[]
report.append('PHASE 11 TTBAR SUITE PHYSICS-SOURCE AUDIT')
report.append('='*43)
report.append(f'campaign_dir={c}')
orig=Path(env['ORIGINAL_SOURCE_CARD']) if env.get('ORIGINAL_SOURCE_CARD') else None
if orig and orig.is_file():
    report += [f'original_source={orig}',f'original_sha256={sha256(orig)}','', 'ORIGINAL INTERESTING LINES',*interesting(orig.read_text().splitlines())]
restricted=c/'frozen_source/process.sin'
if restricted.is_file():
    report += ['',f'frozen_source={restricted}',f'frozen_sha256={sha256(restricted)}','', 'FROZEN INTERESTING LINES',*interesting(restricted.read_text().splitlines())]
    if orig and orig.is_file():
        # Normalize source-specific common roots before diff so provenance path
        # localization does not obscure the physics patch.
        ot=orig.read_text(); ft=restricted.read_text()
        ft=ft.replace(str(c/'frozen_source/common'),str(orig.parent/'common'))
        report += ['','NORMALIZED ORIGINAL -> FROZEN DIFF']
        report += list(difflib.unified_diff(ot.splitlines(),ft.splitlines(),fromfile='unrestricted_original',tofile='frozen_campaign',lineterm=''))
# Region campaigns have multiple frozen cards. Verify no restriction slipped in.
region_cards=sorted((c/'region_sources').glob('*/*/process.sin')) if (c/'region_sources').is_dir() else []
if region_cards:
    report += ['','REGION SOURCE AUDIT',f'n_region_cards={len(region_cards)}']
    bad=[str(x) for x in region_cards if '$restrictions' in x.read_text()]
    report.append(f'region_cards_with_restrictions={len(bad)}')
    for x in bad: report.append('BAD_RESTRICTED_REGION='+x)
out=c/'records/PHYSICS_SOURCE_AUDIT.txt'; out.parent.mkdir(exist_ok=True)
out.write_text('\n'.join(report)+'\n')
print(out.read_text()); print(f'AUDIT_OUTPUT={out}')

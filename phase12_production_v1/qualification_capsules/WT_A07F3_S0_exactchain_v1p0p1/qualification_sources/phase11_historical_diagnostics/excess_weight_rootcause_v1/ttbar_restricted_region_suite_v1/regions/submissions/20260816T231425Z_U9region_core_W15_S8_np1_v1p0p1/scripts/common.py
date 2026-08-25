#!/usr/bin/env python3
"""Shared helpers for the restricted-WT and full-ME region campaigns.

The module deliberately keeps physics manipulation small and auditable:
  * the restricted source differs from the frozen unrestricted source only by
    resonance-history settings and a WT diagram restriction;
  * the region source keeps the unrestricted process and appends kinematic cuts.
"""
from __future__ import annotations
import csv, hashlib, json, math, re
from pathlib import Path
from typing import Iterable

EXPECTED_UNRESTRICTED_SHA = "2246641146c35f49a1825344343a697cbbf6542828906b10cf7c06a3f81384f9"
CANONICAL_PROCESS_RE = re.compile(r'^\s*process\s+proc_epmum\s*=\s*e1\s*,\s*E1\s*=>\s*b\s*,\s*bbar\s*,\s*E1\s*,\s*n1\s*,\s*e2\s*,\s*N2\s*$', re.M)
WT_RESTRICTION = '5+6~W+ && 7+8~W- && 3+5+6~t && 4+7+8~tbar'
ROW_RE = re.compile(r'^\s*(?P<iteration>\d+)\s+(?P<calls>\d+)\s+(?P<integral>[+-]?\d+(?:\.\d*)?[Ee][+-]?\d+)\s+(?P<error>[+-]?\d+(?:\.\d*)?[Ee][+-]?\d+)\s+(?P<errpct>[+-]?\d+(?:\.\d*)?)\s+(?P<acc>[+-]?\d+(?:\.\d*)?)\*?\s+(?P<eff>[+-]?\d+(?:\.\d*)?)(?P<tail>.*)$')

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
    return h.hexdigest()

def read_tsv(p: Path):
    with p.open(newline='') as f: return list(csv.DictReader(f, delimiter='\t'))

def write_tsv(p: Path, rows: list[dict], fields=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    if fields is None: fields=list(rows[0].keys()) if rows else []
    with p.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)

def assert_canonical_process(text: str):
    hits=CANONICAL_PROCESS_RE.findall(text)
    if len(hits)!=1:
        raise ValueError('Expected exactly one canonical proc_epmum declaration with final-state order b,bbar,E1,n1,e2,N2; refusing index-based physics patch.')

def make_restricted_wt(text: str) -> str:
    assert_canonical_process(text)
    if '$restrictions' in text: raise ValueError('Source already contains $restrictions; refusing double patch.')
    line='process proc_epmum = e1, E1 => b, bbar, E1, n1, e2, N2'
    repl=line + ' {$restrictions = "' + WT_RESTRICTION + '"}'
    out=CANONICAL_PROCESS_RE.sub(repl, text, count=1)
    # Add resonance handling immediately before process declaration. These are
    # the settings used by the FCC Winter2023 top card.
    block='?resonance_history = true\nresonance_on_shell_limit = 10\nresonance_background_factor = 0\n\n'
    out=out.replace(repl, block+repl, 1)
    return out

def combine_particles(tokens: str) -> str:
    """Return a SINDARIN particle expression combining >=2 particles.

    WHIZARD's ``combine`` particle expression is binary: its grammar takes
    exactly two particle expressions.  For an n-body invariant mass we must
    therefore build a nested binary expression.  For example,

        b,E1,n1  ->  combine[combine[b,E1],n1]

    Four-vector addition is associative, so the left-associated nesting does
    not change the intended invariant mass.  Keeping this construction in one
    helper also prevents reintroducing the invalid ``combine[a,b,c]`` syntax.
    """
    parts=[x.strip() for x in tokens.split(',') if x.strip()]
    if len(parts) < 2:
        raise ValueError(f'combine_particles requires at least two particles: {tokens!r}')
    expr=f'combine[{parts[0]},{parts[1]}]'
    for part in parts[2:]:
        expr=f'combine[{expr},{part}]'
    return expr

def bin_cut(tokens: str, which: str, low: float, high: float) -> str:
    sel=f'[{combine_particles(tokens)}]'
    if which=='L': return f'all M < {low:.8g} GeV {sel}'
    if which=='I': return f'all M >= {low:.8g} GeV {sel} and all M < {high:.8g} GeV {sel}'
    if which=='H': return f'all M >= {high:.8g} GeV {sel}'
    raise ValueError(which)

def region_cut(region_id: str, low: float, high: float) -> str:
    if len(region_id)!=2 or any(x not in 'LIH' for x in region_id): raise ValueError(region_id)
    # Current external ordering: b,bbar,E1,n1,e2,N2.  Thus t-side=b+e+nu_e
    # and antitop-side=bbar+mu-+numubar.
    a=bin_cut('b,E1,n1', region_id[0], low, high)
    b=bin_cut('bbar,e2,N2', region_id[1], low, high)
    return f'cuts = {a} and {b}'

def make_region_source(text: str, include_path: str) -> str:
    assert_canonical_process(text)
    if '$restrictions' in text: raise ValueError('Region source must be unrestricted; found $restrictions.')
    marker='process proc_epmum = e1, E1 => b, bbar, E1, n1, e2, N2'
    return text.replace(marker, marker+'\n\ninclude("'+include_path+'")', 1)

def parse_log(path: Path):
    rows=[]
    if not path.is_file(): return rows
    for ln,line in enumerate(path.read_text(errors='replace').splitlines(),1):
        m=ROW_RE.match(line)
        if not m: continue
        tail=m.group('tail').strip().split()
        integral=float(m.group('integral')); error=float(m.group('error'))
        # WHIZARD aggregate rows have extra columns after efficiency; ordinary
        # iteration rows do not. Keep both, but mark them explicitly.
        rows.append(dict(line_number=ln, iteration=int(m.group('iteration')), calls=int(m.group('calls')),
            integral_fb=integral,error_fb=error,relative_error=abs(error/integral) if integral else math.inf,
            reported_err_pct=float(m.group('errpct')),accuracy=float(m.group('acc')),efficiency_pct=float(m.group('eff')),
            row_kind='aggregate' if len(tail)>=2 else 'iteration',raw_line=line.strip()))
    return rows

def numerical_metrics(rows: list[dict]):
    its=[r for r in rows if r['row_kind']=='iteration']
    agg=[r for r in rows if r['row_kind']=='aggregate']
    if not its: return {}
    final=(agg[-1] if agg else its[-1])
    jumps=[]
    for a,b in zip(its,its[1:]):
        den=math.hypot(a['error_fb'],b['error_fb'])
        jumps.append(abs(b['integral_fb']-a['integral_fb'])/den if den else math.inf)
    post=its[1:] or its
    return {
      'n_iteration_rows':len(its),'n_aggregate_rows':len(agg),
      'final_integral_fb':final['integral_fb'],'final_error_fb':final['error_fb'],
      'final_relative_error_pct':100*final['relative_error'],
      'max_postfirst_reported_error_pct':max(r['reported_err_pct'] for r in post),
      'max_accuracy':max(r['accuracy'] for r in its),
      'min_efficiency_pct':min(r['efficiency_pct'] for r in its),
      'max_normalized_iteration_jump':max(jumps) if jumps else 0.0,
    }

def weighted_combine(values):
    vals=[x for x in values if x and x[1]>0]
    if not vals: return (math.nan,math.nan)
    sw=sum(1/e**2 for _,e in vals)
    return (sum(v/e**2 for v,e in vals)/sw, math.sqrt(1/sw))

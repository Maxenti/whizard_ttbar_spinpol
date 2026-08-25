#!/usr/bin/env python3
from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from common import make_restricted_wt,make_region_source,region_cut,WT_RESTRICTION
BASE='''include("/x/common/model.inc")\ninclude("/x/common/beams.inc")\nprocess proc_epmum = e1, E1 => b, bbar, E1, n1, e2, N2\ninclude("/x/common/integration.inc")\ninclude("/x/common/event_output.inc")\n'''
r=make_restricted_wt(BASE);assert WT_RESTRICTION in r and '?resonance_history = true' in r
u=make_region_source(BASE,'/x/common/region_cuts.inc');assert '$restrictions' not in u and 'region_cuts.inc' in u
cuts={x:region_cut(x,157.5,187.5) for x in ['LL','LI','LH','IL','II','IH','HL','HI','HH']};assert len(set(cuts.values()))==9;assert 'GeV [combine[combine[b,E1],n1]]' in cuts['II'] and 'GeV [combine[combine[bbar,e2],N2]]' in cuts['II']
print('TEST_SUITE=PASS')

# Regression test for the restricted Condor DAG output-root contract.  The
# submit descriptors consume $(node_output_root); every DAG node must define it.
import subprocess, tempfile
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    srcdir=td/'src'; (srcdir/'common').mkdir(parents=True)
    # prepare_restricted_scan only needs the source tree to be structurally
    # copyable.  The runtime preflight tests the real CERN source separately.
    for name in ['model.inc','beams.inc','isr.inc','polarization.inc','integration.inc','event_output.inc','parameters.inc','diagnostics.inc']:
        (srcdir/'common'/name).write_text('# test\n')
    source=srcdir/'process.sin'
    source.write_text(
        f'include("{srcdir}/common/model.inc")\n'
        f'include("{srcdir}/common/beams.inc")\n'
        f'include("{srcdir}/common/isr.inc")\n'
        f'include("{srcdir}/common/polarization.inc")\n'
        'process proc_epmum = e1, E1 => b, bbar, E1, n1, e2, N2\n'
        f'include("{srcdir}/common/integration.inc")\n'
        f'include("{srcdir}/common/event_output.inc")\n'
    )
    sub=td/'sub'; out=td/'out'; repo=td/'repo'; repo.mkdir()
    subprocess.run([
        sys.executable, str(ROOT/'scripts/prepare_restricted_scan.py'),
        '--package-root', str(ROOT), '--repo', str(repo),
        '--source-card', str(source), '--submission-dir', str(sub),
        '--output-root', str(out), '--allow-source-sha-mismatch'
    ], check=True, stdout=subprocess.DEVNULL)
    dag=(sub/'campaign.dag').read_text().splitlines()
    jobs=[ln.split()[1] for ln in dag if ln.startswith('JOB ')]
    vars_by_node={}
    for ln in dag:
        if ln.startswith('VARS '):
            node=ln.split()[1]
            vars_by_node[node]=ln
    assert len(jobs)==496
    assert set(jobs)==set(vars_by_node)
    missing=[n for n in jobs if 'node_output_root=' not in vars_by_node[n]]
    assert not missing, f'nodes missing node_output_root: {missing[:10]}'
    for submit_name in ['adaptive_parent.sub','fixed_child.sub','full_control.sub']:
        txt=(sub/submit_name).read_text()
        assert '$(node_output_root)' in txt
    print('RESTRICTED_CONDOR_OUTPUT_ROOT_CONTRACT=PASS')

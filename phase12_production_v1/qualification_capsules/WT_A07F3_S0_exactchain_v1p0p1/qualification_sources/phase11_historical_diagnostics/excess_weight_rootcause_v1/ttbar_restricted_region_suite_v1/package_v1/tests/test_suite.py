#!/usr/bin/env python3
from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from common import make_restricted_wt,make_region_source,region_cut,WT_RESTRICTION
BASE='''include("/x/common/model.inc")\ninclude("/x/common/beams.inc")\nprocess proc_epmum = e1, E1 => b, bbar, E1, n1, e2, N2\ninclude("/x/common/integration.inc")\ninclude("/x/common/event_output.inc")\n'''
r=make_restricted_wt(BASE);assert WT_RESTRICTION in r and '?resonance_history = true' in r
u=make_region_source(BASE,'/x/common/region_cuts.inc');assert '$restrictions' not in u and 'region_cuts.inc' in u
cuts={x:region_cut(x,157.5,187.5) for x in ['LL','LI','LH','IL','II','IH','HL','HI','HH']};assert len(set(cuts.values()))==9;assert 'GeV [combine[b,E1,n1]]' in cuts['II'] and 'GeV [combine[bbar,e2,N2]]' in cuts['II']
print('TEST_SUITE=PASS')

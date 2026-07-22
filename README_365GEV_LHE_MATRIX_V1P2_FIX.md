# 365 GeV LHE matrix v1p2 Condor submit-path fix

This additive overlay corrects the v1p1 CERN Condor stream-path patch.

The v1p1 script resolved the repository `runs` symlink and wrote literal
`/eos/...` paths into the submit descriptor. Standard CERN batch schedds reject
literal EOS paths in submit files. The corrected script keeps the logical
AFS-visible path, such as

`/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/...`

in `executable`, `arguments`, `initialdir`, `output`, `error`, `log`, and the
queue-file path. Those logical paths may still resolve through the repository's
`runs` symlink to EOS when accessed.

The physical EOS target is printed for diagnostics only and is never embedded
in the submit descriptor. The script also rejects direct `/eos/...` invocation
and performs a final descriptor scan before submission.

This overlay changes no physics configuration, SINDARIN input, seed, event
count, generated LHE product, or campaign validation rule.

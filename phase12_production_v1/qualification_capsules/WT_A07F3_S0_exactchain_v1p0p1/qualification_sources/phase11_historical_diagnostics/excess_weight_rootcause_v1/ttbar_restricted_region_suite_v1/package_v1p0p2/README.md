> **v1.0.2 Condor hotfix:** the restricted DAG now defines `node_output_root` for every parent, fixed child, and FCC legacy-control node. v1.0.1 fixed the region three-body invariant-mass `combine` syntax. See `RESTRICTED_OUTPUT_ROOT_HOTFIX.md` and `REGION_SYNTAX_HOTFIX.md`.

# Phase 11 ttbar restricted + unrestricted-region suite v1

This package extends the existing Phase-11 WHIZARD 365 GeV full6f work without replacing or mutating the live 480-node unrestricted campaign.

It provides two independent campaigns:

1. **Restricted WT qualification**: eight frozen integration seeds, A00--A14 adaptive prescriptions, F0/F1/F2 fixed descendants, the exact FCC Winter2023 iteration-count suffix F3 for A07, and eight current-WHIZARD VAMP+TAO controls. The primary source modification is only the explicit W+/W-/t/tbar resonance restriction plus resonance-history settings.
2. **Unrestricted region partition**: keeps the complete unrestricted six-fermion process and partitions phase space into nine mutually exclusive top/antitop invariant-mass cells. It uses the same seed IDs and A/F IDs as the monolithic 480 scan, making direct paired comparisons possible.

The package contains preparation, DAG submission, live-tail, collection, numerical-stability analysis, restricted validation, region closure, monolithic comparison, and closeout tooling.

**Never interpret `STATUS.txt=PASS` as numerical qualification.** It is a technical execution/artifact status. `analyze_stability.py` adds a separate numerical screen. Final production still requires generation-envelope stress, independent-grid event-level physics comparison, and an exact final-recipe rehearsal.

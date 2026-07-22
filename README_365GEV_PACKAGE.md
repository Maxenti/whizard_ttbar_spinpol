# 365 GeV paper-spin smoke package v1

Additive first-stage package for the canonical repository:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

It prepares and validates one 365 GeV WHIZARD LHE smoke sample while preserving
the frozen 500 GeV baseline.

Install at the repository root with `tar --strip-components=1`, run the tests,
then execute `scripts/qis/run_365GeV_smoke.sh --prepare-only` before the full
smoke run. Full instructions are in:

```text
docs/qis/paper_spin_365GeV_campaign.md
```

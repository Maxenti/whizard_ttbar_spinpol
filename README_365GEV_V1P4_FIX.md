# 365 GeV smoke v1p4 validator fix

This additive overlay fixes the post-WHIZARD LHE threshold validator.

The repository's canonical `qis_ttbar.models.FourVector` exposes the energy
component as `e`, whereas the original Stage-1 validator assumed `energy`.
The new adapter accepts both conventions and keeps `px`, `py`, and `pz`
strictly required.

No generator inputs, event files, physics configs, or frozen 500 GeV products
are modified. The already-generated 200-event LHE smoke sample can be audited
again without rerunning WHIZARD.

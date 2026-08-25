# Physics contract

## Restricted WT signal

Canonical external state remains `e1,E1 => b,bbar,E1,n1,e2,N2`. The package verifies that exact ordering before adding

`$restrictions = "5+6~W+ && 7+8~W- && 3+5+6~t && 4+7+8~tbar"`

and the FCC resonance-history settings. No arbitrary invariant-mass cut is applied to the restricted primary sample. The current project beam polarization, ISR, model, masses/widths, and other common includes are inherited from the frozen source tree.

This should be described as an **LO hard-process, spin-correlated, beam-polarized ttbar->6f signal sample with the current ISR/beam treatment**, not as the complete inclusive six-fermion prediction.

## Unrestricted region partition

No diagram restriction is introduced. Each event/integration point remains governed by the full unrestricted matrix element. Define

- `m_plus = M(b,E1,n1)`
- `m_minus = M(bbar,e2,N2)`

and classify each mass L/I/H around `m0 +/- Delta`. The nine Cartesian cells LL...HH are disjoint. Their integrated cross sections must close to the monolithic unrestricted result within uncertainty.

Aggregate labels are kinematic only:
- DR = II
- SR_PLUS = IL + IH
- SR_MINUS = LI + HI
- NR = LL + LH + HL + HH

They are **not** diagram labels and preserve interference inside every cell.

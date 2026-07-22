# 365 GeV smoke package v1p1 corrective overlay

The original v1 pilot candidate order allowed a non-ISR 500 GeV SINDARIN to be
selected before the intended ISR source. The prepared file was therefore named
as an ISR sample while retaining `isr_enabled=false`. It also carried duplicate
stale metadata for the old seed, event count, decay label, and 500 GeV scope.

This overlay makes the source and prepared-input contracts strict:

1. only a source declaring `isr_enabled=true` is eligible;
2. the source must identify the qualified 500 GeV ISR sample;
3. explicit `t -> b e+ nu_e` and `tbar -> bbar mu- anti-nu_mu` processes are
   required;
4. controlled metadata are removed and rewritten exactly once;
5. an independent prepared-input validator runs before WHIZARD;
6. non-ISR templates are excluded from automatic candidate selection.

The overlay does not modify the frozen 500 GeV source and does not execute
WHIZARD during installation.

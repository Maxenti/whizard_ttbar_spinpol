# Installation

Extract over the repository root with `--strip-components=1`, rerun the package
tests, locate the authoritative 500 GeV ISR SINDARIN, and pass it explicitly to
`run_365GeV_smoke.sh --prepare-only --template ...`.

Do not run WHIZARD until `prepared_input_validation.json` reports `pass` and the
prepared input contains one `! META isr_enabled=true` line and no
`isr_enabled=false` line.

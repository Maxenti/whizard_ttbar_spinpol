# Phase 11 resonance/restriction matrix closeout

Campaign:
20260816T190807Z_resonance_envelope_matrix_S0_np1

HTCondor:
- cluster: 20200513
- schedd: bigbird08.cern.ch
- jobs: 6
- all six terminated normally with return value 0

Runtime success convention:
This diagnostic predates the newer STATUS.txt convention.
Successful outputs contain:
- EXECUTION_SUCCESS
- SUCCESS
- integration_artifacts.tar.gz

Final newly evaluated integration results:

| case | sigma [fb] | error [fb] |
|---|---:|---:|
| U_2M | 12.073541 | 0.0280 |
| W_2M | 12.032427 | 0.0325 |
| W_G2 | 12.011960 | 0.0359 |
| WT_2M | 11.503066 | 0.0140 |
| WT_G2 | 11.460196 | 0.0256 |
| WT_W23 | 11.498815 | 0.0118 |

Key numerical comparisons:

U_2M vs W_2M:
- difference = -0.041114 fb
- relative difference = -0.341%
- approximately -0.96 sigma

W_2M vs WT_2M:
- difference = -0.529361 fb
- relative difference = -4.399%
- approximately -14.96 sigma

U_2M vs WT_2M:
- difference = -0.570475 fb
- relative difference = -4.725%
- approximately -18.22 sigma

W_G2 vs WT_G2:
- relative difference = -4.593%
- approximately -12.51 sigma

WT_G2 vs WT_2M:
- relative difference = +0.374%
- approximately +1.47 sigma

WT_W23 vs WT_2M:
- difference = -0.004251 fb
- relative difference = -0.037%
- approximately -0.23 sigma

Interpretation:

1. W-only restriction is compatible with the unrestricted total rate at
   the precision of this S0 diagnostic.

2. Adding explicit top/antitop restrictions changes the physics definition
   materially, lowering the integrated rate by approximately 4.5--4.7%.
   WT therefore must not be treated as an unrestricted-equivalent sample.

3. WT is numerically much better behaved in this diagnostic. In particular,
   WT_W23 remains stable through 10 x 100k adaptive iterations followed by
   10 x 200k fixed iterations and agrees extremely well with WT_2M.

4. The result supports the hypothesis that the unrestricted instability is
   tied strongly to the available amplitude/resonance structure rather than
   merely to total call count or VAMP2 itself.

5. This is a single-seed diagnostic and is not by itself a production
   qualification. The 8-seed 496-node restricted-WT campaign remains the
   authoritative multi-seed qualification test.

Status:
COMPLETE / VALIDATED DIAGNOSTIC

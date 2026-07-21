# WHIZARD \(t\bar t\) Spin-15 Validation: What Was Checked and Why

## Purpose of the validation chain

The objective was not merely to confirm that output files existed. The validation had to establish that:

1. the intended beam helicities and decay configurations were actually generated;
2. the samples contained the intended top and antitop polarization information;
3. the spin-correlated samples contained genuine connected \(t\bar t\) correlations;
4. the isotropic samples behaved as appropriate null controls;
5. PYTHIA showering and HepMC conversion preserved the relevant truth-level structure;
6. the samples were complete, non-overlapping, reproducible, and suitable for the intended \(t\bar t\) analysis path.

There were **160,000 unique generated events**:

- 8 spin-correlated samples \(\times\) 10,000 events;
- 8 isotropic-control samples \(\times\) 10,000 events.

Each event was analyzed at both LHE and HepMC level, giving 320,000 analysis records.

# Validation steps

## 1. Production-configuration audit

Every intended sample was checked for the correct:

- initial state: \(e^+e^-\) or \(\mu^+\mu^-\);
- beam helicity: LR100 or RL100;
- decay mode: `epmum` or `mupem`;
- spin treatment: spin-correlated or isotropic;
- center-of-mass energy: 500 GeV;
- event count: 10,000.

### Why this was necessary

A file or plot labeled “LR100” is not proof that the generator actually used LR100 beams. This audit connected every analyzed sample to its production configuration and prevented mislabeled, missing, or incorrectly configured samples from passing the physics analysis.

## 2. Shard and shower integrity

Each 10,000-event LHE sample was split into:

\[
10\ \text{shards}\times1000\ \text{events}.
\]

For every shard, the workflow checked:

- source-event range;
- input checksum;
- exactly 1,000 source LHE events;
- exactly 1,000 canonicalized events;
- exactly 1,000 explicit-\(W\) events;
- exactly 2,000 inserted \(W\) resonances;
- exactly 1,000 accepted PYTHIA events;
- zero failed PYTHIA events;
- deterministic and unique random seed;
- valid output metadata.

The merged HepMC files were then verified to contain exactly 10,000 events each.

### Why this was necessary

Without these checks, merged samples could contain:

- duplicated events;
- missing ranges;
- overlapping shards;
- fewer events than expected;
- incorrect source files;
- silently failed PYTHIA events.

Physics coefficients are not meaningful unless the underlying sample assembly is correct.

## 3. HepMC run-information validation

The ten independently produced HepMC shards for each sample carried separate `GenRunInfo` objects. HepMC warned during merging that only the first such object would be serialized.

The workflow verified that the run-information contents were equivalent and then normalized the merged events to a single canonical run-information object.

### Why this was done

The warning was probably harmless for particle kinematics, but run-level metadata can include weight names and generator information. The correct procedure was to verify equivalence rather than suppressing the warning blindly.

## 4. Truth-topology validation

PYTHIA represents tops, antitops, and \(W\) bosons with multiple status copies. It also introduces:

- QCD radiation;
- photon radiation;
- photon conversions;
- heavy-flavour decays;
- secondary leptons.

The HepMC truth parser was corrected to:

1. find a complete semileptonic top and antitop chain;
2. preserve the hard-process top copy when it contains the full decay chain;
3. follow the same-PDG \(W\)-status-copy chain;
4. select the charged lepton and neutrino from the same direct \(W\)-decay vertex;
5. require flavour consistency:
   \[
   e^\pm\leftrightarrow\nu_e,\qquad
   \mu^\pm\leftrightarrow\nu_\mu,\qquad
   \tau^\pm\leftrightarrow\nu_\tau;
   \]
6. reject photon-conversion and heavy-flavour leptons as primary top-decay analyzers.

### Why this mattered

In 15 spin-correlated events, the earlier parser selected a low-energy conversion electron instead of the real primary electron or muon from the terminal \(W\) decay.

For example, the physical decay was:

\[
W^-\rightarrow\mu^-\bar\nu_\mu,
\]

but a conversion electron elsewhere in the descendant tree was encountered first.

That would have contaminated the angular observables and could have created false polarization or correlation effects. After correction, all 160,000 HepMC events had the expected forced-decay classification.

# How the Spin-15 coefficients were calculated

## Event basis

For every event, an orthonormal basis was constructed in the \(t\bar t\) system:

- \(\hat{k}\): along the top-quark direction;
- \(\hat{n}\): normal to the production plane;
- \(\hat{r}\): the remaining in-plane transverse direction.

Schematically,

\[
\hat n \propto \hat p_{\rm beam}\times\hat k,
\qquad
\hat r = \hat n\times\hat k,
\]

with a fixed orientation convention used consistently for every dataset.

The positive lepton was boosted into the top rest frame and the negative lepton into the antitop rest frame. Their direction cosines were projected onto the three axes:

\[
a_i=\hat\ell_+\cdot\hat i,
\qquad
b_j=\hat\ell_-\cdot\hat j,
\qquad
i,j\in\{k,r,n\}.
\]

These angular analyzers lie in the interval \([-1,1]\).

## Six polarization coefficients

The six single-spin analyzers were:

\[
B_{1k},B_{1r},B_{1n},
B_{2k},B_{2r},B_{2n}.
\]

They were extracted from first angular moments:

\[
B_{1i}=3\langle a_i\rangle,
\qquad
B_{2j}=3\langle b_j\rangle,
\]

using the fixed sign convention of the analysis.

For example,

\[
\langle a_k\rangle=-0.168593
\]

gave

\[
B_{1k}=3(-0.168593)=-0.505778.
\]

The factor of three follows from the normalized linear angular distribution over \([-1,1]\).

## Nine correlation coefficients

The nine two-spin coefficients were:

\[
C_{kk},C_{rr},C_{nn},
C_{kr},C_{rk},
C_{kn},C_{nk},
C_{rn},C_{nr}.
\]

They were extracted from mixed angular moments:

\[
C_{ij}=9\langle a_i b_j\rangle,
\]

again using the pipeline’s fixed sign convention.

The factor of nine follows from the mixed second moment of the normalized two-angle distribution.

Together, the six \(B\) values and nine \(C\) values form the **Spin-15 coefficient set**.

## Statistical uncertainties

For each observable, the code calculated:

- event count;
- sum of weights;
- effective event count;
- mean;
- standard deviation;
- standard error of the mean;
- coefficient;
- coefficient uncertainty.

For the polarization coefficients,

\[
\sigma(B_i)=3\,\sigma(\langle a_i\rangle).
\]

For the correlation coefficients,

\[
\sigma(C_{ij})=9\,\sigma(\langle a_i b_j\rangle).
\]

Comparisons were then expressed as significances:

\[
z=
\frac{X_1-X_2}
{\sqrt{\sigma_1^2+\sigma_2^2}}.
\]

# Why connected correlations were used

A raw \(C_{ij}\) coefficient can be nonzero partly because both the top and antitop are individually polarized.

To isolate genuine two-particle correlation, the workflow formed:

\[
D_{ij}=C_{ij}-B_{1i}B_{2j}.
\]

The product \(B_{1i}B_{2j}\) is the factorized contribution expected from two independently polarized particles.

### Why this is more meaningful

If

\[
B_{1i}\neq0,\qquad B_{2j}\neq0,
\]

then their product can contribute to \(\langle a_i b_j\rangle\) even without genuine connected spin correlation. Comparing \(D_{ij}\) between spin-correlated and isotropic samples is therefore more physically discriminating than comparing raw \(C_{ij}\) alone.

# Physics validation tests

## 1. LR100 versus RL100 in spin-correlated samples

For each initial state, decay channel, and LHE/HepMC stage, the six \(B\) coefficients were compared between LR100 and RL100.

The gate required at least one component to differ by more than:

\[
5\sigma.
\]

The observed maximum separations were approximately:

\[
52\text{–}54\sigma.
\]

The dominant components were generally:

- \(B_{2r}\) for `epmum`;
- \(B_{1r}\) for `mupem`.

### What this proves

Changing the beam helicities creates a very large and reproducible change in the top or antitop polarization measured by the charged leptons.

This is the primary evidence that beam polarization was correctly implemented.

## 2. Isotropic-decay null control

The LR100/RL100 comparison was also examined for the isotropic samples.

The largest ISO separation was only about:

\[
0.9\text{–}2.0\sigma.
\]

These groups were marked **not applicable**, not failed.

### Why this is expected

The isotropic samples retain the production kinematics but replace spin-aware decays with isotropic decays. The charged leptons therefore lose their polarization-analyzer role.

The expected result is:

\[
B_{1i}\approx0,\qquad B_{2i}\approx0,
\]

with no significant LR/RL analyzer separation.

### What this proves

This is a null test. It shows that the strong LR/RL signal in the spin-correlated samples comes from transmitted spin information rather than from sample kinematics, file naming, or analysis bias.

## 3. Spin-correlated versus isotropic connected correlations

For every matched configuration, \(D_{ij}\) was compared between the spin-correlated and isotropic samples.

There were 16 comparison groups:

\[
2\ \text{stages}
\times
2\ \text{initial states}
\times
2\ \text{polarizations}
\times
2\ \text{decay channels}.
\]

All 16 passed the requirement that at least one connected component differ by more than \(5\sigma\).

### What this proves

The spin-correlated samples contain genuine \(t\bar t\) correlation structure that is absent in the isotropic controls.

This is the central evidence that spin correlations were correctly implemented.

## 4. `epmum` versus `mupem` consistency

The two forced channels exchange which top produces the electron and which produces the muon.

The coefficients were compared after applying the correct charge, top/antitop, and basis conventions.

All 16 comparison groups passed.

### Why this was necessary

This test detects:

- lepton-charge mistakes;
- top/antitop swaps;
- sign errors in the basis;
- decay-channel-specific parser problems.

A correct result should not depend arbitrarily on whether the electron came from the top or antitop.

## 5. LHE versus HepMC preservation

Every LHE coefficient was compared with the corresponding HepMC coefficient.

The diagnostic thresholds were:

\[
|\Delta X|>0.02,
\qquad
|z|>5.
\]

The final policy was:

- **pass:** neither threshold exceeded;
- **warning:** exactly one threshold exceeded;
- **fail:** both thresholds exceeded.

The result was:

- 184 direct passes;
- 56 warnings;
- 0 failures.

The largest significance was only approximately:

\[
2.14\sigma.
\]

The warnings were concentrated in:

\[
B_{1k},B_{2k},C_{kk},C_{kr},C_{rk}.
\]

### Why these components move

The \(\hat{k}\) direction is tied to the reconstructed top direction. Shower radiation and recoil can move this direction slightly, causing migration in \(k\)-axis observables without erasing the spin information.

### What this proves

The essential polarization and correlation structure survives PYTHIA showering and HepMC conversion.

The validation does not require every coefficient to be numerically identical before and after showering.

# Why the coefficients were presented this way

## Coefficient forest plots

The six \(B\) coefficients were displayed together for LR100 and RL100.

This makes the following visible simultaneously:

- sign;
- magnitude;
- uncertainty;
- LR/RL separation;
- LHE/HepMC preservation.

This is stronger than showing only one selected coefficient.

## Representative angular distributions

The strongest analyzers, such as \(b_{1r}\) and \(b_{2r}\), were shown as normalized angular distributions.

The coefficient is only the first moment of a distribution. The distribution shows that the coefficient difference arises from a real shape or slope difference rather than from a numerical accident.

## Isotropic null-control plots

The same \(B\)-coefficient views were shown for isotropic samples.

A positive signal is more convincing when a control sample removes the relevant physical mechanism and correspondingly removes the observed signal.

## Connected-correlation matrices

The nine \(D_{ij}\) coefficients naturally form a \(3\times3\) matrix:

\[
D=
\begin{pmatrix}
D_{kk}&D_{kr}&D_{kn}\\
D_{rk}&D_{rr}&D_{rn}\\
D_{nk}&D_{nr}&D_{nn}
\end{pmatrix}.
\]

A heatmap preserves the tensor structure and shows:

- dominant directions;
- sign patterns;
- off-diagonal correlations;
- spin-correlated versus isotropic differences.

## LHE-versus-HepMC scatter plots

Matched coefficients were plotted as:

\[
X_{\rm HepMC}
\quad\text{versus}\quad
X_{\rm LHE},
\]

with a \(y=x\) reference and absolute-shift bands.

This provides a global view of all coefficient comparisons and reveals:

- overall preservation;
- systematic offsets;
- outliers;
- coefficient families most sensitive to showering.

## Summary tables

The tables provide exact and auditable numerical evidence for:

- production configuration;
- LR/RL significance;
- SC/ISO significance;
- decay-flavour consistency;
- LHE/HepMC preservation;
- final gate counts.

Plots establish patterns visually; tables preserve the exact numbers.

# What the results should show

## Evidence for beam polarization

A convincing polarization validation should show:

1. LR100 and RL100 are configured with opposite beam helicities.
2. Spin-correlated samples have strongly different \(B\) vectors:
   \[
   z_{\rm LR/RL}\gg5.
   \]
3. The pattern appears for both \(e^+e^-\) and \(\mu^+\mu^-\).
4. It appears in both forced decay channels.
5. It survives from LHE to HepMC.
6. Isotropic controls have:
   \[
   B_i\approx0
   \]
   and no significant LR/RL analyzer separation.

The validated samples satisfy all six requirements.

## Evidence for spin correlation

A convincing correlation validation should show:

1. SC and ISO samples use matched production settings but different decay spin treatments.
2. Connected correlations are formed:
   \[
   D_{ij}=C_{ij}-B_{1i}B_{2j}.
   \]
3. SC and ISO differ significantly in at least one \(D_{ij}\) component for every matched group.
4. This occurs for both initial states, both helicities, both decay channels, and both LHE and HepMC.
5. `epmum` and `mupem` give convention-consistent results.
6. The effect survives showering.

The result was:

\[
16/16
\]

SC-versus-ISO groups passing.

# Final interpretation

The validation establishes that the samples are suitable for the intended \(t\bar t\) analysis because:

- their production configurations and event counts are correct;
- LR100 and RL100 produce very strong polarization differences in spin-correlated decays;
- those differences disappear when the decay is made isotropic;
- spin-correlated samples contain significant connected \(t\bar t\) correlations absent from isotropic controls;
- both decay channels and both initial states behave consistently;
- PYTHIA showering preserves the relevant spin structure;
- no statistically significant LHE-to-HepMC coefficient failure was observed;
- truth parsing was explicitly validated against status copies, secondary leptons, and photon conversions.

The strongest combined evidence is:

\[
\boxed{
\text{LR/RL separation in SC}
+
\text{null result in ISO}
+
\text{SC/ISO separation in }D_{ij}
+
\text{LHE/HepMC preservation}
}
\]

This combination demonstrates both correctly implemented beam polarization and correctly retained top-antitop spin correlation.

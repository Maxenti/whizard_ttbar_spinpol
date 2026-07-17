# `ttbar` HepMC → Delphes → wire-variant analysis workflow

## Purpose

This document records the physics and software logic of the `ttbar` fast-simulation workflow used to compare IDEA drift-chamber wire and coating variants.

It is intended for long-term validity, review, and reproduction. It explains how the analysis proceeds from a generated event sample to HepMC3, Delphes/EDM4hep ROOT output, chunked extraction, truth–reconstruction matching, response measurements, spin-sensitive observables, top/W record audits, response maps, and final deliverables.

This README deliberately avoids quoting final numerical results. Numerical values belong in generated CSV tables, JSON markers, plots, and internal-note material. The purpose here is to define how those results were obtained, what each observable means, and which validation gates must pass before a detector conclusion is considered reliable.

---

# 1. Provenance boundary

There are two related but not automatically identical workflows.

## 1.1 WHIZARD spin/polarization production

Canonical repository:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

This project is intended to generate controlled Monte Carlo samples for processes such as:

```text
e+ e-  -> t tbar
mu+ mu- -> t tbar
```

with explicit control over:

- center-of-mass energy;
- incoming beam species;
- longitudinal beam polarization;
- initial-state radiation;
- spin-correlated top and W decays;
- showering and hadronization;
- random seeds;
- HepMC3 output;
- generator-level polarization and spin-correlation validation.

## 1.2 Delphes wire-variant campaign

Campaign root:

```text
/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026
```

Analysis package:

```text
/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026/ttbar_initial_diagnostics
```

This campaign applies several IDEA DCH fast-simulation configurations to a common generated `ttbar` event sample and compares the resulting detector response.

## 1.3 Provenance must be explicit

A Delphes output may only be claimed to originate from a specific WHIZARD production when a manifest records:

- generator repository commit;
- generator steering/configuration;
- beam species and energy;
- center-of-mass energy;
- beam polarization convention and numerical values;
- ISR and beam-spectrum settings;
- decay configuration;
- Pythia/shower settings;
- random seeds;
- input LHE path and checksum, when applicable;
- output HepMC path and checksum;
- Delphes input HepMC path;
- Delphes card path and checksum;
- Key4hep/Delphes environment;
- output ROOT path and checksum.

Directory names alone are not sufficient provenance.

---

# 2. Storage model

## 2.1 AFS

AFS should hold compact, maintainable, versionable material:

- source code;
- steering files;
- scripts;
- HTCondor wrappers and submit files;
- configuration files;
- documentation;
- manifests;
- small summary tables;
- internal-note source.

Recommended documentation root:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/Documentation/Projects/ttbar_wire_variant_pipeline
```

## 2.2 EOS

EOS should hold large production products:

- LHE files;
- HepMC files;
- Delphes/EDM4hep ROOT files;
- chunk outputs;
- merged tables;
- plots;
- logs;
- bootstrap replicas;
- response maps;
- deliverable archives.

Canonical campaign root:

```text
/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026
```

The path `/eos/home-c/cglenn/...` may appear after path resolution. On lxplus it aliases the same user space, but manifests and commands should prefer the canonical `/eos/user/c/cglenn/...` spelling.

---

# 3. End-to-end data flow

```text
physics question
    |
    v
beam and hard-process definition
    |
    v
WHIZARD matrix-element generation
    |
    v
spin-correlated top/W decay
    |
    v
LHE event record
    |
    v
LHE canonicalization for Pythia
    |
    v
Pythia showering + hadronization
    |
    v
HepMC3 event record
    |
    +--------------------------------------+
    | identical HepMC events per variant  |
    +--------------------------------------+
       |              |              |
       v              v              v
   W/Au card       CF/Au card     CF/Au card ...
       |              |              |
       v              v              v
   Delphes          Delphes        Delphes
       |              |              |
       v              v              v
   EDM4hep ROOT    EDM4hep ROOT   EDM4hep ROOT
       |              |              |
       +------- exact truth/event identity ------+
                              |
                              v
                   chunk-level extraction
                              |
                              v
                   per-variant merge
                              |
                              v
            truth semantics + reco matching
                              |
                              v
           residuals, widths, ratios, maps
                              |
                              v
        bootstrap, spin proxies, mass audits
                              |
                              v
             validation + final package
```

---

# 4. Physics comparison design

The detector question is:

> When the generated physics events are held fixed, how does changing the configured IDEA DCH wire/coating material proxy alter reconstructed charged-particle and event observables?

The comparison is between specific fast-simulation detector variants, not an abstract statement about bulk materials.

Current variant labels include:

```text
W20_Au0p3_defaultlike
CF25_Au0p3
CF25_Au1p0
CF25_Au2p227matched
```

The short names are descriptive only. The actual Delphes card contents and checksums are authoritative.

## 4.1 Fair-comparison requirements

A valid comparison requires:

- the same generated events;
- the same event ordering;
- the same process and beam configuration;
- the same truth selections;
- the same reconstructed-object selections;
- the same acceptance;
- the same binning;
- the same estimators;
- the same plotting and masking rules;
- only intended detector-card differences.

If unrelated detector subsystems or physics settings differ, the result cannot be interpreted as an isolated DCH wire/material effect.

## 4.2 Why common generated events matter

Using identical HepMC events across all variants enables:

- exact event-key checks;
- exact selected-truth-object checks;
- event-paired CF-minus-W comparisons;
- paired bootstrap resampling;
- reduced generator-sample noise.

Common truth events do not prove that Delphes random smearing is identical across variants. Seeds and random-call ordering must be recorded independently.

---

# 5. WHIZARD hard-process generation

## 5.1 Process definition

The main production process is:

```text
e+ e- -> t tbar
```

with a parallel muon-collider form:

```text
mu+ mu- -> t tbar
```

The production configuration must record:

- incoming particle IDs;
- beam energies;
- center-of-mass energy;
- beam polarization;
- ISR;
- beam-spectrum treatment;
- electroweak input scheme;
- top mass and width;
- process definition;
- decay definition;
- event count;
- integration settings;
- random seed.

## 5.2 Spin-correlated decays

Top quarks decay before hadronization, so decay products preserve top-spin information. Charged leptons are especially powerful spin analyzers.

An analysis of spin-sensitive observables must therefore preserve production–decay correlations. Generating undecayed tops and imposing independent isotropic decays later would distort or erase the intended correlations.

The generator should maintain correlated production and decay whenever studying:

- top polarization;
- antitop polarization;
- spin correlation;
- beam polarization;
- dilepton angular distributions;
- threshold or toponium-like behavior.

## 5.3 Beam-polarization convention

Sample names such as `LR`, `RL`, `LR100`, or `RL100` are not sufficient documentation.

The manifest must state:

- which beam is listed first;
- whether positive polarization means right-handed or left-handed;
- the numerical polarization of each beam;
- whether the state is pure-helicity or partially polarized;
- whether weights already include polarization factors.

The configuration should be validated through physics distributions rather than inferred from filenames.

## 5.4 Initial-state radiation

ISR changes the effective collision energy and therefore affects:

- threshold behavior;
- top boosts;
- angular distributions;
- invariant-mass distributions;
- spin-sensitive shapes.

ISR must be handled consistently across compared samples and recorded explicitly.

## 5.5 LHE validation

Before showering, the LHE file should be checked for:

- valid `<event>` blocks;
- correct event counts;
- two incoming beam particles;
- valid mother indices;
- valid color-flow indices;
- finite four-vectors;
- event-by-event four-momentum closure;
- correct top/antitop content;
- expected decay products;
- no malformed metadata that breaks downstream readers.

---

# 6. LHE canonicalization for Pythia

The WHIZARD LHE record may contain bookkeeping structures that are acceptable to WHIZARD but not safely interpreted by the selected Pythia external-LHE interface.

Canonicalization is performed by a script such as:

```text
scripts/showering/canonicalize_whizard_lhe_for_pythia.py
```

The canonicalizer should:

- identify the true incoming beams;
- promote them to standard incoming LHE status;
- remove nonphysical bridge/bookkeeping entries where necessary;
- preserve all physical four-vectors;
- preserve event weights;
- update mother indices after record removal;
- remove incompatible custom tags only when required;
- verify four-momentum closure;
- write a machine-readable summary.

Canonicalization is an event-record compatibility operation. It must not change the physical process, beam polarization, decay assignment, event weight, or physical four-vectors.

For every canonicalized file, record:

- input path and checksum;
- output path and checksum;
- total events;
- modified events;
- promoted beam entries;
- removed bookkeeping entries;
- maximum absolute and relative closure residual;
- script version or repository commit.

---

# 7. Pythia showering and HepMC3 production

Pythia is used for:

- QCD and QED showering according to the configured settings;
- hadronization;
- unstable-hadron decays;
- conversion of the hard event into a realistic final-state event record.

The persistent generator output is HepMC3.

The production manifest must record:

- Pythia version;
- environment;
- external-LHE mode;
- ISR and FSR settings;
- multiparton interactions;
- hadronization;
- QED showering;
- top/W/tau decay handling;
- photon conversion handling;
- random seed;
- HepMC format.

Showering must not silently replace the already spin-correlated top/W decay with an unrelated decay model.

Before Delphes, validate the HepMC file:

- all events parse;
- event numbers are unique;
- particle four-vectors are finite;
- ancestry is recoverable;
- top and W decay chains are present;
- expected stable-particle content exists;
- event weights are finite;
- energy-momentum closure is understood;
- beam and polarization-sensitive distributions are plausible.

A nonempty file is not automatically a validated sample.

---

# 8. Generator-level spin validation

## 8.1 Lab-frame spin-sensitive observables

Robust lab-frame diagnostics include:

- \(|\Delta\phi_{\ell\ell}|\);
- \(\Delta R_{\ell\ell}\);
- the three-dimensional opening-angle cosine;
- the opening angle \(\omega_{\ell\ell}\);
- \(m_{\ell\ell}\);
- \(p_{T,\ell\ell}\);
- lepton \(p_T\) asymmetry.

These are spin-sensitive physics observables, but they are not a complete spin-density-matrix measurement.

## 8.2 Top-frame basis

A full spin analysis can use the `ttbar` zero-momentum frame and an orthonormal basis:

- `k`: helicity axis along the top direction;
- `n`: normal to the production plane;
- `r`: in the production plane and perpendicular to `k`.

One convention is:

\[
\hat n =
\frac{\hat p \times \hat k}
     {|\hat p \times \hat k|},
\qquad
\hat r = \hat n \times \hat k,
\]

where \(\hat p\) is the incoming negatively charged beam direction and \(\hat k\) is the top direction.

The sign convention must be frozen in code and documentation because mixed and normal coefficients can change sign under alternative valid conventions.

## 8.3 Fifteen spin observables

Single-spin quantities:

```text
B1k B1r B1n
B2k B2r B2n
```

Correlation quantities:

```text
Ckk Crr Cnn
Ckr Crk
Ckn Cnk
Crn Cnr
```

A commonly used angular form is:

\[
\frac{1}{\sigma}
\frac{d^2\sigma}
     {d\cos\theta^+_i\,d\cos\theta^-_j}
=
\frac14
\left[
1+B_{1i}\cos\theta^+_i
+B_{2j}\cos\theta^-_j
-C_{ij}\cos\theta^+_i\cos\theta^-_j
\right].
\]

Under this sign convention:

\[
B_{1i}=3\langle\cos\theta^+_i\rangle,
\qquad
B_{2j}=3\langle\cos\theta^-_j\rangle,
\qquad
C_{ij}=-9\langle\cos\theta^+_i\cos\theta^-_j\rangle.
\]

The implemented sign convention must be written into metadata.

## 8.4 Top-frame readiness gate

Top-rest-frame observables must not be published until the selected top and antitop four-vectors pass closure checks.

Compare:

\[
p^\mu_{t,\mathrm{stored}}
\quad\text{with}\quad
p^\mu_W+p^\mu_q.
\]

An unusual selected top mass or status can represent an off-shell object, a shower copy, or a bookkeeping record. Such a record should not be used automatically for rest-frame boosts.

Lab-frame observables can remain valid while top-frame observables are blocked.

---

# 9. Delphes fast simulation

## 9.1 Purpose

Delphes converts stable-particle HepMC events into a parameterized approximation of detector response.

In this project, Delphes is used as a controlled proxy for how IDEA DCH material and tracking-response assumptions affect reconstructed observables. It does not replace full Geant4 transport, Garfield response simulation, realistic digitization, or pattern recognition.

## 9.2 Common-input rule

Every detector variant must read the same HepMC events.

Conceptually:

```text
one HepMC chunk
    -> W/Au Delphes card
    -> CF/Au thin-coating card
    -> CF/Au thicker-coating card
    -> CF/Au matched-conductivity card
```

This structure is repeated for every chunk.

## 9.3 Card-difference audit

Before production, create a structured diff of all cards and included fragments.

Classify every difference as:

- intended DCH material proxy;
- intended momentum-resolution or covariance change;
- intended electron material/bremsstrahlung change;
- fixed common detector setting;
- accidental unrelated difference;
- formatting-only difference.

The card audit should record:

- card path;
- card checksum;
- included files;
- changed parameter names;
- old and new values;
- physical interpretation;
- whether the change is intended.

A wire-variant conclusion is only defensible if unrelated subsystems are demonstrably fixed.

## 9.4 Track-covariance interpretation

Delphes track response may depend on:

- momentum;
- transverse momentum;
- polar angle;
- pseudorapidity;
- charge-over-momentum;
- impact parameters;
- multiple-scattering terms;
- material-sensitive covariance terms.

A card change can improve momentum response while leaving angular response nearly unchanged. That can be physically reasonable if the modified terms primarily affect curvature or multiple scattering rather than angular-coordinate resolution.

This interpretation must come from the actual card diff, not solely from output plots.

## 9.5 EDM4hep ROOT output

The Delphes campaign writes EDM4hep-compatible ROOT files.

Relevant collections may include:

- MC particles;
- reconstructed particles;
- tracks or EFlow tracks;
- jets;
- missing transverse momentum;
- truth-to-reconstructed associations;
- association weights;
- event headers.

The analysis should inventory actual branches and collections rather than assume a fixed schema.

---

# 10. Delphes production and chunking

Large samples are split into chunks to support:

- manageable memory use;
- HTCondor parallelism;
- localized retries;
- deterministic provenance;
- scalable extraction;
- partial reruns;
- failure diagnosis.

Each job should record:

- input HepMC path and checksum;
- input chunk or event range;
- detector variant;
- card path and checksum;
- software environment;
- random seed;
- output ROOT path;
- output event count;
- hostname;
- start and end time;
- exit code.

## 10.1 Stable event keys

A local event index alone is not a safe global identifier.

A stable key should include enough context to remain unique, for example:

```text
chunk_id:event_number
```

or:

```text
input_file_id:event_number
```

Object-level keys should additionally include a stable truth-particle or selected-object index.

## 10.2 Seeds and determinism

Record Delphes seeds for every job.

Using the same seed across variants may increase stochastic correlation, but identical random smearing is not guaranteed because different cards can change random-call ordering.

The robust comparison requirements are:

- common generated events;
- recorded seeds;
- exact event-key identity;
- paired analysis by event;
- no unsupported assumption of identical random-number histories.

---

# 11. Extract-once, analyze-many-times design

Current analysis package:

```text
/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026/ttbar_initial_diagnostics
```

Instead of reopening large ROOT files independently for every plot, each chunk is read once and converted into compact reusable products.

Typical chunk products include:

```text
chunk_summary.json
histograms.npz
histogram_metadata.json
event_keys.csv.gz
lepton_keys.csv.gz
link_outliers.csv.gz
branch_inventory.json
physics_object_selection.json
top_decay_audit.csv.gz
```

## 11.1 `chunk_summary.json`

Records:

- variant;
- chunk;
- event range;
- event counts;
- selected-object counts;
- paths;
- status;
- warnings.

## 11.2 `histograms.npz`

Stores numerical histogram arrays for later merging and plotting.

## 11.3 `histogram_metadata.json`

Stores:

- histogram names;
- bin edges;
- units;
- normalization semantics;
- underflow/overflow treatment;
- observable definitions.

## 11.4 `event_keys.csv.gz`

Stores stable event identifiers and event-level truth fingerprints.

## 11.5 `lepton_keys.csv.gz`

Stores one row per selected truth lepton, including:

- event key;
- truth-particle index;
- PDG ID;
- charge;
- truth kinematics;
- reconstructed match;
- ancestry;
- origin category;
- response residuals.

## 11.6 `link_outliers.csv.gz`

Stores invalid, unusual, or low-quality association cases for explicit inspection rather than silent removal.

## 11.7 `branch_inventory.json`

Records the collections and branch names actually found in the ROOT file.

## 11.8 `physics_object_selection.json`

Records the selection configuration for:

- stable truth particles;
- electrons and muons;
- reconstructed particles;
- tracks;
- jets;
- links and weights;
- kinematic acceptance.

## 11.9 `top_decay_audit.csv.gz`

Stores selected top, W, and direct-quark records and the reason each was accepted or flagged.

---

# 12. Merge and finalization

Chunk products are merged per detector variant.

The merge stage must verify:

- every expected chunk exists;
- no chunk is duplicated;
- no duplicate event keys exist;
- event ranges do not overlap unexpectedly;
- histogram binning is identical;
- table schemas are compatible;
- compressed CSV products are readable;
- required numerical values are finite.

The initial finalizer is conceptually:

```text
scripts/finalize_ttbar_initial_diagnostics.sh
```

It produces:

- merged per-variant tables;
- merged histograms;
- initial plots;
- validation tables;
- a human-readable report;
- a machine-readable status.

A warning requires interpretation. A failure indicates that a required contract was broken.

---

# 13. Cross-variant identity validation

Detector-response ratios are meaningful only after proving that all variants contain the same truth sample and the same selected truth objects.

## 13.1 Event identity

For every variant, require:

- identical unique event-key sets;
- no missing keys;
- no extra keys;
- no duplicate keys;
- matching truth fingerprints.

## 13.2 Selected-object identity

For each selection state, require:

- identical selected truth-lepton keys;
- identical matched truth-lepton keys;
- identical unmatched truth-lepton keys;
- no duplicate selected-object keys.

## 13.3 Truth-semantic identity

Require identical:

- selected top records;
- selected W records;
- selected direct quarks;
- W decay modes;
- lepton-origin categories;
- ancestry paths;
- prompt/tau/secondary membership.

A detector comparison should stop if these truth-level contracts fail.

---

# 14. Truth-particle kinematics

For momentum components \((p_x,p_y,p_z)\):

## 14.1 Transverse momentum

\[
p_T=\sqrt{p_x^2+p_y^2}.
\]

This is the primary charged-track scale because curvature in a solenoidal field is most directly related to transverse momentum.

## 14.2 Momentum magnitude

\[
p=\sqrt{p_x^2+p_y^2+p_z^2}.
\]

## 14.3 Azimuth

\[
\phi=\operatorname{atan2}(p_y,p_x).
\]

Azimuth is periodic. Differences must be wrapped.

## 14.4 Pseudorapidity

\[
\eta=
\frac12
\ln\left(
\frac{p+p_z}{p-p_z}
\right).
\]

Numerical handling is required near the beam direction.

Absolute pseudorapidity, \(|\eta|\), folds positive and negative detector hemispheres when a sign-symmetric comparison is intended.

## 14.5 Energy

Use the stored energy when it is authoritative. Otherwise:

\[
E=\sqrt{p^2+m^2}.
\]

## 14.6 Invariant mass

\[
m^2=E^2-p_x^2-p_y^2-p_z^2,
\qquad
m=\sqrt{\max(m^2,0)}.
\]

Small negative values may be clipped only when they are consistent with floating-point precision.

---

# 15. Selected top and W semantics

Generator records can contain multiple copies of a physical top or W because of:

- matrix-element bookkeeping;
- shower history;
- radiation;
- status transitions;
- same-PDG copy chains.

The analysis therefore uses ordered selection logic rather than selecting the first particle with PDG `±6` or `±24`.

## 15.1 Selected top

For each event:

1. identify top and antitop candidates;
2. inspect daughter relations;
3. prefer physically interpretable decay records;
4. require a W with the correct sign;
5. identify the accompanying direct quark;
6. record mass and generator status;
7. flag unusual daughter patterns or masses;
8. preserve the selected index for later audits.

The dominant decay is `t -> W b`, but physical `W s` and `W d` decays must not automatically be labeled invalid.

## 15.2 Direct W

The direct W is attached directly to the selected top.

Expected signs:

```text
t    -> W+ + q
tbar -> W- + qbar
```

## 15.3 Terminal W

Starting from the direct W, traverse same-PDG W daughters until reaching the W copy whose daughters define the decay mode.

The direct and terminal W may be the same record.

## 15.4 W decay classification

The terminal W is classified as:

- direct electron;
- direct muon;
- tau-mediated;
- hadronic;
- other or ambiguous.

Tau-mediated means the final stable electron or muon descends through an intermediate tau.

---

# 16. Stable electron/muon origin categories

## 16.1 `prompt_top_w`

Stable electron or muon descending from the selected top-decay W with no intervening tau.

This is the primary clean top-lepton tracking-response category.

## 16.2 `prompt_top_w_e`

Electron subset of `prompt_top_w`.

It is especially sensitive to material-dependent bremsstrahlung and electron-specific response terms.

## 16.3 `prompt_top_w_mu`

Muon subset of `prompt_top_w`.

It provides a cleaner curvature and multiple-scattering control because muon bremsstrahlung is much smaller.

## 16.4 `top_w_tau`

Stable electron or muon descending through:

```text
top -> W -> tau -> electron/muon
```

This category has softer kinematics and additional neutrinos.

## 16.5 `all_top_chain`

Union of:

```text
prompt_top_w
top_w_tau
```

## 16.6 `heavy_flavour_secondary`

Stable electron or muon with bottom- or charm-flavoured ancestry.

## 16.7 `w_hadronic_secondary`

Stable electron or muon downstream of hadronic selected-W daughters.

## 16.8 `photon_conversion`

Electron or positron with photon ancestry consistent with conversion-like production.

## 16.9 `secondary_multitag_or_other`

Used when several secondary-origin tags apply or no unique classification is justified.

This preserves ambiguity instead of forcing a false unique origin.

---

# 17. Truth-to-reconstructed association

The analysis uses EDM4hep truth–reconstructed association records, commonly referred to as RecoMC links.

For each selected truth lepton:

1. find all association records connected to it;
2. identify associated reconstructed particles;
3. read the association weight;
4. apply validity and optional weight requirements;
5. reject invalid indices or nonfinite kinematics;
6. choose the authoritative match according to the configured rule;
7. record matched or unmatched status.

A matched fraction derived from prelinked Delphes objects is a matching diagnostic within this fast-simulation model. It is not automatically a complete real-detector tracking efficiency.

A stable selected-object key should include:

- event key;
- truth-particle index;
- optional category or selection state.

---

# 18. Single-particle response observables

For an exactly associated truth and reconstructed lepton:

## 18.1 Relative transverse-momentum residual

\[
\delta_{p_T}^{\mathrm{rel}}
=
\frac{
p_{T,\mathrm{reco}}
-
p_{T,\mathrm{truth}}
}{
p_{T,\mathrm{truth}}
}.
\]

Interpretation:

- zero: unbiased;
- positive: reconstructed `pT` too high;
- negative: reconstructed `pT` too low;
- narrower: better fractional `pT` resolution.

Use truth `pT` for binning. Reconstructed-value binning can bias the measured response through migration.

## 18.2 Pseudorapidity residual

\[
\Delta\eta
=
\eta_{\mathrm{reco}}
-
\eta_{\mathrm{truth}}.
\]

## 18.3 Wrapped azimuthal residual

\[
\Delta\phi_{\mathrm{raw}}
=
\phi_{\mathrm{reco}}
-
\phi_{\mathrm{truth}},
\]

then:

\[
\Delta\phi
=
\operatorname{atan2}
\left(
\sin\Delta\phi_{\mathrm{raw}},
\cos\Delta\phi_{\mathrm{raw}}
\right).
\]

This correctly handles the \(-\pi/+ \pi\) boundary.

## 18.4 Angular displacement

\[
\Delta R
=
\sqrt{
(\Delta\eta)^2
+
(\Delta\phi)^2
}.
\]

Because \(\Delta R\ge 0\), its median is a positive scale rather than a signed bias.

## 18.5 Link weight

The association weight is retained as a matching-quality diagnostic. It should not be interpreted as a universal probability without confirming producer semantics.

---

# 19. One-dimensional plots

For each category and variant, produce truth and reconstructed distributions for quantities such as:

- `pT`;
- `eta`;
- `phi`;
- energy;
- response residuals;
- multiplicities.

## 19.1 Absolute-count overlays

These preserve:

- selected yield;
- acceptance;
- matching loss;
- category population.

## 19.2 Unit-area overlays

These normalize each distribution to one and compare shape only.

A unit-area plot cannot establish equal efficiency or equal yield.

## 19.3 Ratio-to-W panels

For histogram bin \(b\):

\[
R_{\mathrm{variant}/W}(b)
=
\frac{
H_{\mathrm{variant}}(b)
}{
H_W(b)
}.
\]

Bins with zero or invalid W denominator must be masked rather than set to zero or one.

---

# 20. Event-level reconstructed observables

## 20.1 Visible energy

\[
E_{\mathrm{visible}}
=
\sum_i E_i
\]

over the selected reconstructed-particle collection.

## 20.2 Charged visible energy

\[
E_{\mathrm{charged}}
=
\sum_{i\in\mathrm{charged}}E_i.
\]

## 20.3 Neutral visible energy

\[
E_{\mathrm{neutral}}
=
\sum_{i\in\mathrm{neutral}}E_i.
\]

## 20.4 Charged-energy fraction

\[
f_{\mathrm{charged}}
=
\frac{
E_{\mathrm{charged}}
}{
E_{\mathrm{visible}}
},
\]

for nonzero visible energy.

## 20.5 Scalar transverse-momentum sum

\[
\sum p_T
=
\sum_i p_{T,i}.
\]

This is a scalar sum and does not include vector cancellation.

## 20.6 Visible-recoil missing transverse momentum

\[
\vec p_T^{\,\mathrm{miss}}
=
-\sum_i\vec p_{T,i},
\qquad
p_T^{\mathrm{miss,visible}}
=
\left|
\vec p_T^{\,\mathrm{miss}}
\right|.
\]

This is an independent visible-object missing-momentum proxy.

## 20.7 Native missing transverse momentum

This is read from the stored Delphes/EDM4hep missing-energy collection.

The native and visible-recoil definitions are not guaranteed to be identical.

## 20.8 Missing azimuth

\[
\phi_{\mathrm{miss}}
=
\operatorname{atan2}
(p_y^{\mathrm{miss}},p_x^{\mathrm{miss}}).
\]

It becomes unstable when the missing-momentum magnitude is very small.

## 20.9 Multiplicity diagnostics

Potential counts include:

- reconstructed particles;
- charged reconstructed particles;
- neutral reconstructed particles;
- tracks;
- EFlow tracks;
- jets;
- selected truth leptons;
- matched truth leptons.

A multiplicity is not an efficiency unless a denominator and object definition are explicit.

---

# 21. Jet observables

Jets are normally sorted by descending transverse momentum.

Useful quantities include:

- jet multiplicity;
- leading-jet `pT`;
- subleading-jet `pT`;
- leading-jet energy;
- subleading-jet energy;
- jet `eta`;
- jet `phi`;
- scalar jet `HT`.

For two selected jets:

\[
p^\mu_{\mathrm{dijet}}
=
p^\mu_{\mathrm{jet1}}
+
p^\mu_{\mathrm{jet2}},
\qquad
m_{\mathrm{dijet}}
=
\sqrt{p_{\mathrm{dijet}}^2}.
\]

This is a general hadronic observable. It is not a reconstructed W mass unless jets are explicitly assigned to a W candidate using a documented reconstruction algorithm.

---

# 22. Prompt dilepton construction

A prompt dilepton event requires one selected positively charged and one selected negatively charged prompt top-W lepton.

The selected pair should record:

- event key;
- positive-lepton key;
- negative-lepton key;
- truth four-vectors;
- reconstructed four-vectors;
- charges;
- flavours;
- ambiguity or multiple-candidate flags.

Charge ordering fixes the sign convention for signed observables.

---

# 23. Dilepton observables

Let the selected leptons be \(\ell^+\) and \(\ell^-\).

## 23.1 Absolute azimuthal separation

\[
|\Delta\phi_{\ell\ell}|
=
\left|
\operatorname{wrap}
(\phi_+-\phi_-)
\right|.
\]

## 23.2 Dilepton angular distance

\[
\Delta R_{\ell\ell}
=
\sqrt{
(\eta_+-\eta_-)^2
+
\operatorname{wrap}(\phi_+-\phi_-)^2
}.
\]

## 23.3 Three-dimensional opening-angle cosine

\[
\cos\omega_{\ell\ell}
=
\frac{
\vec p_+\cdot\vec p_-
}{
|\vec p_+||\vec p_-|
}.
\]

Clip numerically to `[-1,1]`.

## 23.4 Opening angle

\[
\omega_{\ell\ell}
=
\arccos(\cos\omega_{\ell\ell}).
\]

## 23.5 Transverse-momentum asymmetry

\[
A_{p_T}
=
\frac{
p_{T,+}-p_{T,-}
}{
p_{T,+}+p_{T,-}
}.
\]

## 23.6 Dilepton transverse momentum

\[
p_{T,\ell\ell}
=
\left|
\vec p_{T,+}
+
\vec p_{T,-}
\right|.
\]

This is a vector sum, not a scalar sum.

## 23.7 Dilepton invariant mass

\[
m_{\ell\ell}
=
\sqrt{
(p^\mu_+ + p^\mu_-)^2
}.
\]

## 23.8 Detector residuals

For a dilepton observable \(x\):

\[
\Delta x
=
x_{\mathrm{reco}}
-
x_{\mathrm{truth}}.
\]

Angular quantities require wrapping or bounded-domain handling.

The detector question is whether reconstruction preserves the truth distribution. A larger or smaller physics value is not intrinsically “better.”

---

# 24. Resolution and tail estimators

## 24.1 Number of finite entries

\[
n
=
\text{number of finite selected values}.
\]

## 24.2 Mean

\[
\bar x
=
\frac{1}{n}
\sum_i x_i.
\]

Sensitive to tails.

## 24.3 Median

\[
\mathrm{median}
=
q_{50}.
\]

Robust to tails.

## 24.4 Standard deviation

\[
\sigma
=
\sqrt{
\frac{1}{n}
\sum_i
(x_i-\bar x)^2
}.
\]

Sensitive to non-Gaussian tails.

## 24.5 Central-68 half-width

\[
w_{68}
=
\frac{
q_{84}-q_{16}
}{2}.
\]

This is the primary robust core-width estimator. It equals a Gaussian standard deviation only for an ideal Gaussian distribution.

## 24.6 Central-90 half-width

\[
w_{90}
=
\frac{
q_{95}-q_{05}
}{2}.
\]

This probes a wider response region.

## 24.7 Absolute 95th percentile

\[
q_{95}^{|\cdot|}
=
q_{95}(|x|).
\]

This summarizes the scale containing most absolute deviations. For a biased distribution it combines bias and spread.

## 24.8 Outer quantiles

The first and ninety-ninth percentiles characterize broad tails but do not describe rarer events beyond those quantiles.

---

# 25. Variant-to-W comparison metrics

For a positive width or tail metric \(s\):

\[
R_{\mathrm{CF}/W}
=
\frac{
s_{\mathrm{CF}}
}{
s_W
}.
\]

Interpretation:

- \(R<1\): narrower CF response;
- \(R=1\): equal width;
- \(R>1\): broader CF response.

Percentage improvement is defined as:

\[
I_{\mathrm{CF}/W}
=
100
\left(
1-
\frac{
s_{\mathrm{CF}}
}{
s_W
}
\right).
\]

Thus:

- positive means improvement;
- zero means no change;
- negative means degradation.

## 25.1 Signed quantities near zero

Do not ratio signed means or medians to a near-zero baseline.

Use a difference:

\[
\Delta\mathrm{median}
=
\mathrm{median}_{\mathrm{CF}}
-
\mathrm{median}_W.
\]

## 25.2 Conditions for a valid ratio

Only calculate a ratio when:

- numerator is finite;
- denominator is finite;
- denominator is nonzero;
- selection is identical;
- binning is identical;
- estimator is identical;
- minimum-statistics requirement is satisfied.

---

# 26. One-axis response curves

Resolution is studied versus:

- truth `pT`;
- truth `|eta|`.

## 26.1 Width versus truth `pT`

For each truth-`pT` bin:

1. select matched objects using truth `pT`;
2. collect the residual;
3. require the minimum number of finite entries;
4. calculate the configured estimator;
5. repeat for all variants;
6. form CF/W ratios where valid.

This integrates over the accepted `|eta|` distribution in each `pT` bin.

## 26.2 Width versus truth `|eta|`

The same procedure is repeated in truth-`|eta|` bins.

This integrates over the truth-`pT` distribution in each `|eta|` bin.

One-axis curves therefore remain spectrum weighted in the unplotted variable.

---

# 27. Two-dimensional response maps

The response-map stage evaluates metrics in:

```text
truth pT × truth |eta|
```

For each category, metric, estimator, and variant:

1. select matched objects;
2. assign each object to a truth-`pT` bin;
3. assign each object to a truth-`|eta|` bin;
4. collect finite residual values;
5. require the configured minimum population;
6. calculate the estimator;
7. mask insufficient cells;
8. calculate CF/W ratios only for finite nonzero W values;
9. calculate percentage improvement for positive width-like estimators.

A masked cell means insufficient information, not zero response.

## 27.1 Absolute maps

Show the estimator itself for each detector variant.

## 27.2 All-variant absolute panels

Place W and all CF variants together for direct comparison.

## 27.3 CF/W ratio maps

\[
R_{\mathrm{CF}/W}
=
\frac{
\mathrm{metric}_{\mathrm{CF}}
}{
\mathrm{metric}_W
}.
\]

## 27.4 Improvement maps

\[
I_{\mathrm{CF}/W}
=
100
\left(
1-
\frac{
\mathrm{metric}_{\mathrm{CF}}
}{
\mathrm{metric}_W
}
\right).
\]

## 27.5 Median-difference maps

For signed medians near zero:

\[
\mathrm{median}_{\mathrm{CF}}
-
\mathrm{median}_W.
\]

## 27.6 Coverage records

Every response-map product should be accompanied by:

- cell population;
- finite-entry population;
- masked-cell flag;
- finite-ratio flag;
- bin edges;
- minimum-entry threshold.

---

# 28. Paired bootstrap uncertainty

Because all variants use common generated events, uncertainty estimation should preserve event pairing.

## 28.1 Resampling unit

Resample parent events, not individual leptons.

This preserves:

- cross-variant event covariance;
- correlations between both leptons in one event;
- within-event object correlations;
- exact common-event structure.

## 28.2 Procedure

For each bootstrap replica:

1. draw event keys with replacement;
2. apply identical event multiplicities to W and every CF variant;
3. calculate the W estimator;
4. calculate each CF estimator;
5. calculate the paired ratio or difference;
6. store the replica.

## 28.3 Percentile intervals

Typical intervals:

```text
68%: q16 to q84
95%: q2.5 to q97.5
```

These quantify finite-sample statistical resampling uncertainty.

They do not include:

- detector-model systematics;
- material-model systematics;
- generator uncertainty;
- card-parameter uncertainty;
- calibration uncertainty;
- beam uncertainty;
- theory uncertainty.

---

# 29. Migration matrices

For a binned observable:

- rows are truth bins;
- columns are reconstructed bins.

## 29.1 Diagonal fraction

\[
f_{\mathrm{diag}}
=
\frac{
N(b_{\mathrm{reco}}=b_{\mathrm{truth}})
}{
N_{\mathrm{total}}
}.
\]

## 29.2 Off-diagonal fraction

\[
f_{\mathrm{offdiag}}
=
1-f_{\mathrm{diag}}.
\]

## 29.3 Mean absolute migration

\[
\left\langle
|b_{\mathrm{reco}}-b_{\mathrm{truth}}|
\right\rangle.
\]

These metrics depend strongly on binning. Coarse bins can hide small detector changes.

---

# 30. Selected-top mass audit

The selected-top mass is a generator-record diagnostic used to validate:

- top-copy selection;
- generator status semantics;
- daughter pattern;
- top-rest-frame suitability.

An out-of-window top mass is not automatically invalid. It can indicate:

- off-shell production;
- radiation;
- a shower copy;
- generator bookkeeping;
- a valid non-b decay;
- an incorrectly selected record.

The stored top four-vector should be compared with the summed W+quark daughter four-vector before deciding.

---

# 31. Selected-W mass and daughter closure

This is a generator-truth audit, not a detector-level W reconstruction.

For each frozen selected top/W target:

## 31.1 Direct-W mass

Mass stored on the direct W attached to the selected top.

## 31.2 Terminal-W mass

Mass stored on the terminal same-PDG W copy whose daughters define the decay mode.

## 31.3 Daughter-system mass

\[
p^\mu_{\mathrm{daughters}}
=
\sum_i p_i^\mu,
\qquad
m_{\mathrm{daughters}}
=
\sqrt{
p_{\mathrm{daughters}}^2
}.
\]

## 31.4 Direct-to-terminal consistency

\[
\Delta m_{\mathrm{direct-terminal}}
=
m_{W,\mathrm{direct}}
-
m_{W,\mathrm{terminal}}.
\]

## 31.5 Terminal-to-daughter closure

\[
\Delta m_{\mathrm{terminal-daughters}}
=
m_{W,\mathrm{terminal}}
-
m_{\mathrm{daughters}}.
\]

Near-zero closure confirms that the selected daughters reproduce the stored W record to numerical precision.

A broad W-mass-window warning is distinct from:

- missing targets;
- invalid indices;
- wrong W sign;
- nonfinite mass;
- failed daughter closure.

---

# 32. Plot and metric explanation records

The analysis creates:

```text
docs/PLOT_AND_METRIC_EXPLANATION.md
docs/PLOT_AND_METRIC_DICTIONARY.csv
docs/PLOT_FILE_EXPLANATION_INDEX.csv
```

The dictionary should define:

- observable;
- formula;
- units;
- physical meaning;
- preferred detector-response direction;
- ratio rule;
- caveat.

The file index maps each actual plot to inferred:

- plot family;
- category;
- observable;
- estimator;
- comparison mode.

The dictionary and generating script are authoritative. Filename inference is only a navigation aid.

---

# 33. Validation status model

Every stage should report:

```text
PASS
WARNING
FAIL
```

## PASS

All required contracts were satisfied.

## WARNING

Required outputs exist and structural contracts pass, but interpretation is needed.

Examples:

- broad physical tails;
- range loss;
- low-statistics bins;
- blocked top-frame readiness;
- masked response-map cells.

## FAIL

A required contract is broken.

Examples:

- missing input;
- missing chunk;
- duplicate keys;
- truth mismatch;
- invalid index;
- nonfinite required value;
- inconsistent binning;
- missing plot;
- zero-byte output;
- failed closure.

Do not downgrade a failure to a warning merely to complete the campaign.

---

# 34. Histogram range validation

Every histogram should track:

- finite entries;
- underflow;
- overflow;
- observed minimum;
- observed maximum;
- plotted range;
- fraction outside the plotted range.

A narrow core plot may intentionally omit tails, but a wide diagnostic plot or range-loss record should exist.

Plot range is a presentation choice and must not silently redefine the selected sample.

---

# 35. Typical output tree

```text
RUN_DIR/
  chunk_products/
  merged/
  plots/
  tables/
  validation/
  logs/
  metadata/
  derived/
  deliverables/
```

- `chunk_products/`: independent extraction results;
- `merged/`: per-variant merged compact records;
- `plots/`: initial diagnostic figures;
- `tables/`: merged summaries;
- `validation/`: machine- and human-readable checks;
- `logs/`: runtime and batch logs;
- `metadata/`: pointers, environment, success markers;
- `derived/`: higher-level analyses;
- `deliverables/`: curated closeout packages.

---

# 36. Reconstructing current paths

```bash
CAMPAIGN=/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026
PACKAGE_DIR="$CAMPAIGN/ttbar_initial_diagnostics"

RUN_DIR="$CAMPAIGN/plots/ttbar_initial_diagnostics_v1p2p1_split2000_20260715_034945"

ANALYSIS_DIR=$(
  cat "$RUN_DIR/derived/LATEST_TTBAR_DECAY_ANALYSIS_V1P3_RUN.txt"
)

echo "CAMPAIGN=$CAMPAIGN"
echo "PACKAGE_DIR=$PACKAGE_DIR"
echo "RUN_DIR=$RUN_DIR"
echo "ANALYSIS_DIR=$ANALYSIS_DIR"
```

A future campaign should create a new timestamped run rather than overwrite the current authoritative instance.

---

# 37. Environment setup

Use the Key4hep release recorded by the campaign metadata.

Example:

```bash
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-07-10
```

Verify dependencies:

```bash
python3 - <<'PY'
import sys
import numpy
import matplotlib
import uproot

print("python:", sys.executable)
print("numpy:", numpy.__version__)
print("matplotlib:", matplotlib.__version__)
print("uproot:", uproot.__version__)
PY
```

## 37.1 Bash strict-mode caveat

The Key4hep setup script may inspect optional positional parameters. Do not source it under active `set -u` without protection.

Safe pattern:

```bash
set +e
set +u
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-07-10
SETUP_RC=$?
set -euo pipefail

if [[ "$SETUP_RC" -ne 0 ]]; then
  echo "Key4hep setup failed: rc=$SETUP_RC" >&2
  exit "$SETUP_RC"
fi
```

---

# 38. Reproducing from an existing Delphes ROOT campaign

## 38.1 Inventory the package

```bash
find "$PACKAGE_DIR" \
  -maxdepth 3 \
  -type f \
  -printf '%P\n' \
  | sort
```

## 38.2 Discover current entry points

Script names can evolve. Inspect rather than guess:

```bash
find "$PACKAGE_DIR/scripts" \
  -maxdepth 1 \
  -type f \
  \( \
    -name 'submit*.sh' \
    -o -name 'run*.sh' \
    -o -name 'finalize*.sh' \
    -o -name 'check*.sh' \
  \) \
  -printf '%f\n' \
  | sort
```

Read each script’s `--help` output and embedded documentation before rerunning.

## 38.3 Validate chunk completion

Verify every expected chunk and event range. Do not infer completeness from ROOT-file count alone.

## 38.4 Finalize initial diagnostics

Conceptually:

```bash
"$PACKAGE_DIR/scripts/finalize_ttbar_initial_diagnostics.sh" \
  "$RUN_DIR"
```

Only rerun if the operation is documented as safe or an explicit overwrite mode is used.

## 38.5 Recover derived analysis

```bash
ANALYSIS_DIR=$(
  cat "$RUN_DIR/derived/LATEST_TTBAR_DECAY_ANALYSIS_V1P3_RUN.txt"
)
```

## 38.6 Validate response maps

```bash
"$PACKAGE_DIR/scripts/check_ttbar_topmode_response_2d.sh" \
  --analysis-dir "$ANALYSIS_DIR"
```

## 38.7 Validate W-mass and plot documentation

```bash
"$PACKAGE_DIR/scripts/check_ttbar_w_mass_audit.sh" \
  --analysis-dir "$ANALYSIS_DIR"
```

## 38.8 Finalize the explanation record

```bash
"$PACKAGE_DIR/scripts/finalize_ttbar_plot_explanation_record.py" \
  --analysis-dir "$ANALYSIS_DIR"
```

## 38.9 Build the final deliverable

```bash
"$PACKAGE_DIR/scripts/build_step2_topmode_deliverable.sh" \
  --analysis-dir "$ANALYSIS_DIR"
```

Recover it through the stable pointer:

```bash
DELIV_DIR=$(
  cat "$ANALYSIS_DIR/deliverables/LATEST_STEP2_TOPMODE_PACKAGE.txt"
)

echo "DELIV_DIR=$DELIV_DIR"
cat "$DELIV_DIR/STATUS.txt"
```

---

# 39. Reproducing from HepMC

To reproduce Delphes output from a validated HepMC sample:

1. freeze the HepMC path and checksum;
2. freeze all Delphes cards and checksums;
3. freeze the software environment;
4. create an input-chunk manifest;
5. assign deterministic Delphes seeds;
6. run every HepMC chunk through every detector variant;
7. validate each ROOT file;
8. prove event-key and truth-fingerprint identity;
9. run the analysis package.

A minimal manifest structure is:

```yaml
schema_version: 1

sample:
  process: "e+ e- -> t tbar"
  generator: "WHIZARD"
  generator_commit: "<commit>"
  center_of_mass_energy_gev: "<value>"
  beam_1_pdg: 11
  beam_2_pdg: -11
  beam_1_polarization: "<value>"
  beam_2_polarization: "<value>"
  isr_enabled: true
  spin_correlated_decays: true
  shower: "Pythia8"
  hepmc_format: "HepMC3"
  hepmc_path: "<path>"
  hepmc_sha256: "<sha256>"

environment:
  key4hep_release: "<release>"
  host_os: "<os>"
  delphes_version: "<version>"
  edm4hep_version: "<version>"

variants:
  - name: "W20_Au0p3_defaultlike"
    card: "<path>"
    card_sha256: "<sha256>"
  - name: "CF25_Au0p3"
    card: "<path>"
    card_sha256: "<sha256>"
  - name: "CF25_Au1p0"
    card: "<path>"
    card_sha256: "<sha256>"
  - name: "CF25_Au2p227matched"
    card: "<path>"
    card_sha256: "<sha256>"

chunking:
  input_manifest: "<path>"
  events_per_job: "<value>"
  seed_rule: "<description>"

outputs:
  root_base: "<path>"
  analysis_base: "<path>"
```

Replace every placeholder before archiving.

---

# 40. Reproducing from WHIZARD

Canonical generator repository:

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

The conceptual sequence is:

1. source the recorded environment;
2. validate steering files;
3. integrate the WHIZARD process;
4. generate requested helicity/polarization samples;
5. write LHE;
6. canonicalize LHE;
7. validate closure;
8. shower with Pythia;
9. write HepMC3;
10. validate event content;
11. write checksums and metadata;
12. pass only validated HepMC to Delphes.

Canonicalization command structure:

```bash
python3 scripts/showering/canonicalize_whizard_lhe_for_pythia.py \
  --input INPUT.lhe \
  --output OUTPUT.canonical.lhe \
  --summary canonicalization_summary.json
```

Use the exact production and shower commands from the current generator repository because they encode the tested settings and metadata conventions.

---

# 41. Generator-production gates

A sample is ready for Delphes only when all applicable gates pass.

## Gate A: steering and integration

- steering parses;
- integration completes;
- cross section is finite;
- integration uncertainty is recorded.

## Gate B: event generation

- requested event count is produced;
- event numbers are unique;
- weights are finite;
- seed is recorded.

## Gate C: LHE structure

- event blocks parse;
- incoming particles are valid;
- mother indices are valid;
- four-momentum closure passes;
- canonicalization summary passes.

## Gate D: showering

- events are accepted or rejection fraction is documented;
- no fatal Pythia errors occur;
- settings are recorded;
- HepMC output is nonempty.

## Gate E: physics content

- top and antitop are present;
- decay modes are valid;
- ancestry is recoverable;
- polarization-sensitive distributions are plausible;
- spin-sensitive observables are consistent with the configured sample.

## Gate F: provenance

- checksums;
- commits;
- environment;
- commands;
- logs;
- output manifest.

---

# 42. Delphes-production gates

A detector variant is ready for analysis only when:

- every expected input chunk was processed;
- output ROOT files are readable;
- event counts are consistent;
- event headers exist;
- MC particles exist;
- reconstructed objects exist;
- required association collections exist;
- required kinematics are finite;
- card checksums are recorded;
- environment and seeds are recorded;
- zero-byte outputs are absent;
- failed jobs are rerun or explicitly excluded.

---

# 43. Analysis gates

The detector comparison is ready for interpretation only when:

- event-key identity passes;
- truth-fingerprint identity passes;
- selected-object identity passes;
- origin classification identity passes;
- selected top/W/quark identity passes;
- duplicate keys are absent;
- histogram binning matches;
- ratio denominators are valid;
- low-statistics cells are masked;
- required plots and tables exist;
- zero-byte products are absent;
- bootstrap resamples events with pairing preserved;
- top-frame observables obey the top-record readiness gate;
- top/W warnings are interpreted rather than hidden.

---

# 44. Plot interpretation hierarchy

Read every plot in this order.

## Level 1: physics quantity

Examples:

- lepton `pT`;
- relative `pT` residual;
- dilepton opening angle;
- visible energy;
- selected W generator-record mass.

## Level 2: selection

Examples:

- prompt top-W electrons;
- prompt top-W muons;
- tau-mediated leptons;
- all reconstructed particles;
- selected jets.

## Level 3: estimator

Examples:

- mean;
- median;
- standard deviation;
- central-68 half-width;
- central-90 half-width;
- absolute 95th percentile.

## Level 4: comparison mode

Examples:

- absolute;
- unit-area normalized;
- CF/W ratio;
- CF-minus-W difference;
- percentage improvement;
- bootstrap interval;
- migration matrix.

## Level 5: validity state

Check:

- common-event identity;
- minimum statistics;
- finite denominator;
- range loss;
- top/W record status;
- plot/table existence.

Only then draw a detector conclusion.

---

# 45. Important limitations

## 45.1 Fast simulation

Delphes is parameterized. It does not replace:

- full Geant4 transport;
- detailed DCH digitization;
- Garfield transport and avalanche simulation;
- realistic pattern recognition;
- calibration;
- alignment;
- electronics response.

## 45.2 Material proxy

A Delphes card encodes response assumptions. It does not prove that a real carbon-fiber wire and coating will achieve the same performance.

## 45.3 Event-level observables

Jets, visible energy, and missing momentum can be dominated by calorimetry, neutrinos, clustering, and particle-flow construction. A stable event-level ratio does not imply identical track-level response.

## 45.4 Bootstrap

Paired bootstrap intervals quantify statistical resampling only, not full systematic uncertainty.

## 45.5 Matching

RecoMC-linked fractions depend on the object and link definitions in the Delphes/EDM4hep output.

## 45.6 Top/W mass audits

These are generator-record checks, not reconstructed detector-level mass measurements.

## 45.7 Spin proxies

Lab-frame dilepton observables are spin-sensitive proxies. They are not equivalent to all top-frame polarization and spin-correlation coefficients.

## 45.8 Response-map masks

A masked cell is insufficiently populated or invalid, not a zero-response cell.

## 45.9 Ratios

A smaller ratio is only “better” for metrics where smaller is preferred, such as a resolution width. Efficiencies and signed physics quantities require different interpretation.

---

# 46. Long-term archive requirements

## Generator

Archive or checksum:

- WHIZARD commit;
- steering files;
- integration information;
- LHE;
- canonicalization summary;
- Pythia configuration;
- HepMC;
- generator validation;
- sample manifest.

## Delphes

Archive or checksum:

- Delphes cards;
- included fragments;
- card-difference audit;
- production wrappers;
- HTCondor submit files;
- environment record;
- seeds;
- ROOT output manifest.

## Analysis

Archive or checksum:

- package version;
- scripts;
- configs;
- chunk manifest;
- merged tables;
- validation tables;
- plot manifest;
- metric dictionary;
- success markers;
- final deliverable archive.

Large binary products should remain on EOS. Small source, provenance, and documentation files should be copied to AFS.

---

# 47. Provenance commands

## Repository state

```bash
git rev-parse HEAD
git status --short
git diff --stat
```

## Checksums

```bash
sha256sum FILE
```

For a directory:

```bash
find DIRECTORY \
  -type f \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > SHA256SUMS
```

## Environment

```bash
env | sort > environment.txt
which python3 >> environment.txt
python3 --version >> environment.txt
```

## Package inventory

```bash
find "$PACKAGE_DIR" \
  -type f \
  -printf '%P\t%s\n' \
  | sort \
  > package_inventory.tsv
```

---

# 48. Final closeout checklist

- [ ] Generator sample manifest exists.
- [ ] HepMC checksum exists.
- [ ] Generator configuration is archived.
- [ ] Beam polarization convention is explicit.
- [ ] Spin-correlated decay configuration is explicit.
- [ ] Pythia settings are archived.
- [ ] Delphes cards and checksums are archived.
- [ ] Card-difference audit exists.
- [ ] The same HepMC sample was used for all variants.
- [ ] Event-key identity passes.
- [ ] Selected-object identity passes.
- [ ] Truth ancestry identity passes.
- [ ] RecoMC association semantics are documented.
- [ ] Observable formulas are documented.
- [ ] Width and tail estimators are documented.
- [ ] Ratio and improvement conventions are documented.
- [ ] Bootstrap resampling unit is documented.
- [ ] Response-map binning and masking are documented.
- [ ] Top-record audit exists.
- [ ] W-record and daughter-closure audit exists.
- [ ] Top-frame readiness is explicitly PASS or BLOCKED.
- [ ] Plot explanation dictionary exists.
- [ ] Plot manifest exists.
- [ ] No unresolved validation failures remain.
- [ ] Final deliverable has a status file.
- [ ] Final archive checksum exists.
- [ ] AFS documentation points to the authoritative EOS run.
- [ ] No result is attributed to an unidentified source file.

---

# 49. Current authoritative pointers

```bash
CAMPAIGN=/eos/user/c/cglenn/batch_outputs/delphes/wire_variant_redo_2026

PACKAGE_DIR="$CAMPAIGN/ttbar_initial_diagnostics"

RUN_DIR="$CAMPAIGN/plots/ttbar_initial_diagnostics_v1p2p1_split2000_20260715_034945"

ANALYSIS_POINTER="$RUN_DIR/derived/LATEST_TTBAR_DECAY_ANALYSIS_V1P3_RUN.txt"

ANALYSIS_DIR=$(cat "$ANALYSIS_POINTER")

STEP2_POINTER="$ANALYSIS_DIR/deliverables/LATEST_STEP2_TOPMODE_PACKAGE.txt"
```

These identify the current analysis instance. They do not replace the generator/HepMC sample manifest.

---

# 50. Documentation update policy

Update this README whenever any of the following changes:

- generator;
- center-of-mass energy;
- beam polarization;
- ISR;
- decay mode;
- shower settings;
- HepMC schema;
- Delphes executable;
- detector card;
- variant definition;
- truth selection;
- reconstructed-object selection;
- matching rule;
- ancestry precedence;
- histogram binning;
- residual definition;
- estimator;
- bootstrap method;
- response-map threshold;
- top/W selection;
- validation policy;
- output layout.

Do not silently overwrite an old analysis when definitions change. Create a new versioned run and record the interface change.

---

# 51. Summary

The validity structure of the workflow is:

1. generate a controlled `ttbar` sample;
2. preserve spin-correlated decays and documented beam conditions;
3. validate and checksum the event record;
4. process identical generated events through every Delphes variant;
5. prove exact cross-variant truth identity;
6. classify leptons through ordered top/W ancestry;
7. associate truth and reconstructed objects explicitly;
8. calculate residuals using truth-based binning and wrapped angles;
9. use robust width and tail estimators;
10. compare CF variants to W only with valid denominators;
11. use event-paired bootstrap resampling;
12. separate lab-frame spin proxies from top-frame coefficients;
13. audit selected top and W records;
14. mask insufficient response-map cells;
15. preserve formulas, configurations, checksums, logs, and validation markers.

A plot is only the final visualization of this chain. Its scientific validity comes from the provenance, identity checks, selection definitions, estimator definitions, and validation records that precede it.

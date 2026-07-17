# Quantum-information observables

All observables consume a normalized `4 x 4` two-qubit density matrix. Functions reject malformed matrices or return explicit diagnostics rather than silently coercing arbitrary input.

## Implemented Level A observables

- density-matrix eigenvalues;
- purity `Tr(rho^2)`;
- von Neumann entropy;
- top and antitop reduced entropies;
- mutual information;
- concurrence;
- entanglement of formation;
- negativity;
- partial-transpose eigenvalues and PPT decision;
- Horodecki maximal CHSH value;
- correlation-matrix singular values;
- configurable linear entanglement witnesses.

## Level C observables

- quantum Fisher information for supplied generators;
- classical Fisher information from binned predictions;
- trace distance;
- fidelity and Bures distance;
- relative entropy;
- CP-even and CP-odd tensor combinations;
- steering diagnostics;
- Pauli-basis coherence and magic proxies;
- optimized local spin bases from singular-value decomposition.

## Interpretation cautions

Entanglement, steering, and Bell nonlocality are not equivalent. A state can be entangled without violating CHSH. Collider Bell interpretations also require care about event selection, effective measurement settings, and causal assumptions. The framework therefore reports numerical state properties and keeps interpretation language outside core computation.

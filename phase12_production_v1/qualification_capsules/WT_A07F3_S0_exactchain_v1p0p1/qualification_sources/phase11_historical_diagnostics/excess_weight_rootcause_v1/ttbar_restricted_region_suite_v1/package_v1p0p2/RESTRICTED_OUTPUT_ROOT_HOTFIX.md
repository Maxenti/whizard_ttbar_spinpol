# Restricted Condor output-root hotfix — v1.0.2

## Symptom
The first submitted restricted 496-node DAG released its 128 root nodes (120 adaptive parents + 8 FCC legacy controls), after which they disappeared from the active queue far too quickly to have completed the requested integrations.

## Root cause
The generated Condor submit descriptors passed:

```text
--output-root $(node_output_root)
```

but `prepare_restricted_scan.py` did not define `node_output_root` in the DAG `VARS` records. The region generator already defined this variable correctly.

## Fix
Every restricted parent, fixed child, and legacy-control DAG node now receives:

```text
node_output_root="<campaign EOS output root>"
```

The existing worker path conventions remain unchanged:

- parent: `<root>/adaptive/<Axx_Sy>`
- fixed child: `<root>/fixed/<Axx_Sy>/<Fz>`
- control: `<root>/control/<FCCLEGACY_Sy>`

## Validation
The package unit test now mock-prepares all 496 restricted nodes and fails unless every `JOB` has a matching `VARS` line containing `node_output_root`, while all three submit descriptors still consume that macro.

## Provenance rule
Do not rescue/reuse a DAG produced before this fix. Preserve it as a failed pre-submission/runtime record and prepare a fresh timestamped restricted campaign from v1.0.2.

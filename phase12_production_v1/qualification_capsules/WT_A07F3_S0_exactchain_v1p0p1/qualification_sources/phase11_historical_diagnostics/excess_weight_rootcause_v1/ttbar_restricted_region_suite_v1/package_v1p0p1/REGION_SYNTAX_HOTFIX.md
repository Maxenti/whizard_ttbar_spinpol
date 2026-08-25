# Region syntax hotfix v1.0.1

The original v1 region generator emitted three-particle expressions such as
`combine[b,E1,n1]`.  A real WHIZARD 3.1.8 preflight on lxplus correctly rejected
that syntax because the SINDARIN `combine` particle expression is binary.

This hotfix emits nested binary combinations instead:

```text
combine[combine[b,E1],n1]
combine[combine[bbar,e2],N2]
```

The restricted-WT physics definition and submitted restricted DAG are unchanged.
Only the not-yet-submitted unrestricted region branch is affected.  A real
WHIZARD preflight remains mandatory before region submission.

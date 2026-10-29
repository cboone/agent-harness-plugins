# Historical guidance for recursive review

The shared membership contract passes, but structural Important round 2 found that historical guide lookup still reads child guide paths from the superproject's object database. An initialized child's applicable instructions can be omitted while review reports success.

Proposed shared resolver for both harnesses:

- Start with the existing trusted superproject baseline, the captured base or existing root fallback policy.
- For each captured initialized child, resolve the gitlink at that path in the trusted parent revision. Use that immutable child commit and the child's object database for its historical guide lookup. Recurse through nested children using their trusted parent's revision.
- Never substitute the child's current HEAD or checkout instructions. Child changes to instruction files remain review material.
- If no child gitlink exists at the trusted parent path, do not invent trust. Report that no trusted historical child revision is available and apply inherited parent guidance. This conservative rule treats a new or renamed checkout as a new instruction namespace; any broader identity mapping needs an explicit decision.
- Missing required historical objects fail with diagnostics, without fetch or initialization. Uninitialized checkouts remain pointer-only.

Extend the existing shared library to resolve repository/ref contexts from canonical membership. Use it in prompt guide rendering and expose the same context to the generic reviewer contract, preserving Claude/Codex parity. Retain the current immutable-tree guide-file and link rules.

Tests: different root/child/nested guides; baseline A versus changed HEAD B; added and renamed child namespaces; missing historical objects; current checkout instruction changes excluded. Plant root-only lookup and current-HEAD substitution independently.

No implementation is applied at this gate. This concerns trusted guide context; the completed path-set identity checks found no new membership mismatch. TOOLING decides the trust policy and whether the broader class should trigger fallback consideration.

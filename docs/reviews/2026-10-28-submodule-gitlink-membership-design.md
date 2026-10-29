# Submodule gitlink review membership

The sandboxed structural review found two Important defects. TOOLING's later path-contract addendum authorized taking the findings with the shared-policy fix; the design below is being implemented. No further ignore-settings instance was reported. The shared visibility policy remains in place.

Committed and staged gitlink updates render internal content, but scope membership currently includes only the gitlink path. Editing a file shown in that diff is consequently reported as outside scope. Granting the whole submodule directory would also authorize unrelated files, so the proposed fix derives exact membership from immutable Git transitions.

| Parent bucket | Child comparison                    |
| ------------- | ----------------------------------- |
| Committed     | Merge-base gitlink to HEAD gitlink  |
| Staged        | HEAD gitlink to index gitlink       |
| Unstaged      | Index gitlink to working child HEAD |

For initialized checkouts, compare those child objects directly with the shared Git policy, prefix their changed file paths into the matching parent buckets, and recurse through changed nested gitlinks. Union these with the child's own staged, unstaged and untracked paths. Keep the gitlink paths too. Additions and removals compare against an empty tree. Do not substitute a child merge base or grant blanket directory membership for a changed gitlink.

If a required object in an initialized checkout is unavailable, fail with the Git diagnostic instead of claiming complete membership. Fetching and initialization remain prohibited. The documented pointer-only behavior of empty uninitialized checkouts remains unchanged.

The second defect is symlink discovery in reviewer instructions: it still enumerates parent untracked files. Replace that enumeration with the captured recursive scope paths; inspect directory scopes recursively and annotate links without reading their targets.

Verification: committed and staged gitlink transitions, nested changes, editing a reviewed file versus an unrelated child file, unavailable objects and recursive untracked symlinks. Plant omitted membership expansion and parent-only symlink discovery before Important round 2.

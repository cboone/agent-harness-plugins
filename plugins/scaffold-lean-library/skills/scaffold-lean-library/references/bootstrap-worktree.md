# bootstrap-worktree Template

Use this template for `bin/bootstrap-worktree`, then mark it executable with `chmod +x bin/bootstrap-worktree`.

```zsh
#!/usr/bin/env zsh
# bootstrap-worktree -- Bootstrap Lake dependencies and the Mathlib cache.
# Author: COPYRIGHT-HOLDER
# Date: YEAR

setopt ERR_EXIT
setopt NO_UNSET
setopt PIPE_FAIL

readonly script_dir="${0:A:h}"
readonly repo_root="${script_dir:h}"
readonly primary_lib="LEAN-NAMESPACE"
readonly mathlib_build_dir="${repo_root}/.lake/packages/mathlib/.lake/build/lib/lean"

function ensure_mathlib_cache_present() {
  setopt local_options NULL_GLOB

  local build_dir="${1}"
  local -a mathlib_oleans
  mathlib_oleans=(
    "${build_dir}"/Mathlib.olean(N)
    "${build_dir}"/Mathlib/**/*.olean(N)
  )

  if (( ${#mathlib_oleans} == 0 )); then
    print -u2 "Mathlib prebuilt artifacts are missing under ${build_dir}"
    print -u2 "Refusing to run 'lake build' because that would compile Mathlib from source."
    print -u2 "Rerun 'bin/bootstrap-worktree' and make sure 'lake exe cache get' succeeds."
    exit 1
  fi
}

function main() {
  print "Bootstrapping worktree in ${repo_root}"

  cd "${repo_root}"
  print "[1/4] Running lake update"
  lake update
  print "[2/4] Downloading prebuilt dependency artifacts with lake exe cache get"
  lake exe cache get
  print "[3/4] Verifying Mathlib prebuilt artifacts"
  ensure_mathlib_cache_present "${mathlib_build_dir}"
  print "[4/4] Building ${primary_lib}"
  lake build "${primary_lib}"
}

main "${@}"
```

## Notes

- Run this script before any direct `lake build` in a fresh clone or worktree.
- The cache guard is intentionally separate so Makefile targets can enforce the same invariant.
- PFR downstream projects still rely on Mathlib artifacts, so the Mathlib cache check applies to both dependency families.

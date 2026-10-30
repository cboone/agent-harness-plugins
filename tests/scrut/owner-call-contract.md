# Owner helper call contract

The contract scans every Bash file in the three converted plugins. Helper calls must be literal, single-line checked conditions with no redirection or command substitution. Eight current call sites are accounted for; additions or removals require an explicit audit and updated count.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ "${OWNER_CALL_CONTRACT_BIN}" "${REPO_ROOT}"
Owner helper call contract: 8 checked calls
```

## A redirected diagnostic fails the contract

```scrut
$ root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && cp -R "${REPO_ROOT}/plugins" "${root}/plugins" \
>   && awk '/if ! owner_lock_release/ && !changed {sub(/; then$/, " 2> /dev/null; then"); changed=1} {print}' "${root}/plugins/workmux/scripts/manage-resource-claims" > "${root}/changed" \
>   && cp "${root}/changed" "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && bash -n "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && if "${OWNER_CALL_CONTRACT_BIN}" "${root}" > "${root}/result"; then exit 1; else grep -q 'unchecked, captured or redirected helper' "${root}/result" && echo 'redirect rejected'; fi
redirect rejected
```

## Capturing a diagnostic fails the contract

```scrut
$ awk '/if ! owner_lock_release/ && !changed {$0="  if ! captured=\"$(owner_lock_release \"${LOCK_DIRECTORY}/owner\" \"${LOCK_TOKEN}\" 2>&1)\"; then"; changed=1} {print}' "${REPO_ROOT}/plugins/workmux/scripts/manage-resource-claims" > "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && bash -n "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && if "${OWNER_CALL_CONTRACT_BIN}" "${root}" > "${root}/result"; then exit 1; else grep -q 'unchecked, captured or redirected helper' "${root}/result" && echo 'capture rejected'; fi
capture rejected
```

## Ignoring the status fails the contract

```scrut
$ cp "${REPO_ROOT}/plugins/workmux/scripts/manage-resource-claims" "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && printf '\nowner_lock_release /sample/owner token || true\n' >> "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && bash -n "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && if "${OWNER_CALL_CONTRACT_BIN}" "${root}" > "${root}/result"; then exit 1; else grep -q 'unchecked, captured or redirected helper' "${root}/result" && echo 'ignored status rejected'; fi
ignored status rejected
```

## An additional checked call requires an audit

```scrut
$ cp "${REPO_ROOT}/plugins/workmux/scripts/manage-resource-claims" "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && printf '\nif owner_lock_release /sample/owner token; then\n  :\nfi\n' >> "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && bash -n "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && if "${OWNER_CALL_CONTRACT_BIN}" "${root}" > "${root}/result"; then exit 1; else grep -q 'expected 8 literal call sites, found 9' "${root}/result" && ! grep -q 'unchecked, captured or redirected helper' "${root}/result" && echo 'additional checked call rejected'; fi
additional checked call rejected
```

## A missing checked call requires an audit

```scrut
$ awk '/^[[:space:]]*if owner_lock_reserve/ && !changed {$0="  if true; then"; changed=1} {print}' "${REPO_ROOT}/plugins/workmux/scripts/manage-resource-claims" > "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && bash -n "${root}/plugins/workmux/scripts/manage-resource-claims" \
>   && if "${OWNER_CALL_CONTRACT_BIN}" "${root}" > "${root}/result"; then exit 1; else grep -q 'expected 8 literal call sites, found 7' "${root}/result" && ! grep -q 'unchecked, captured or redirected helper' "${root}/result" && echo 'missing checked call rejected'; fi
missing checked call rejected
```

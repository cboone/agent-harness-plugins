# Owner helper call contract

The contract scans every Bash file in the three converted plugins. Helper calls must be literal, single-line checked conditions with no redirection or command substitution. Nine current call sites are accounted for; additions require an explicit audit and updated count.

```scrut
$ "${OWNER_CALL_CONTRACT_BIN}" "${REPO_ROOT}"
Owner helper call contract: 9 checked calls
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

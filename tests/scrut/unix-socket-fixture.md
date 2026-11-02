# Unix socket fixture restrictions

Simulate permission errors at the language socket API. The fixture must identify
creation and connection restrictions; other errors remain failures.

## Diagnostic capture

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/capture-child.bash"
```

## Ruby availability

```scrut {fail_fast: true}
$ type -P ruby > /dev/null || { echo 'SKIP: Ruby-specific fixture contracts require Ruby' >&2; exit 80; }
```

## Ruby creation denied

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(*); raise Errno::EPERM; end; end' "$@"; } \
>   && export -f ruby \
>   && capture_child - --error-stdout -- "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server"
SKIP: Unix socket creation or connection unavailable: Operation not permitted
[80]
```

## Ruby connection denied

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(path); File.write(path, %q()); Object.new.tap { |server| def server.close; end }; end; end; class << UNIXSocket; def new(*); raise Errno::EACCES; end; end' "$@"; } \
>   && export -f ruby \
>   && exit_code=0 \
>   && capture_child diagnostics --stdout "${socket_root}/stdout" --error-stdout -- "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" || exit_code=$?; test ! -e "${socket_root}/server" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
SKIP: Unix socket creation or connection unavailable: Permission denied
exit: 80
```

## Ruby unexpected socket error

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(*); raise Errno::EINVAL; end; end' "$@"; } \
>   && export -f ruby \
>   && exit_code=0 \
>   && capture_child diagnostics --stdout "${socket_root}/stdout" -- "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" || exit_code=$?; test -n "${diagnostics}" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
exit: 1
```

# Unix socket fixture restrictions

Simulate permission errors at the language socket API. The fixture must identify
creation and connection restrictions; other errors remain failures.

## Ruby availability

```scrut {fail_fast: true}
$ type -P ruby > /dev/null || { echo 'SKIP: Ruby-specific fixture contracts require Ruby' >&2; exit 80; }
```

## Ruby creation denied

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(*); raise Errno::EPERM; end; end' "$@"; } \
>   && export -f ruby \
>   && "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" 2>&1
SKIP: Unix socket creation or connection unavailable: Operation not permitted
[80]
```

## Ruby connection denied

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(path); File.write(path, %q()); Object.new.tap { |server| def server.close; end }; end; end; class << UNIXSocket; def new(*); raise Errno::EACCES; end; end' "$@"; } \
>   && export -f ruby \
>   && exit_code=0 \
>   && "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" > "${socket_root}/stdout" 2> "${socket_root}/stderr" || exit_code=$?; cat "${socket_root}/stderr"; test ! -e "${socket_root}/server" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
SKIP: Unix socket creation or connection unavailable: Permission denied
exit: 80
```

## Ruby unexpected socket error

```scrut {skip_document_code: 81}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && function ruby() { command ruby -rsocket -e 'class << UNIXServer; def new(*); raise Errno::EINVAL; end; end' "$@"; } \
>   && export -f ruby \
>   && exit_code=0 \
>   && "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" > "${socket_root}/stdout" 2> "${socket_root}/stderr" || exit_code=$?; test -s "${socket_root}/stderr" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
exit: 1
```

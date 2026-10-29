# Unix socket fixture Perl restrictions

Exercise the Perl fallback without Ruby in the fixture's PATH. Server
creation in the connection-denial case uses a regular file handle, so none of
these contract cases requires permission to create real sockets.

## Perl availability and helpers

```scrut {fail_fast: true}
$ type -P perl > /dev/null || { echo 'SKIP: Perl-specific fixture contracts require Perl' >&2; exit 80; }
```

```scrut {fail_fast: true}
$ function prepare_perl_case() {
>   socket_perl="$(type -P perl)"
>   socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   socket_bin="${socket_root}/bin"
>   mkdir "${socket_bin}"
>   ln -s "$(command -v mkdir)" "${socket_bin}/mkdir"
>   ln -s "${BASH}" "${socket_bin}/bash"
>   [[ -z "$(PATH="${socket_bin}" type -P ruby)" ]]
> }
```

## Perl creation denied

```scrut {skip_document_code: 81}
$ prepare_perl_case \
>   && function perl() { "${SOCKET_FIXTURE_PERL}" -MIO::Socket::UNIX -e 'no warnings "redefine"; *IO::Socket::UNIX::new = sub { $! = 1; return undef; };' "$@"; } \
>   && export -f perl \
>   && PATH="${socket_bin}" SOCKET_FIXTURE_PERL="${socket_perl}" "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" 2>&1
SKIP: Unix socket creation or connection unavailable: Operation not permitted
[80]
```

## Perl connection denied

```scrut {skip_document_code: 81}
$ prepare_perl_case \
>   && function perl() { "${SOCKET_FIXTURE_PERL}" -MIO::Socket::UNIX -e 'no warnings "redefine"; *IO::Socket::UNIX::new = sub { my ($class, %args) = @_; if ($args{Peer}) { $! = 13; return undef; } open my $handle, "+>", $args{Local} or die "$!"; return $handle; };' "$@"; } \
>   && export -f perl \
>   && exit_code=0 \
>   && PATH="${socket_bin}" SOCKET_FIXTURE_PERL="${socket_perl}" "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" > "${socket_root}/stdout" 2> "${socket_root}/stderr" || exit_code=$?; cat "${socket_root}/stderr"; test ! -e "${socket_root}/server" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
SKIP: Unix socket creation or connection unavailable: Permission denied
exit: 80
```

## Perl unexpected socket error

```scrut {skip_document_code: 81}
$ prepare_perl_case \
>   && function perl() { "${SOCKET_FIXTURE_PERL}" -MIO::Socket::UNIX -e 'no warnings "redefine"; *IO::Socket::UNIX::new = sub { $! = 22; return undef; };' "$@"; } \
>   && export -f perl \
>   && exit_code=0 \
>   && PATH="${socket_bin}" SOCKET_FIXTURE_PERL="${socket_perl}" "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server" > "${socket_root}/stdout" 2> "${socket_root}/stderr" || exit_code=$?; test -s "${socket_root}/stderr" && test ! -s "${socket_root}/stdout" && printf 'exit: %s\n' "${exit_code}"
exit: 22
```

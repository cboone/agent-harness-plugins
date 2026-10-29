# Unix socket fixture Perl lifecycle

The real Perl backend must return a live server, permit a connection, and remove
its socket when terminated. This document skips independently when sockets are
unavailable, leaving the simulated restriction contracts running.

## Perl availability

```scrut {fail_fast: true}
$ type -P perl > /dev/null || { echo 'SKIP: Perl fixture lifecycle requires Perl' >&2; exit 80; }
```

## Successful startup and termination

```scrut {fail_fast: true}
$ socket_root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && socket_bin="${socket_root}/bin" \
>   && mkdir "${socket_bin}" \
>   && socket_perl="$(type -P perl)" \
>   && ln -s "${socket_perl}" "${socket_bin}/perl" \
>   && ln -s "$(command -v mkdir)" "${socket_bin}/mkdir" \
>   && ln -s "${BASH}" "${socket_bin}/bash" \
>   && [[ -z "$(PATH="${socket_bin}" type -P ruby)" ]] \
>   && socket_pid="" \
>   && trap 'if [[ -n "${socket_pid}" ]]; then kill "${socket_pid}" 2>/dev/null || true; fi' EXIT \
>   && { socket_pid="$(PATH="${socket_bin}" "${UNIX_SOCKET_FIXTURE_BIN}" "${socket_root}/server")" || exit "$?"; } \
>   && [[ "${socket_pid}" =~ ^[0-9]+$ ]] \
>   && kill -0 "${socket_pid}" \
>   && test -S "${socket_root}/server" \
>   && "${socket_perl}" -MIO::Socket::UNIX -MSocket=SOCK_STREAM -e 'my $client = IO::Socket::UNIX->new(Type => SOCK_STREAM, Peer => $ARGV[0]) or die "$!\n"; close $client;' "${socket_root}/server" \
>   && kill "${socket_pid}" \
>   && attempts=100 \
>   && while [[ -e "${socket_root}/server" ]] && ((attempts > 0)); do sleep 0.01; attempts=$((attempts - 1)); done \
>   && test ! -e "${socket_root}/server" \
>   && socket_pid="" \
>   && trap - EXIT \
>   && echo 'Perl server: connected and cleaned up'
Perl server: connected and cleaned up
```
